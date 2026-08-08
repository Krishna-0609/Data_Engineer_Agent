"""
AI Data Engineer Agent — FastAPI Application Factory

Creates and configures the FastAPI application with all middleware,
routes, exception handlers, and lifespan events.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.error_handler import app_error_handler, unhandled_error_handler
from app.api.middleware.request_context import RequestContextMiddleware
from app.api.v1.agent import router as agent_router
from app.api.v1.auth import router as auth_router
from app.api.v1.connections import router as connections_router
from app.api.v1.health import router as health_router
from app.api.v1.pipelines import router as pipeline_router
from app.api.v1.projects import router as project_router
from app.application.exceptions import AppError
from app.config import get_settings
from app.dependencies import get_redis_cache
from app.infrastructure.database.session import close_db

logger = structlog.get_logger()


def _configure_logging() -> None:
    """Configure structlog for structured JSON logging."""
    import logging

    log_level = logging.getLevelNamesMapping().get(
        get_settings().app_log_level.upper(), logging.INFO
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown of shared resources:
    - Redis connection pool
    - Database engine disposal
    """
    settings = get_settings()
    logger.info(
        "app.starting",
        app_name=settings.app_name,
        version=settings.app_version,
        env=settings.app_env,
    )

    # Startup
    redis = get_redis_cache()
    await redis.connect()
    logger.info("redis.connected")

    from app.infrastructure.database.session import engine
    from app.infrastructure.database.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database.tables_ready")

    yield

    # Shutdown
    await redis.disconnect()
    logger.info("redis.disconnected")
    await close_db()
    logger.info("database.disconnected")
    logger.info("app.shutdown_complete")


def create_app() -> FastAPI:
    """
    Application factory.

    Creates and fully configures the FastAPI application.
    """
    settings = get_settings()
    _configure_logging()

    app = FastAPI(
        title="AI Data Engineer Agent",
        description="AI Agent for creating complete ETL/ELT pipelines from natural language",
        version=settings.app_version,
        docs_url="/api/docs" if settings.is_development else None,
        redoc_url="/api/redoc" if settings.is_development else None,
        openapi_url="/api/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # -- Middleware (order matters: last added = first executed) --
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )

    # -- Exception Handlers --
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    # -- Routes --
    api_prefix = "/api/v1"
    app.include_router(health_router, prefix=api_prefix)
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(project_router, prefix=api_prefix)
    app.include_router(pipeline_router, prefix=api_prefix)
    app.include_router(agent_router, prefix=api_prefix)
    app.include_router(connections_router, prefix=api_prefix)

    logger.info("app.configured", routes=len(app.routes))

    return app


# Module-level app instance for uvicorn
app = create_app()
