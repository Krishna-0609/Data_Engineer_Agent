"""
Tests — Pipeline API Endpoints
"""

import pytest
from httpx import AsyncClient


class TestPipelineCRUD:
    """Pipeline CRUD operations."""

    async def _create_project(self, client: AsyncClient, headers: dict) -> str:
        resp = await client.post(
            "/api/v1/projects/",
            json={"name": "Pipeline Test Project", "description": "For pipeline tests"},
            headers=headers,
        )
        return resp.json()["id"]

    async def test_create_pipeline(self, client: AsyncClient, auth_headers: dict):
        project_id = await self._create_project(client, auth_headers)
        response = await client.post(
            "/api/v1/pipelines/",
            json={
                "project_id": project_id,
                "name": "Customer ETL",
                "description": "Load customer data",
                "spec": {"source": "postgresql", "destination": "delta_lake"},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Customer ETL"
        assert data["status"] == "draft"
        assert data["version"] == 1

    async def test_list_pipelines(self, client: AsyncClient, auth_headers: dict):
        project_id = await self._create_project(client, auth_headers)
        for i in range(3):
            await client.post(
                "/api/v1/pipelines/",
                json={
                    "project_id": project_id,
                    "name": f"Pipeline {i}",
                    "description": f"Test {i}",
                },
                headers=auth_headers,
            )

        response = await client.get(
            f"/api/v1/pipelines/?project_id={project_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["total"] == 3

    async def test_execute_pipeline(self, client: AsyncClient, auth_headers: dict):
        project_id = await self._create_project(client, auth_headers)
        create_resp = await client.post(
            "/api/v1/pipelines/",
            json={
                "project_id": project_id,
                "name": "Execute Me",
                "description": "Test execution",
            },
            headers=auth_headers,
        )
        pipeline_id = create_resp.json()["id"]

        response = await client.post(
            f"/api/v1/pipelines/{pipeline_id}/execute",
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] in ["running", "success"]
        assert data["pipeline_id"] == pipeline_id

    async def test_get_execution_history(
        self, client: AsyncClient, auth_headers: dict
    ):
        project_id = await self._create_project(client, auth_headers)
        create_resp = await client.post(
            "/api/v1/pipelines/",
            json={
                "project_id": project_id,
                "name": "History Test",
                "description": "Test",
            },
            headers=auth_headers,
        )
        pipeline_id = create_resp.json()["id"]

        # Execute twice
        await client.post(f"/api/v1/pipelines/{pipeline_id}/execute", headers=auth_headers)
        await client.post(f"/api/v1/pipelines/{pipeline_id}/execute", headers=auth_headers)

        response = await client.get(
            f"/api/v1/pipelines/{pipeline_id}/history",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["total"] == 2
