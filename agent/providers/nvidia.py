"""
NVIDIA Nemotron Model Provider

Implements the ModelProvider interface for NVIDIA NIM (Nemotron) via OpenAI-compatible API.
"""

import os
import logging
from typing import Optional, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from agent.providers.base import ModelProvider, ModelResponse, ModelError, ProviderType

logger = logging.getLogger(__name__)


class NVIDIAProviderError(ModelError):
    """NVIDIA-specific provider errors."""
    pass


class NVIDIAProvider(ModelProvider):
    """NVIDIA Nemotron provider using OpenAI-compatible API."""
    
    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str = "https://integrate.api.nvidia.com/v1",
        timeout: float = 60.0,
        max_retries: int = 3,
        **kwargs
    ):
        super().__init__(model, **kwargs)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Create HTTP client with timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(self.timeout),
        )
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.NVIDIA
    
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def analyze(self, prompt: str, system_prompt: Optional[str] = None) -> ModelResponse:
        """
        Send a prompt to NVIDIA Nemotron and return structured response.
        
        Args:
            prompt: The user prompt to analyze
            system_prompt: Optional system prompt for context
            
        Returns:
            ModelResponse with content and metadata
            
        Raises:
            NVIDIAProviderError: If the API call fails
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 4096,
        }
        
        try:
            logger.debug(f"Sending request to NVIDIA API: model={self.model}, messages={len(messages)}")
            
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract content from OpenAI-compatible response
            choices = data.get("choices", [])
            if not choices:
                raise NVIDIAProviderError(
                    "No choices returned from NVIDIA API",
                    ProviderType.NVIDIA,
                )
            
            content = choices[0].get("message", {}).get("content", "")
            if not content:
                raise NVIDIAProviderError(
                    "Empty content in NVIDIA API response",
                    ProviderType.NVIDIA,
                )
            
            usage = data.get("usage")
            
            logger.debug(f"Received response from NVIDIA API: tokens={usage}")
            
            return ModelResponse(
                content=content,
                model=self.model,
                provider=ProviderType.NVIDIA,
                usage=usage,
                metadata={"finish_reason": choices[0].get("finish_reason")},
            )
            
        except httpx.TimeoutException as e:
            logger.error(f"NVIDIA API timeout: {e}")
            raise NVIDIAProviderError(
                f"Request timeout after {self.timeout}s",
                ProviderType.NVIDIA,
                original_error=e,
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"NVIDIA API HTTP error: {e.response.status_code} - {e.response.text}")
            raise NVIDIAProviderError(
                f"API error: {e.response.status_code}",
                ProviderType.NVIDIA,
                original_error=e,
            )
        except httpx.NetworkError as e:
            logger.error(f"NVIDIA API network error: {e}")
            raise NVIDIAProviderError(
                "Network error connecting to NVIDIA API",
                ProviderType.NVIDIA,
                original_error=e,
            )
        except Exception as e:
            logger.error(f"NVIDIA API unexpected error: {e}")
            raise NVIDIAProviderError(
                f"Unexpected error: {str(e)}",
                ProviderType.NVIDIA,
                original_error=e,
            )
    
    async def health_check(self) -> bool:
        """
        Check if NVIDIA API is reachable.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try a minimal request to check connectivity
            response = await self._client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1,
                },
                timeout=httpx.Timeout(10.0),
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"NVIDIA health check failed: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    def get_config_summary(self) -> dict[str, Any]:
        """Return sanitized config for logging."""
        base = super().get_config_summary()
        base.update({
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "api_key_set": bool(self.api_key),
        })
        return base