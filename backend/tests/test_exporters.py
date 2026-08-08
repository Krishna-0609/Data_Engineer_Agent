"""
Tests — Apache Airflow & Prefect Exporters and Endpoints
"""

import pytest
from httpx import AsyncClient

from app.application.exporters.airflow_exporter import AirflowDAGExporter
from app.application.exporters.dagster_exporter import DagsterExporter
from app.application.exporters.dbt_exporter import DBTExporter
from app.application.exporters.prefect_exporter import PrefectExporter
from app.domain.entities import Pipeline, PipelineStatus
from app.domain.value_objects import PipelineId, ProjectId, UserId


@pytest.fixture
def sample_pipeline() -> Pipeline:
    return Pipeline(
        id=PipelineId.generate(),
        project_id=ProjectId.generate(),
        name="Sales Analytics ETL",
        description="Extract sales transactions and aggregate totals",
        status=PipelineStatus.ACTIVE,
        version=1,
        created_by=UserId.generate(),
        spec={
            "source": "Postgres",
            "destination": "Snowflake",
            "nodes": [
                {"id": "extract_step", "label": "Extract Postgres Records", "type": "extractor"},
                {"id": "transform_step", "label": "Data Cleaning & Nulls", "type": "transformer"},
                {"id": "load_step", "label": "Load Target Table", "type": "loader"},
            ],
            "code": {
                "python": "import pandas as pd\nprint('Running ETL')",
                "sql": "SELECT * FROM sales;",
            },
            "parameters": {
                "schedule_interval": "@daily",
                "max_retries": 3,
            },
        },
    )


class TestExportersUnit:
    def test_airflow_exporter_generates_valid_python(self, sample_pipeline: Pipeline):
        exporter = AirflowDAGExporter()
        code = exporter.export_dag_code(sample_pipeline)

        assert "from airflow import DAG" in code
        assert "from airflow.operators.python import PythonOperator" in code
        assert 'dag_id="sales_analytics_etl"' in code
        assert "extract_step_task" in code
        assert "transform_step_task" in code
        assert "load_step_task" in code
        assert "extract_step_task >> transform_step_task >> load_step_task" in code

    def test_prefect_exporter_generates_valid_script(self, sample_pipeline: Pipeline):
        exporter = PrefectExporter()
        code = exporter.export_flow_code(sample_pipeline)

        assert "from prefect import flow, task" in code
        assert '@flow(name="Sales Analytics ETL"' in code
        assert "@task(name=\"Extract Postgres Records\")" in code
        assert "def sales_analytics_etl_flow():" in code

    def test_dbt_exporter_generates_sql_and_schema(self, sample_pipeline: Pipeline):
        exporter = DBTExporter()
        files = exporter.export_dbt_project(sample_pipeline)

        assert "models/sales_analytics_etl.sql" in files
        assert "models/schema.yml" in files
        assert "WITH source_data AS (" in files["models/sales_analytics_etl.sql"]
        assert "models:" in files["models/schema.yml"]

    def test_dagster_exporter_generates_valid_script(self, sample_pipeline: Pipeline):
        exporter = DagsterExporter()
        code = exporter.export_dagster_code(sample_pipeline)

        assert "from dagster import OpExecutionContext, job, op" in code
        assert '@op(name="extract_step")' in code
        assert "@job(name=\"sales_analytics_etl_job\")" in code


class TestExporterEndpoints:
    async def test_export_airflow_endpoint(self, client: AsyncClient, auth_headers: dict):
        proj_resp = await client.post(
            "/api/v1/projects/",
            json={"name": "Export Test Proj", "description": "Testing exports"},
            headers=auth_headers,
        )
        assert proj_resp.status_code == 201
        proj_id = proj_resp.json()["id"]

        gen_resp = await client.post(
            "/api/v1/agent/generate",
            json={
                "project_id": proj_id,
                "prompt": "Extract user events from Postgres and load into Snowflake.",
            },
            headers=auth_headers,
        )
        assert gen_resp.status_code == 201
        pipeline_id = gen_resp.json()["id"]

        export_resp = await client.get(
            f"/api/v1/pipelines/{pipeline_id}/export/airflow",
            headers=auth_headers,
        )
        assert export_resp.status_code == 200
        assert "from airflow import DAG" in export_resp.text
        assert "PythonOperator" in export_resp.text

    async def test_export_prefect_endpoint(self, client: AsyncClient, auth_headers: dict):
        proj_resp = await client.post(
            "/api/v1/projects/",
            json={"name": "Prefect Export Proj"},
            headers=auth_headers,
        )
        proj_id = proj_resp.json()["id"]

        gen_resp = await client.post(
            "/api/v1/agent/generate",
            json={
                "project_id": proj_id,
                "prompt": "Extract logs from S3 and clean invalid IP addresses.",
            },
            headers=auth_headers,
        )
        pipeline_id = gen_resp.json()["id"]

        export_resp = await client.get(
            f"/api/v1/pipelines/{pipeline_id}/export/prefect",
            headers=auth_headers,
        )
        assert export_resp.status_code == 200
        assert "from prefect import flow, task" in export_resp.text

    async def test_export_dbt_endpoint(self, client: AsyncClient, auth_headers: dict):
        proj_resp = await client.post(
            "/api/v1/projects/",
            json={"name": "dbt Export Proj"},
            headers=auth_headers,
        )
        proj_id = proj_resp.json()["id"]

        gen_resp = await client.post(
            "/api/v1/agent/generate",
            json={
                "project_id": proj_id,
                "prompt": "Build dbt models for daily active users.",
            },
            headers=auth_headers,
        )
        pipeline_id = gen_resp.json()["id"]

        export_resp = await client.get(
            f"/api/v1/pipelines/{pipeline_id}/export/dbt",
            headers=auth_headers,
        )
        assert export_resp.status_code == 200
        data = export_resp.json()
        assert "models/schema.yml" in data

    async def test_export_dagster_endpoint(self, client: AsyncClient, auth_headers: dict):
        proj_resp = await client.post(
            "/api/v1/projects/",
            json={"name": "Dagster Export Proj"},
            headers=auth_headers,
        )
        proj_id = proj_resp.json()["id"]

        gen_resp = await client.post(
            "/api/v1/agent/generate",
            json={
                "project_id": proj_id,
                "prompt": "Build Dagster job for streaming metrics.",
            },
            headers=auth_headers,
        )
        pipeline_id = gen_resp.json()["id"]

        export_resp = await client.get(
            f"/api/v1/pipelines/{pipeline_id}/export/dagster",
            headers=auth_headers,
        )
        assert export_resp.status_code == 200
        assert "from dagster import" in export_resp.text

