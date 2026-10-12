"""
chatops/teams/bot.py

Microsoft Teams bot implementation using Bot Framework ActivityHandler.
"""

from __future__ import annotations

import logging
from typing import Optional

from chatops.core import run_analysis, run_status
from chatops.formatter import to_teams_adaptive_card, to_teams_error_card

logger = logging.getLogger(__name__)

try:
    from botbuilder.core import ActivityHandler, TurnContext, CardFactory
    from botbuilder.schema import Activity, ActivityTypes
except ImportError:
    ActivityHandler = object  # type: ignore
    TurnContext = None  # type: ignore
    CardFactory = None  # type: ignore
    Activity = None  # type: ignore
    ActivityTypes = None  # type: ignore


class InfraBuddyTeamsBot(ActivityHandler):
    """Teams Activity Handler for InfraBuddy chat operations."""

    async def on_message_activity(self, turn_context: TurnContext):
        """Process messages directed at the bot in Microsoft Teams."""
        text = (turn_context.activity.text or "").strip().lower()

        # Clean mention tags if present (e.g. <at>InfraBuddy</at>)
        if "@infrabuddy" in text:
            text = text.replace("@infrabuddy", "").strip()

        parts = text.split()
        subcmd = parts[0] if parts else "help"
        arg = parts[1] if len(parts) > 1 else "all"

        if subcmd in ("analyze", "check"):
            await turn_context.send_activity(
                Activity(
                    type=ActivityTypes.message,
                    text=f"🔍 InfraBuddy is analyzing AWS infrastructure (target: `{arg}`). Please wait...",
                )
            )

            result = await run_analysis(arg)
            card = to_teams_adaptive_card(result)

            reply = Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(card["content"])] if CardFactory else [],
            )
            await turn_context.send_activity(reply)

        elif subcmd == "status":
            await turn_context.send_activity("⏳ Fetching AWS connection snapshot...")
            status = await run_status()
            if status.get("success"):
                region = status.get("region", "unknown")
                await turn_context.send_activity(
                    f"✅ InfraBuddy successfully connected to AWS region `{region}`."
                )
            else:
                err = status.get("error", "Unknown error")
                await turn_context.send_activity(f"⚠️ AWS status check failed: `{err}`")

        else:
            help_message = (
                "**InfraBuddy Teams Commands:**\n\n"
                "- `@InfraBuddy analyze [service]` — Run AI diagnostic (services: `all`, `ec2`, `alb`, `asg`, `rds`, `cloudwatch`)\n"
                "- `@InfraBuddy status` — Quick connection & region status check\n"
                "- `@InfraBuddy help` — Show this guide"
            )
            await turn_context.send_activity(help_message)

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        """Welcome new users when added to conversation."""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "👋 Welcome! I am **InfraBuddy**, your AWS AI DevOps Assistant. "
                    "Type `@InfraBuddy analyze` to start an infrastructure health diagnosis."
                )
