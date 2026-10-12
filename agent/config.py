"""
Configuration Management

Centralized configuration using Pydantic Settings with environment variable support.
"""

from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Model Provider Configuration
    model_provider: str = Field(
        default="bedrock",
        description="Model provider type: 'bedrock', 'nvidia', or 'sample'",
    )
    model_name: str = Field(
        default="amazon.nova-pro-v1:0",
        description="Model identifier (e.g. amazon.nova-pro-v1:0, amazon.nova-lite-v1:0)",
    )
    bedrock_region: Optional[str] = Field(
        default=None,
        description="AWS region for Bedrock (defaults to aws_region if not specified)",
    )
    nvidia_api_key: Optional[str] = Field(
        default=None,
        description="NVIDIA NIM API key",
    )
    nvidia_base_url: str = Field(
        default="https://integrate.api.nvidia.com/v1",
        description="NVIDIA NIM API base URL",
    )
    model_timeout: float = Field(
        default=60.0,
        description="Model API timeout in seconds",
    )
    model_max_retries: int = Field(
        default=3,
        description="Maximum retry attempts for model API",
    )
    
    # AWS Configuration
    aws_region: str = Field(
        default="us-east-1",
        description="Default AWS region",
    )
    aws_profile: Optional[str] = Field(
        default=None,
        description="AWS CLI profile name",
    )
    
    # API Server Configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host",
    )
    api_port: int = Field(
        default=8000,
        description="API server port",
    )
    api_workers: int = Field(
        default=1,
        description="Number of API workers",
    )
    
    # Security Configuration
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication (optional in dev)",
    )
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    log_format: str = Field(
        default="json",
        description="Log format: 'json' or 'text'",
    )
    
    # Feature Flags
    enable_sample_mode: bool = Field(
        default=True,
        description="Enable sample mode fallback",
    )
    enable_metrics: bool = Field(
        default=False,
        description="Enable Prometheus metrics",
    )

    # Slack ChatOps
    slack_bot_token: Optional[str] = Field(
        default=None,
        description="Slack Bot OAuth token (xoxb-...)",
    )
    slack_signing_secret: Optional[str] = Field(
        default=None,
        description="Slack signing secret for request verification",
    )
    slack_app_token: Optional[str] = Field(
        default=None,
        description="Slack App-level token for Socket Mode (xapp-...)",
    )

    # Microsoft Teams ChatOps
    microsoft_app_id: Optional[str] = Field(
        default=None,
        description="Azure Bot App ID",
    )
    microsoft_app_password: Optional[str] = Field(
        default=None,
        description="Azure Bot App password / client secret",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_settings_override(**overrides) -> Settings:
    """Get settings with runtime overrides (for testing)."""
    settings = get_settings()
    for key, value in overrides.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    return settings