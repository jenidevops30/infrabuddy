"""
Tests for Slack bot module.
"""

from unittest.mock import AsyncMock, patch
import pytest
from chatops.slack.bot import create_slack_app, _async_analyze_and_respond
from chatops.core import AnalysisResult


@pytest.mark.asyncio
async def test_async_analyze_and_respond():
    mock_respond = AsyncMock()
    mock_result = AnalysisResult(
        success=True,
        region="us-east-1",
        service_filter="ec2",
        analysis="Diagnostic summary.",
        provider="sample",
        model="sample-model",
    )

    with patch("chatops.slack.bot.run_analysis", return_value=mock_result):
        await _async_analyze_and_respond(mock_respond, "ec2")

    mock_respond.assert_called_once()
    _, kwargs = mock_respond.call_args
    assert "blocks" in kwargs
    assert kwargs["replace_original"] is False


def test_create_slack_app_no_token(monkeypatch):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "")
    from agent.config import get_settings
    get_settings.cache_clear()
    app = create_slack_app()
    assert app is None
