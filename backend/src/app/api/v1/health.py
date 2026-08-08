"""
API v1 — Health Check Route
"""

from fastapi import APIRouter

from app.api.schemas import HealthResponse
from app.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Application health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_env,
    )
