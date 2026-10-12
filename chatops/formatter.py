"""
chatops/formatter.py

Converts AnalysisResult objects into platform-specific message payloads:
  - Slack   → Block Kit (list of block dicts)
  - Teams   → Bot Framework Activity with Adaptive Card attachment
"""

from __future__ import annotations

import textwrap
from typing import Any

from chatops.core import AnalysisResult

# Maximum characters for a single Slack section block text field
_SLACK_BLOCK_LIMIT = 3000
# Maximum characters for an Adaptive Card text block
_TEAMS_TEXT_LIMIT = 4000


# ---------------------------------------------------------------------------
# Slack — Block Kit
# ---------------------------------------------------------------------------

def to_slack_blocks(result: AnalysisResult) -> list[dict[str, Any]]:
    """
    Build a Slack Block Kit payload from an AnalysisResult.

    Returns a list of blocks ready to pass to ``client.chat_postMessage``.
    """
    blocks: list[dict[str, Any]] = []

    if not result.success:
        blocks.append(_slack_section(f":x: *Analysis failed*\n{result.error or 'Unknown error'}"))
        return blocks

    # Header
    service_label = (
        f"Service: `{result.service_filter}`" if result.service_filter != "all" else "All services"
    )
    blocks.append(
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🔍 InfraBuddy Analysis", "emoji": True},
        }
    )
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        f"*Region:* `{result.region}` · "
                        f"*{service_label}* · "
                        f"*Model:* `{result.model}`"
                    ),
                }
            ],
        }
    )
    blocks.append({"type": "divider"})

    # Warnings
    for warning in result.warnings:
        blocks.append(_slack_section(f":warning: {warning}"))

    # Analysis body — split into chunks to respect Slack's 3 000 char limit
    for chunk in _chunk_text(result.analysis, _SLACK_BLOCK_LIMIT):
        blocks.append(_slack_section(chunk))
        blocks.append({"type": "divider"})

    # Footer
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        "_InfraBuddy is read-only and never modifies AWS resources. "
                        "Always verify recommendations before acting._"
                    ),
                }
            ],
        }
    )
    return blocks


def to_slack_error_blocks(message: str) -> list[dict[str, Any]]:
    """Quick error payload for user-facing Slack errors."""
    return [_slack_section(f":x: {message}")]


def _slack_section(text: str) -> dict[str, Any]:
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


# ---------------------------------------------------------------------------
# Teams — Adaptive Card
# ---------------------------------------------------------------------------

def to_teams_adaptive_card(result: AnalysisResult) -> dict[str, Any]:
    """
    Build a Teams Adaptive Card payload from an AnalysisResult.

    Returns a dict that can be set as ``attachment`` on a Bot Framework Activity.
    """
    body: list[dict[str, Any]] = []

    if not result.success:
        body.append(_teams_text(f"❌ **Analysis failed**\n\n{result.error or 'Unknown error'}"))
        return _wrap_adaptive_card(body)

    # Header
    body.append(
        {
            "type": "TextBlock",
            "text": "🔍 InfraBuddy Analysis",
            "weight": "Bolder",
            "size": "Large",
            "wrap": True,
        }
    )

    service_label = result.service_filter if result.service_filter != "all" else "All services"
    body.append(
        {
            "type": "FactSet",
            "facts": [
                {"title": "Region", "value": result.region},
                {"title": "Service", "value": service_label},
                {"title": "Model", "value": result.model},
            ],
        }
    )
    body.append({"type": "Separator"})

    # Warnings
    for warning in result.warnings:
        body.append(_teams_text(f"⚠️ {warning}"))

    # Analysis body — split into chunks
    for chunk in _chunk_text(result.analysis, _TEAMS_TEXT_LIMIT):
        body.append(_teams_text(chunk))

    # Footer
    body.append({"type": "Separator"})
    body.append(
        {
            "type": "TextBlock",
            "text": (
                "_InfraBuddy is read-only and never modifies AWS resources. "
                "Always verify recommendations before acting._"
            ),
            "isSubtle": True,
            "wrap": True,
            "size": "Small",
        }
    )

    return _wrap_adaptive_card(body)


def to_teams_error_card(message: str) -> dict[str, Any]:
    """Quick error Adaptive Card for Teams."""
    body = [_teams_text(f"❌ {message}")]
    return _wrap_adaptive_card(body)


def _teams_text(text: str) -> dict[str, Any]:
    return {"type": "TextBlock", "text": text, "wrap": True}


def _wrap_adaptive_card(body: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": body,
        },
    }


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _chunk_text(text: str, limit: int) -> list[str]:
    """Split text into chunks no larger than ``limit`` characters."""
    if len(text) <= limit:
        return [text]
    # Try to split on paragraph boundaries first
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= limit:
            current = f"{current}\n\n{para}".lstrip("\n")
        else:
            if current:
                chunks.append(current)
            # If a single paragraph exceeds the limit, hard-wrap it
            if len(para) > limit:
                for line in textwrap.wrap(para, limit):
                    chunks.append(line)
                current = ""
            else:
                current = para
    if current:
        chunks.append(current)
    return chunks or [text[:limit]]
