"""
Infrastructure — JWT Token Management

Handles creation and verification of JWT access and refresh tokens.
Uses python-jose with cryptographic backend for RS256/HS256 signing.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import get_settings


class TokenError(Exception):
    """Raised when token operations fail."""
    pass


class TokenPayload:
    """Decoded token payload."""

    def __init__(
        self,
        sub: str,
        role: str,
        token_type: str,
        exp: datetime,
        jti: str,
    ) -> None:
        self.sub = sub
        self.role = role
        self.token_type = token_type
        self.exp = exp
        self.jti = jti

    @property
    def user_id(self) -> uuid.UUID:
        return uuid.UUID(self.sub)


class JWTService:
    """Stateless JWT token creation and verification."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def create_access_token(self, user_id: uuid.UUID, role: str) -> str:
        """Create a short-lived access token."""
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.jwt_access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "exp": expires,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(
            payload, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm
        )

    def create_refresh_token(self, user_id: uuid.UUID, role: str) -> str:
        """Create a long-lived refresh token."""
        expires = datetime.now(timezone.utc) + timedelta(
            days=self._settings.jwt_refresh_token_expire_days
        )
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "refresh",
            "exp": expires,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(
            payload, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm
        )

    def verify_token(self, token: str, expected_type: str = "access") -> TokenPayload:
        """
        Verify and decode a JWT token.

        Raises TokenError if the token is invalid, expired, or wrong type.
        """
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret_key,
                algorithms=[self._settings.jwt_algorithm],
            )
        except JWTError as e:
            raise TokenError(f"Invalid token: {e}") from e

        if payload.get("type") != expected_type:
            raise TokenError(
                f"Expected {expected_type} token, got {payload.get('type')}"
            )

        return TokenPayload(
            sub=payload["sub"],
            role=payload.get("role", "user"),
            token_type=payload["type"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            jti=payload.get("jti", ""),
        )

    def create_token_pair(
        self, user_id: uuid.UUID, role: str
    ) -> dict[str, str]:
        """Create both access and refresh tokens."""
        return {
            "access_token": self.create_access_token(user_id, role),
            "refresh_token": self.create_refresh_token(user_id, role),
            "token_type": "bearer",
        }
