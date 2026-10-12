"""
chatops/slack/bot.py

Slack Bolt application definition and event/command handlers.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from agent.config import get_settings
from chatops.core import run_analysis, run_status
from chatops.formatter import to_slack_blocks, to_slack_error_blocks

logger = logging.getLogger(__name__)

try:
    from slack_bolt.async_app import AsyncApp
    from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
except ImportError:
    AsyncApp = None  # type: ignore
    AsyncSocketModeHandler = None  # type: ignore


def create_slack_app() -> Optional[AsyncApp]:
    """Create and configure the Slack AsyncApp if tokens are available."""
    if AsyncApp is None:
        logger.warning("slack-bolt is not installed. Install with `uv sync --extra chatops`.")
        return None

    settings = get_settings()
    if not settings.slack_bot_token:
        logger.warning("SLACK_BOT_TOKEN is not configured.")
        return None

    app = AsyncApp(
        token=settings.slack_bot_token,
        signing_secret=settings.slack_signing_secret,
    )

    # Register Slash Command /infrabuddy
    @app.command("/infrabuddy")
    async def handle_slash_command(ack, respond, command):
        """Handle slash command /infrabuddy [command] [args]."""
        await ack()
        text = (command.get("text") or "").strip()
        parts = text.split()
        subcmd = parts[0].lower() if parts else "help"
        arg = parts[1].lower() if len(parts) > 1 else "all"

        if subcmd in ("analyze", "check"):
            await respond(
                text=f":mag: InfraBuddy is analyzing AWS infrastructure (target: `{arg}`). Please hold on..."
            )
            # Run analysis asynchronously
            asyncio.create_task(_async_analyze_and_respond(respond, arg))

        elif subcmd == "status":
            await respond(text=":hourglass_flowing_sand: Fetching AWS status snapshot...")
            status = await run_status()
            if status.get("success"):
                region = status.get("region", "unknown")
                await respond(text=f":white_check_mark: InfraBuddy connected to AWS region `{region}` successfully.")
            else:
                err = status.get("error", "Unknown error")
                await respond(text=f":warning: AWS connection error: `{err}`")

        else:
            help_text = (
                "*InfraBuddy Slack Commands:*\n"
                "• `/infrabuddy analyze [service]` — Analyze AWS infrastructure (options: `all`, `ec2`, `alb`, `asg`, `rds`, `cloudwatch`)\n"
                "• `/infrabuddy status` — Check AWS connectivity & raw snapshot\n"
                "• `/infrabuddy help` — Show this help message"
            )
            await respond(text=help_text)

    # Register App Mention
    @app.event("app_mention")
    async def handle_app_mention(event, say):
        """Handle @InfraBuddy mentions in channels."""
        text = event.get("text", "").lower()
        channel = event.get("channel")
        thread_ts = event.get("thread_ts") or event.get("ts")

        if "analyze" in text:
            await say(
                text=":mag: InfraBuddy received analysis request. Starting diagnostic...",
                channel=channel,
                thread_ts=thread_ts,
            )
            # Find requested service filter
            target = "all"
            for s in ["ec2", "alb", "asg", "rds", "cloudwatch"]:
                if s in text:
                    target = s
                    break

            result = await run_analysis(target)
            blocks = to_slack_blocks(result)
            await say(blocks=blocks, text="Analysis Complete", channel=channel, thread_ts=thread_ts)
        else:
            await say(
                text="Hi! Mention me with `analyze` (e.g. `@InfraBuddy analyze ec2`) or use the `/infrabuddy` slash command.",
                channel=channel,
                thread_ts=thread_ts,
            )

    return app


async def _async_analyze_and_respond(respond, service: str):
    """Run analysis and respond to slash command via response_url."""
    try:
        result = await run_analysis(service)
        blocks = to_slack_blocks(result)
        await respond(blocks=blocks, text="InfraBuddy Analysis Results", replace_original=False)
    except Exception as e:
        logger.exception("Failed to run analysis for Slack")
        error_blocks = to_slack_error_blocks(f"Analysis failed unexpectedly: {e}")
        await respond(blocks=error_blocks, text="InfraBuddy Error", replace_original=False)


async def start_socket_mode():
    """Start the Slack app using Socket Mode for local development."""
    settings = get_settings()
    if not settings.slack_app_token:
        raise ValueError("SLACK_APP_TOKEN is required for Socket Mode")

    app = create_slack_app()
    if app is None or AsyncSocketModeHandler is None:
        raise RuntimeError("Could not initialize Slack AsyncApp or AsyncSocketModeHandler")

    handler = AsyncSocketModeHandler(app, settings.slack_app_token)
    logger.info("Starting InfraBuddy Slack bot in Socket Mode...")
    await handler.start_async()
