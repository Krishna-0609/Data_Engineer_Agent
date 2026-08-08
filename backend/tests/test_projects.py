"""
Tests — Project API Endpoints
"""

import pytest
from httpx import AsyncClient


class TestProjectCRUD:
    """Project CRUD operations."""

    async def test_create_project(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/v1/projects/",
            json={"name": "ETL Pipeline Project", "description": "Test project"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "ETL Pipeline Project"
        assert data["status"] == "active"

    async def test_list_projects(self, client: AsyncClient, auth_headers: dict):
        # Create two projects
        await client.post(
            "/api/v1/projects/",
            json={"name": "Project 1", "description": "First"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/projects/",
            json={"name": "Project 2", "description": "Second"},
            headers=auth_headers,
        )

        response = await client.get("/api/v1/projects/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_get_project(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/projects/",
            json={"name": "Get Me", "description": "Test"},
            headers=auth_headers,
        )
        project_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/projects/{project_id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Get Me"

    async def test_update_project(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/projects/",
            json={"name": "Original", "description": "Before"},
            headers=auth_headers,
        )
        project_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/projects/{project_id}",
            json={"name": "Updated"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    async def test_archive_project(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/v1/projects/",
            json={"name": "Archive Me", "description": "Test"},
            headers=auth_headers,
        )
        project_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/projects/{project_id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "archived"

    async def test_get_nonexistent_project(
        self, client: AsyncClient, auth_headers: dict
    ):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(
            f"/api/v1/projects/{fake_id}", headers=auth_headers
        )
        assert response.status_code == 404

    async def test_create_project_unauthenticated(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/projects/",
            json={"name": "No Auth", "description": "Should fail"},
        )
        assert response.status_code == 401
