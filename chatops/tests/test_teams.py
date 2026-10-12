"""
Tests for Teams bot module.
"""

from unittest.mock import AsyncMock, patch
import pytest
from chatops.teams.bot import InfraBuddyTeamsBot
from chatops.core import AnalysisResult


class DummyActivity:
    def __init__(self, text=""):
        self.text = text


class DummyTurnContext:
    def __init__(self, text=""):
        self.activity = DummyActivity(text)
        self.send_activity = AsyncMock()


@pytest.mark.asyncio
async def test_teams_bot_help():
    bot = InfraBuddyTeamsBot()
    context = DummyTurnContext(text="help")

    await bot.on_message_activity(context)

    context.send_activity.assert_called_once()
    msg = context.send_activity.call_args[0][0]
    assert "InfraBuddy Teams Commands" in msg


@pytest.mark.asyncio
async def test_teams_bot_analyze():
    bot = InfraBuddyTeamsBot()
    context = DummyTurnContext(text="analyze ec2")

    mock_result = AnalysisResult(
        success=True,
        region="us-east-1",
        service_filter="ec2",
        analysis="EC2 healthy",
        provider="sample",
        model="sample-model",
    )

    with patch("chatops.teams.bot.run_analysis", return_value=mock_result):
        await bot.on_message_activity(context)

    assert context.send_activity.call_count == 2
