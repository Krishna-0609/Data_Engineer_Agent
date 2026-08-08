"""
Test Configuration — Shared Fixtures

Provides async database sessions, test client, mock Redis,
and auth helper factories for all backend tests.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.infrastructure.database.session import Base, get_async_session
from app.infrastructure.security.password import hash_password
from app.infrastructure.security.jwt import JWTService
from app.infrastructure.cache.redis import RedisCache
from app.dependencies import get_redis_cache
from app.main import create_app


# ---------------------------------------------------------------------------
# Fake Redis — in-memory substitute for tests
# ---------------------------------------------------------------------------

class FakeRedisCache(RedisCache):
    """In-memory Redis substitute for unit tests."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float | None]] = {}

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        self._store.clear()

    async def get(self, key: str) -> str | None:
        entry = self._store.get(key)
        return entry[0] if entry else None

    async def set(self, key: str, value: str, expire_seconds: int | None = None) -> None:
        self._store[key] = (value, expire_seconds)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return key in self._store

    async def get_json(self, key: str) -> Any | None:
        import json
        raw = await self.get(key)
        return json.loads(raw) if raw else None

    async def set_json(self, key: str, value: Any, expire_seconds: int | None = None) -> None:
        import json
        await self.set(key, json.dumps(value), expire_seconds)

    async def blacklist_token(self, jti: str, expire_seconds: int) -> None:
        await self.set(f"blacklist:{jti}", "1", expire_seconds)

    async def is_token_blacklisted(self, jti: str) -> bool:
        return await self.exists(f"blacklist:{jti}")

    async def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        rate_key = f"rate:{key}"
        entry = self._store.get(rate_key)
        if entry:
            current = int(entry[0]) + 1
        else:
            current = 1
        self._store[rate_key] = (str(current), window_seconds)
        return current <= max_requests


_fake_redis = FakeRedisCache()


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Clear fake redis between tests
    _fake_redis._store.clear()


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# App + Client fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def app():
    """Create a test FastAPI app with overridden dependencies."""
    import app.dependencies as deps

    # Monkey-patch the module-level Redis singleton
    original_redis = deps._redis_cache
    deps._redis_cache = _fake_redis

    test_app = create_app()
    test_app.dependency_overrides[get_async_session] = override_get_async_session

    yield test_app

    # Restore
    deps._redis_cache = original_redis


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Auth helper fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def test_user_data() -> dict[str, str]:
    """Standard test user data."""
    return {
        "email": "test@example.com",
        "password": "SecureP@ssw0rd!",
        "full_name": "Test User",
    }


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient, test_user_data: dict) -> dict:
    """Register a user and return the response data."""
    response = await client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    return response.json()


@pytest_asyncio.fixture
async def auth_headers(registered_user: dict) -> dict[str, str]:
    """Authorization headers for an authenticated user."""
    return {"Authorization": f"Bearer {registered_user['access_token']}"}
