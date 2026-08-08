"""
API v1 — Auth Routes
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Header

from app.api.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.application.services.auth_service import AuthService
from app.dependencies import get_auth_service, get_current_user, CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    """Register a new user account."""
    return await auth_service.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    """Authenticate with email and password."""
    return await auth_service.login(email=body.email, password=body.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    """Exchange a refresh token for a new token pair."""
    return await auth_service.refresh_token(body.refresh_token)


@router.post("/logout", status_code=204)
async def logout(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """Invalidate the current access token."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        await auth_service.logout(token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    """Get current authenticated user profile."""
    return await auth_service.get_user_profile(current_user.user_id)
