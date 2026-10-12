"""
server.py

Unified FastAPI server application serving:
- Health check endpoints
- Slack events router (/slack/events)
- Microsoft Teams messages router (/teams/messages)
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from agent.config import get_settings

logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    FastAPI = None  # type: ignore
    CORSMiddleware = None  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hook for startup and shutdown events."""
    settings = get_settings()
    logger.info("Starting InfraBuddy ChatOps Server...")
    logger.info("AWS Region: %s | Model Provider: %s", settings.aws_region, settings.model_provider)
    yield
    logger.info("Shutting down InfraBuddy ChatOps Server...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install with `uv sync --extra chatops`.")

    settings = get_settings()

    app = FastAPI(
        title="InfraBuddy ChatOps API",
        description="Unified ChatOps server for Slack & Microsoft Teams AWS diagnostics",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    if CORSMiddleware and settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Basic Health Check
    @app.get("/health", tags=["System"])
    async def health():
        return {
            "status": "healthy",
            "service": "infrabuddy-chatops",
            "region": settings.aws_region,
            "provider": settings.model_provider,
        }

    # Mount Slack router
    try:
        from chatops.slack.server import get_slack_router

        slack_router = get_slack_router()
        if slack_router:
            app.include_router(slack_router)
            logger.info("Slack ChatOps router mounted at /slack")
    except Exception as exc:
        logger.warning("Could not mount Slack router: %s", exc)

    # Mount Teams router
    try:
        from chatops.teams.server import get_teams_router

        teams_router = get_teams_router()
        if teams_router:
            app.include_router(teams_router)
            logger.info("Teams ChatOps router mounted at /teams")
    except Exception as exc:
        logger.warning("Could not mount Teams router: %s", exc)

    return app


app = create_app() if FastAPI is not None else None


def run():
    """CLI runner function for console script entry point."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        workers=settings.api_workers,
    )


if __name__ == "__main__":
    run()
