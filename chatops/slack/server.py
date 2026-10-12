"""
chatops/slack/server.py

FastAPI router integration for Slack events and interactions via HTTP webhook.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from fastapi import APIRouter, Request, Response
    from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
    from chatops.slack.bot import create_slack_app
except ImportError:
    APIRouter = None  # type: ignore
    AsyncSlackRequestHandler = None  # type: ignore
    create_slack_app = None  # type: ignore


def get_slack_router() -> Optional[APIRouter]:
    """Create FastAPI router for Slack endpoints."""
    if APIRouter is None or AsyncSlackRequestHandler is None:
        logger.warning("FastAPI or slack-bolt not available for Slack router.")
        return None

    app = create_slack_app()
    if app is None:
        return None

    handler = AsyncSlackRequestHandler(app)
    router = APIRouter(prefix="/slack", tags=["Slack"])

    @router.post("/events")
    async def slack_events(req: Request) -> Response:
        """Handle incoming Slack events, commands, and interactive payloads."""
        return await handler.handle(req)

    return router
