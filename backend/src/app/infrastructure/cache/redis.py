"""
Infrastructure — Redis Cache Service

Async Redis client for token blacklisting, rate limiting, and general caching.
"""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings


class RedisCache:
    """Async Redis cache client."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: aioredis.Redis | None = None

    async def connect(self) -> None:
        """Initialize Redis connection pool."""
        self._client = aioredis.from_url(
            self._settings.redis_dsn,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )

    async def disconnect(self) -> None:
        """Close Redis connection pool."""
        if self._client:
            await self._client.close()

    @property
    def client(self) -> aioredis.Redis:
        if not self._client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._client

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def set(
        self, key: str, value: str, expire_seconds: int | None = None
    ) -> None:
        await self.client.set(key, value, ex=expire_seconds)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def get_json(self, key: str) -> Any | None:
        raw = await self.get(key)
        if raw:
            return json.loads(raw)
        return None

    async def set_json(
        self, key: str, value: Any, expire_seconds: int | None = None
    ) -> None:
        await self.set(key, json.dumps(value), expire_seconds)

    # -- Token Blacklist --

    async def blacklist_token(self, jti: str, expire_seconds: int) -> None:
        """Add a token JTI to the blacklist."""
        await self.set(f"blacklist:{jti}", "1", expire_seconds)

    async def is_token_blacklisted(self, jti: str) -> bool:
        """Check if a token JTI has been blacklisted."""
        return await self.exists(f"blacklist:{jti}")

    # -- Rate Limiting --

    async def check_rate_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> bool:
        """
        Simple sliding window rate limiter.
        Returns True if the request is within the limit.
        """
        current = await self.client.incr(f"rate:{key}")
        if current == 1:
            await self.client.expire(f"rate:{key}", window_seconds)
        return current <= max_requests
