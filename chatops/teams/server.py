"""
chatops/teams/server.py

FastAPI router integration for Microsoft Teams Bot Framework messages.
"""

from __future__ import annotations

import logging
from typing import Optional

from agent.config import get_settings
from chatops.teams.bot import InfraBuddyTeamsBot

logger = logging.getLogger(__name__)

try:
    from fastapi import APIRouter, Request, Response, status
    from botbuilder.core import (
        BotFrameworkAdapter,
        BotFrameworkAdapterSettings,
    )
    from botbuilder.schema import Activity
except ImportError:
    APIRouter = None  # type: ignore
    BotFrameworkAdapter = None  # type: ignore
    BotFrameworkAdapterSettings = None  # type: ignore
    Activity = None  # type: ignore


def get_teams_router() -> Optional[APIRouter]:
    """Create FastAPI router for Teams Bot Framework messages."""
    if APIRouter is None or BotFrameworkAdapter is None:
        logger.warning("BotFramework SDK or FastAPI is not available for Teams router.")
        return None

    settings = get_settings()
    app_id = settings.microsoft_app_id or ""
    app_password = settings.microsoft_app_password or ""

    adapter_settings = BotFrameworkAdapterSettings(app_id=app_id, app_password=app_password)
    adapter = BotFrameworkAdapter(adapter_settings)
    bot = InfraBuddyTeamsBot()

    router = APIRouter(prefix="/teams", tags=["Teams"])

    @router.post("/messages")
    async def messages(request: Request) -> Response:
        """Handle incoming HTTP messages from Microsoft Teams Bot Service."""
        if "application/json" not in request.headers.get("Content-Type", ""):
            return Response(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        body = await request.json()
        activity = Activity().deserialize(body)
        auth_header = request.headers.get("Authorization", "")

        try:
            response = await adapter.process_activity(activity, auth_header, bot.on_turn)
            if response:
                return Response(status_code=response.status, content=response.body)
            return Response(status_code=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to process Teams activity")
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(e))

    return router
