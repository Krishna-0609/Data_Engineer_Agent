"""
API Middleware — Error Handler

Maps application exceptions to proper HTTP responses.
Catches unhandled exceptions and returns structured error JSON.
"""

from __future__ import annotations

import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.application.exceptions import (
    AlreadyExistsError,
    AppError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
)

logger = structlog.get_logger()

_EXCEPTION_STATUS_MAP = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    AlreadyExistsError: status.HTTP_409_CONFLICT,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    ValidationError: 422,
}


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle known application errors."""
    status_code = _EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code, "message": exc.message},
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors — log full traceback, return sanitized response."""
    logger.exception("unhandled_error", path=request.url.path, method=request.method)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )
