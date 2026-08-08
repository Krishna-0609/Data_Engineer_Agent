"""
Tests — Auth API Endpoints
"""

import pytest
from httpx import AsyncClient


class TestAuthRegister:
    """POST /api/v1/auth/register"""

    async def test_register_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "password": "StrongP@ss1!",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "new@example.com"
        assert data["user"]["role"] == "user"

    async def test_register_duplicate_email(
        self, client: AsyncClient, registered_user: dict
    ):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "AnotherP@ss1!",
                "full_name": "Duplicate User",
            },
        )
        assert response.status_code == 409

    async def test_register_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "StrongP@ss1!",
                "full_name": "Bad Email",
            },
        )
        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@example.com",
                "password": "short",
                "full_name": "Short Pass",
            },
        )
        assert response.status_code == 422


class TestAuthLogin:
    """POST /api/v1/auth/login"""

    async def test_login_success(
        self, client: AsyncClient, registered_user: dict, test_user_data: dict
    ):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_login_wrong_password(
        self, client: AsyncClient, registered_user: dict
    ):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "WrongPassword!"},
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "Password1!"},
        )
        assert response.status_code == 401


class TestAuthMe:
    """GET /api/v1/auth/me"""

    async def test_get_me_authenticated(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    async def test_get_me_no_token(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401


class TestHealthCheck:
    """GET /api/v1/health"""

    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
