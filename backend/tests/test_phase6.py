"""
Tests — Phase 6: Scheduler, Alerting & Lineage Unit & Integration Tests
"""

import pytest
from httpx import AsyncClient

from app.application.services.lineage_service import DataLineageService
from app.application.services.scheduler_service import PipelineSchedulerService
from app.infrastructure.notifications.alert_service import AlertService


class TestSchedulerUnit:
    @pytest.mark.asyncio
    async def test_schedule_and_unschedule_pipeline(self):
        scheduler = PipelineSchedulerService()
        scheduler.start()

        async def dummy_job():
            pass

        # Schedule valid cron
        success = scheduler.schedule_pipeline("pipe_123", "0 2 * * *", dummy_job)
        assert success is True

        jobs = scheduler.list_jobs()
        assert len(jobs) == 1
        assert jobs[0]["job_id"] == "pipeline_job_pipe_123"

        # Unschedule job
        removed = scheduler.unschedule_pipeline("pipe_123")
        assert removed is True
        assert len(scheduler.list_jobs()) == 0

        scheduler.shutdown()


class TestAlertServiceUnit:
    async def test_slack_alert_no_url_graceful_skip(self):
        alert_svc = AlertService()
        result = await alert_svc.send_slack_alert(
            pipeline_name="ETL Customer Sync",
            status="success",
            details="Ingested 1000 rows successfully.",
            rows_processed=1000,
        )
        assert result is False

    async def test_email_alert_dispatch(self):
        alert_svc = AlertService()
        result = await alert_svc.send_email_alert(
            recipient="data-lead@company.com",
            subject="Pipeline Failure Alert",
            body="Pipeline failed at step 2.",
        )
        assert result is True


class TestLineageServiceUnit:
    def test_generate_lineage_graph(self):
        svc = DataLineageService()
        spec = {
            "nodes": [
                {"id": "1", "name": "Extract (CSV)", "type": "extract"},
                {"id": "2", "name": "Clean Data", "type": "transform"},
                {"id": "3", "name": "Load Target", "type": "load"},
            ],
            "edges": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
            ],
        }

        lineage = svc.generate_lineage(spec)
        assert len(lineage["nodes"]) == 3
        assert len(lineage["links"]) == 2
        assert len(lineage["column_lineage"]) > 0
        assert lineage["column_lineage"][0]["source_column"] == "user_id"


class TestLineageAPIEndpoint:
    async def test_get_pipeline_lineage_endpoint(
        self, client: AsyncClient, auth_headers: dict
    ):
        # Create project and pipeline
        proj_resp = await client.post(
            "/api/v1/projects/",
            json={"name": "Lineage Proj"},
            headers=auth_headers,
        )
        proj_id = proj_resp.json()["id"]

        pipe_resp = await client.post(
            "/api/v1/pipelines/",
            json={
                "project_id": proj_id,
                "name": "Lineage Test Pipeline",
                "spec": {
                    "nodes": [
                        {"id": "1", "name": "Ingest S3", "type": "extract"},
                        {"id": "2", "name": "Load RDS", "type": "load"},
                    ]
                },
            },
            headers=auth_headers,
        )
        assert pipe_resp.status_code == 201
        pipe_id = pipe_resp.json()["id"]

        # Call lineage endpoint
        lineage_resp = await client.get(
            f"/api/v1/pipelines/{pipe_id}/lineage",
            headers=auth_headers,
        )
        assert lineage_resp.status_code == 200
        data = lineage_resp.json()
        assert "nodes" in data
        assert "column_lineage" in data
