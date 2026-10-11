"""
LLM Interface

Provides a unified interface for model analysis using the provider abstraction.
Supports both sync (legacy CLI) and async (new API) usage patterns.
"""

import asyncio
import logging
from typing import Optional

from agent.providers.base import ModelProvider, ModelResponse, ProviderType
from agent.providers.factory import create_provider, create_provider_with_fallback
from agent.config import get_settings

logger = logging.getLogger(__name__)


class LLM:
    """
    LLM interface for infrastructure analysis.
    
    Uses the provider abstraction to support multiple model backends
    (NVIDIA Nemotron, sample mode) with automatic fallback.
    """
    
    def __init__(
        self,
        provider: Optional[ModelProvider] = None,
        provider_type: Optional[ProviderType] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize LLM with optional explicit provider.
        
        Args:
            provider: Pre-configured provider instance (for testing)
            provider_type: Explicit provider type (overrides config)
            model: Explicit model name (overrides config)
        """
        self._provider = provider
        self._provider_type = provider_type
        self._model = model
        self._initialized = False
    
    async def _ensure_provider(self) -> ModelProvider:
        """Lazy initialization of provider with fallback."""
        if self._provider is None:
            self._provider = await create_provider_with_fallback(
                provider_type=self._provider_type,
                model=self._model,
            )
            self._initialized = True
            logger.info(f"Initialized LLM with provider: {self._provider.provider_type.value}")
        return self._provider
    
    async def analyze_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> ModelResponse:
        """
        Analyze evidence asynchronously using the configured provider.
        
        Args:
            prompt: The evidence/prompt to analyze
            system_prompt: Optional system prompt for context
            
        Returns:
            Structured ModelResponse
        """
        provider = await self._ensure_provider()
        
        default_system = (
            "You are an expert AWS DevOps engineer. "
            "Analyze infrastructure evidence carefully. "
            "Do not invent information. "
            "Identify anomalies, likely causes, "
            "and recommended investigation steps. "
            "Return structured JSON only."
        )
        
        return await provider.analyze(
            prompt=prompt,
            system_prompt=system_prompt or default_system,
        )
    
    def analyze(self, evidence: str) -> str:
        """
        Synchronous analyze method for backward compatibility with CLI.
        
        Args:
            evidence: The evidence to analyze
            
        Returns:
            Analysis content as string
        """
        # Run async method in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(self.analyze_async(evidence))
        return response.content
    
    @property
    def provider_info(self) -> dict:
        """Get provider information for logging/debugging."""
        if self._provider:
            return self._provider.get_config_summary()
        return {"status": "not_initialized"}
    
    async def close(self):
        """Close provider connections if needed."""
        if self._provider and hasattr(self._provider, 'close'):
            await self._provider.close()


# Legacy function for backward compatibility
def create_llm() -> LLM:
    """Create LLM instance with default configuration."""
    return LLM()
