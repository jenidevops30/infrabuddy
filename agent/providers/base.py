"""
Base Model Provider Interface

Defines the abstract interface that all model providers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
from enum import Enum


class ProviderType(str, Enum):
    """Supported model provider types."""
    NVIDIA = "nvidia"
    BEDROCK = "bedrock"
    SAMPLE = "sample"


@dataclass(frozen=True)
class ModelResponse:
    """Structured response from a model provider."""
    content: str
    model: str
    provider: ProviderType
    usage: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None


class ModelError(Exception):
    """Base exception for model provider errors."""
    
    def __init__(self, message: str, provider: ProviderType, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.provider = provider
        self.original_error = original_error


class ModelProvider(ABC):
    """Abstract base class for model providers."""
    
    def __init__(self, model: str, **kwargs):
        self.model = model
        self._config = kwargs
    
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type identifier."""
        pass
    
    @abstractmethod
    async def analyze(self, prompt: str, system_prompt: Optional[str] = None) -> ModelResponse:
        """
        Send a prompt to the model and return a structured response.
        
        Args:
            prompt: The user prompt to analyze
            system_prompt: Optional system prompt for context
            
        Returns:
            ModelResponse with content and metadata
            
        Raises:
            ModelError: If the provider fails to generate a response
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is available and healthy.
        
        Returns:
            True if provider is healthy, False otherwise
        """
        pass
    
    def get_config_summary(self) -> dict[str, Any]:
        """Return a sanitized config summary for logging (no secrets)."""
        return {
            "provider": self.provider_type.value,
            "model": self.model,
        }