"""
Model Provider Factory

Creates model provider instances based on configuration.
"""

import logging
from typing import Optional

from agent.providers.base import ModelProvider, ProviderType
from agent.providers.bedrock import BedrockProvider
from agent.providers.nvidia import NVIDIAProvider
from agent.providers.sample import SampleProvider
from agent.config import get_settings

logger = logging.getLogger(__name__)


def create_provider(
    provider_type: Optional[ProviderType] = None,
    model: Optional[str] = None,
    **kwargs
) -> ModelProvider:
    """
    Create a model provider instance based on configuration.
    
    Args:
        provider_type: Explicit provider type (overrides config)
        model: Model identifier (overrides config)
        **kwargs: Additional provider-specific arguments
        
    Returns:
        Configured ModelProvider instance
        
    Raises:
        ValueError: If provider type is unknown or required config is missing
    """
    settings = get_settings()
    
    # Determine provider type
    if provider_type is None:
        provider_type = ProviderType(settings.model_provider)
    
    # Determine model
    if model is None:
        model = settings.model_name
    
    logger.info(f"Creating provider: type={provider_type.value}, model={model}")
    
    if provider_type == ProviderType.BEDROCK:
        return _create_bedrock_provider(model, settings, **kwargs)
    elif provider_type == ProviderType.NVIDIA:
        return _create_nvidia_provider(model, settings, **kwargs)
    elif provider_type == ProviderType.SAMPLE:
        return _create_sample_provider(model, **kwargs)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")


def _create_bedrock_provider(
    model: str,
    settings,
    **kwargs
) -> BedrockProvider:
    """Create AWS Bedrock provider with settings."""
    region = settings.bedrock_region or settings.aws_region
    return BedrockProvider(
        model=model,
        region=region,
        profile=settings.aws_profile,
        **kwargs,
    )


def _create_nvidia_provider(
    model: str,
    settings,
    **kwargs
) -> NVIDIAProvider:
    """Create NVIDIA provider with settings."""
    api_key = settings.nvidia_api_key
    base_url = settings.nvidia_base_url
    
    if not api_key:
        logger.warning("NVIDIA API key not configured, falling back to sample provider")
        return _create_sample_provider(model, **kwargs)
    
    return NVIDIAProvider(
        model=model,
        api_key=api_key,
        base_url=base_url,
        timeout=settings.model_timeout,
        max_retries=settings.model_max_retries,
        **kwargs
    )


def _create_sample_provider(model: str, **kwargs) -> SampleProvider:
    """Create sample provider."""
    return SampleProvider(model=model, **kwargs)


async def create_provider_with_fallback(
    provider_type: Optional[ProviderType] = None,
    model: Optional[str] = None,
    **kwargs
) -> ModelProvider:
    """
    Create a provider with automatic fallback to sample mode.
    
    Attempts to create the requested provider, falls back to sample
    if the primary provider fails health check.
    """
    provider = create_provider(provider_type, model, **kwargs)
    
    # Health check primary provider
    if provider.provider_type != ProviderType.SAMPLE:
        try:
            healthy = await provider.health_check()
            if not healthy:
                logger.warning(f"Provider {provider.provider_type.value} health check failed, falling back to sample")
                return _create_sample_provider(model or "sample-model", **kwargs)
        except Exception as e:
            logger.warning(f"Provider {provider.provider_type.value} health check error: {e}, falling back to sample")
            return _create_sample_provider(model or "sample-model", **kwargs)
    
    return provider