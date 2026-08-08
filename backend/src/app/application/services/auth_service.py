"""
Application — Auth Service

Handles user registration, login, token refresh, and logout.
Orchestrates domain entities, repositories, and infrastructure services.
"""

from __future__ import annotations

import structlog

from app.application.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    NotFoundError,
)
from app.domain.entities import User
from app.domain.repositories import UserRepository
from app.domain.value_objects import Email
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.security.jwt import JWTService, TokenError
from app.infrastructure.security.password import hash_password, verify_password

logger = structlog.get_logger()


class AuthService:
    """Application service for authentication operations."""

    def __init__(
        self,
        user_repo: UserRepository,
        jwt_service: JWTService,
        cache: RedisCache,
    ) -> None:
        self._user_repo = user_repo
        self._jwt = jwt_service
        self._cache = cache

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
    ) -> dict:
        """
        Register a new user account.

        Returns token pair on success.
        Raises AlreadyExistsError if email is taken.
        """
        existing = await self._user_repo.get_by_email(Email(email))
        if existing:
            raise AlreadyExistsError("User", "email", email)

        user = User.create(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )
        created_user = await self._user_repo.create(user)

        tokens = self._jwt.create_token_pair(
            created_user.id.value, created_user.role.value
        )

        logger.info(
            "user.registered",
            user_id=str(created_user.id),
            email=email,
        )

        return {
            **tokens,
            "user": {
                "id": str(created_user.id),
                "email": str(created_user.email),
                "full_name": created_user.full_name,
                "role": created_user.role.value,
            },
        }

    async def login(self, email: str, password: str) -> dict:
        """
        Authenticate a user and return token pair.

        Raises AuthenticationError if credentials are invalid.
        """
        user = await self._user_repo.get_by_email(Email(email))
        if not user:
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        tokens = self._jwt.create_token_pair(user.id.value, user.role.value)

        logger.info("user.logged_in", user_id=str(user.id), email=email)

        return {
            **tokens,
            "user": {
                "id": str(user.id),
                "email": str(user.email),
                "full_name": user.full_name,
                "role": user.role.value,
            },
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Exchange a valid refresh token for a new token pair.

        The old refresh token's JTI is blacklisted to prevent reuse.
        """
        try:
            payload = self._jwt.verify_token(refresh_token, expected_type="refresh")
        except TokenError as e:
            raise AuthenticationError(str(e)) from e

        # Check if token has been blacklisted (logout / previous refresh)
        if await self._cache.is_token_blacklisted(payload.jti):
            raise AuthenticationError("Token has been revoked")

        # Blacklist the old refresh token
        remaining = int((payload.exp - __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        )).total_seconds())
        if remaining > 0:
            await self._cache.blacklist_token(payload.jti, remaining)

        user = await self._user_repo.get_by_id(
            __import__("app.domain.value_objects", fromlist=["UserId"]).UserId(payload.user_id)
        )
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        return self._jwt.create_token_pair(user.id.value, user.role.value)

    async def logout(self, access_token: str) -> None:
        """Blacklist the current access token's JTI."""
        try:
            payload = self._jwt.verify_token(access_token, expected_type="access")
            remaining = int((payload.exp - __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            )).total_seconds())
            if remaining > 0:
                await self._cache.blacklist_token(payload.jti, remaining)
        except TokenError:
            pass  # Token already expired, no need to blacklist

        logger.info("user.logged_out")

    async def get_user_profile(self, user_id: UserId) -> dict:
        """Return user profile by UserId."""
        user = await self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise NotFoundError("User", str(user_id))

        return {
            "id": str(user.id),
            "email": str(user.email),
            "full_name": user.full_name,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
        }

    async def get_current_user(self, token: str) -> dict:
        """Decode access token and return user profile."""
        try:
            payload = self._jwt.verify_token(token, expected_type="access")
        except TokenError as e:
            raise AuthenticationError(str(e)) from e

        if await self._cache.is_token_blacklisted(payload.jti):
            raise AuthenticationError("Token has been revoked")

        from app.domain.value_objects import UserId
        return await self.get_user_profile(UserId(payload.user_id))
