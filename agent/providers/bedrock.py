"""
AWS Bedrock Model Provider

Integrates AWS Bedrock using the unified Converse API, supporting
Amazon Nova (nova-pro, nova-lite), Claude 3/3.5, and Llama models.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

from agent.providers.base import ModelError, ModelProvider, ModelResponse, ProviderType

logger = logging.getLogger(__name__)


class BedrockProvider(ModelProvider):
    """
    Model provider for AWS Bedrock.
    
    Uses boto3 bedrock-runtime converse API for multi-turn structured conversations,
    system prompts, and consistent token usage accounting.
    """

    def __init__(
        self,
        model: str = "amazon.nova-pro-v1:0",
        region: Optional[str] = None,
        profile: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs,
    ):
        super().__init__(model=model, **kwargs)
        self.region = region
        self.profile = profile
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None

    def _get_client(self):
        """Lazily initialize boto3 bedrock-runtime client."""
        if self._client is None:
            session_kwargs: dict[str, Any] = {}
            if self.profile:
                session_kwargs["profile_name"] = self.profile
            
            session = boto3.Session(**session_kwargs)
            client_kwargs: dict[str, Any] = {}
            if self.region:
                client_kwargs["region_name"] = self.region
                
            self._client = session.client("bedrock-runtime", **client_kwargs)
        return self._client

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.BEDROCK

    async def analyze(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> ModelResponse:
        """Send prompt to AWS Bedrock Converse API asynchronously."""
        try:
            return await asyncio.to_thread(self._invoke_converse, prompt, system_prompt)
        except Exception as e:
            logger.error("Bedrock analyze failed: %s", e)
            raise ModelError(
                f"AWS Bedrock invocation failed: {e}",
                provider=self.provider_type,
                original_error=e,
            ) from e

    def _invoke_converse(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> ModelResponse:
        """Synchronous wrapper executing converse via boto3 in a threadpool."""
        client = self._get_client()

        messages = [
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ]

        kwargs: dict[str, Any] = {
            "modelId": self.model,
            "messages": messages,
            "inferenceConfig": {
                "temperature": self.temperature,
                "maxTokens": self.max_tokens,
            },
        }

        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]

        try:
            response = client.converse(**kwargs)
            output_message = response.get("output", {}).get("message", {})
            content_list = output_message.get("content", [])

            # Join all text chunks
            text_chunks = [c.get("text", "") for c in content_list if "text" in c]
            content = "".join(text_chunks)

            usage = response.get("usage", {})
            metrics = response.get("metrics", {})

            return ModelResponse(
                content=content,
                model=self.model,
                provider=self.provider_type,
                usage=usage,
                metadata={
                    "stop_reason": response.get("stopReason"),
                    "latency_ms": metrics.get("latencyMs"),
                    "region": self.region,
                },
            )
        except ClientError as ce:
            error_code = ce.response.get("Error", {}).get("Code", "Unknown")
            error_msg = ce.response.get("Error", {}).get("Message", str(ce))
            raise RuntimeError(f"Bedrock ClientError [{error_code}]: {error_msg}") from ce
        except Exception as ex:
            raise RuntimeError(f"Unexpected Bedrock error: {ex}") from ex

    async def health_check(self) -> bool:
        """Check if AWS Bedrock credentials and model access work."""
        try:
            test_response = await self.analyze(
                prompt="Respond with 'healthy'",
                system_prompt="You are a health check system.",
            )
            return bool(test_response.content)
        except Exception as e:
            logger.warning("Bedrock health check failed: %s", e)
            return False

    def get_config_summary(self) -> dict[str, Any]:
        return {
            "provider": self.provider_type.value,
            "model": self.model,
            "region": self.region,
        }
