"""
Tests for AWS Bedrock provider (Amazon Nova / Converse API).
"""

from unittest.mock import MagicMock, patch
import pytest

from agent.providers.base import ModelError, ProviderType
from agent.providers.bedrock import BedrockProvider
from agent.providers.factory import create_provider


def test_bedrock_provider_init():
    provider = BedrockProvider(
        model="amazon.nova-pro-v1:0",
        region="us-east-1",
    )
    assert provider.provider_type == ProviderType.BEDROCK
    assert provider.model == "amazon.nova-pro-v1:0"
    assert provider.region == "us-east-1"


@pytest.mark.asyncio
async def test_bedrock_analyze_success():
    provider = BedrockProvider(model="amazon.nova-pro-v1:0", region="us-east-1")

    mock_converse_response = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"text": "EC2 and RDS instances are functioning normally."}],
            }
        },
        "stopReason": "end_turn",
        "usage": {
            "inputTokens": 120,
            "outputTokens": 45,
            "totalTokens": 165,
        },
        "metrics": {"latencyMs": 350},
    }

    mock_boto_client = MagicMock()
    mock_boto_client.converse.return_value = mock_converse_response

    with patch.object(provider, "_get_client", return_value=mock_boto_client):
        response = await provider.analyze(
            prompt="Analyze infrastructure",
            system_prompt="You are an AWS expert",
        )

    assert response.content == "EC2 and RDS instances are functioning normally."
    assert response.provider == ProviderType.BEDROCK
    assert response.model == "amazon.nova-pro-v1:0"
    assert response.usage["totalTokens"] == 165
    assert response.metadata["stop_reason"] == "end_turn"

    mock_boto_client.converse.assert_called_once()
    _, kwargs = mock_boto_client.converse.call_args
    assert kwargs["modelId"] == "amazon.nova-pro-v1:0"
    assert kwargs["system"] == [{"text": "You are an AWS expert"}]


@pytest.mark.asyncio
async def test_bedrock_analyze_failure():
    provider = BedrockProvider(model="amazon.nova-pro-v1:0", region="us-east-1")

    mock_boto_client = MagicMock()
    mock_boto_client.converse.side_effect = RuntimeError("AccessDeniedException")

    with patch.object(provider, "_get_client", return_value=mock_boto_client):
        with pytest.raises(ModelError) as exc_info:
            await provider.analyze(prompt="Test prompt")

    assert "AWS Bedrock invocation failed" in str(exc_info.value)
    assert exc_info.value.provider == ProviderType.BEDROCK


def test_factory_creates_bedrock_provider(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "bedrock")
    monkeypatch.setenv("MODEL_NAME", "amazon.nova-pro-v1:0")
    monkeypatch.setenv("AWS_REGION", "us-east-1")

    from agent.config import get_settings
    get_settings.cache_clear()

    provider = create_provider()
    assert isinstance(provider, BedrockProvider)
    assert provider.model == "amazon.nova-pro-v1:0"
    assert provider.region == "us-east-1"
