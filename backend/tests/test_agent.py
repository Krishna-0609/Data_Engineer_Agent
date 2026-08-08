"""
Tests — AI Agent Generation & Execution API Endpoints
"""

import pytest
from httpx import AsyncClient


class TestAgentAPI:
    """AI Agent synthesis and execution tests."""

    async def _create_project(self, client: AsyncClient, headers: dict) -> str:
        resp = await client.post(
            "/api/v1/projects/",
            json={"name": "Agent Project", "description": "For AI Agent generation tests"},
            headers=headers,
        )
        return resp.json()["id"]

    async def test_generate_pipeline_from_prompt(self, client: AsyncClient, auth_headers: dict):
        project_id = await self._create_project(client, auth_headers)
        prompt = "Extract CSV user transactions, drop null emails, calculate daily active users, and load into target table"

        response = await client.post(
            "/api/v1/agent/generate",
            json={
                "project_id": project_id,
                "prompt": prompt,
                "pipeline_name": "AI Generated ETL Pipeline",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "AI Generated ETL Pipeline"
        assert data["status"] == "active"
        assert "nodes" in data["spec"]
        assert "code" in data["spec"]
        assert len(data["spec"]["nodes"]) >= 3

    async def test_refine_pipeline(self, client: AsyncClient, auth_headers: dict):
        project_id = await self._create_project(client, auth_headers)
        
        # 1. Generate
        gen_resp = await client.post(
            "/api/v1/agent/generate",
            json={
                "project_id": project_id,
                "prompt": "Extract API data and load to S3 bucket",
            },
            headers=auth_headers,
        )
        pipeline_id = gen_resp.json()["id"]

        # 2. Refine
        refine_resp = await client.post(
            "/api/v1/agent/refine",
            json={
                "pipeline_id": pipeline_id,
                "refinement_prompt": "Add data validation rule for email syntax",
            },
            headers=auth_headers,
        )
        assert refine_resp.status_code == 200
        ref_data = refine_resp.json()
        assert ref_data["version"] == 2
        assert len(ref_data["spec"]["refinements"]) >= 1

    async def test_execute_agent_generated_pipeline(self, client: AsyncClient, auth_headers: dict):
        project_id = await self._create_project(client, auth_headers)
        gen_resp = await client.post(
            "/api/v1/agent/generate",
            json={
                "project_id": project_id,
                "prompt": "Extract Postgres sales logs, filter completed sales, and write summary to Snowflake",
            },
            headers=auth_headers,
        )
        pipeline_id = gen_resp.json()["id"]

        # Execute
        exec_resp = await client.post(
            f"/api/v1/pipelines/{pipeline_id}/execute",
            headers=auth_headers,
        )
        assert exec_resp.status_code == 201
        exec_data = exec_resp.json()
        assert exec_data["status"] == "success"
        assert exec_data["metrics"]["rows_written"] > 0
        assert len(exec_data["logs"]) >= 3
