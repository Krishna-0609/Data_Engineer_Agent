"""
Application — Pipeline Cron Scheduler Service

Uses APScheduler (AsyncIOScheduler) to execute background data pipelines
automatically based on cron schedule specifications.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Coroutine

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog

logger = structlog.get_logger()


class PipelineSchedulerService:
    """
    Background job scheduler for autonomous pipeline execution on cron schedules.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._scheduler = AsyncIOScheduler()
        self._is_running = False

    def start(self) -> None:
        """Start the background scheduler."""
        if not self._is_running:
            self._scheduler.start()
            self._is_running = True
            logger.info("scheduler.started")

    def shutdown(self) -> None:
        """Shutdown the background scheduler cleanly."""
        if self._is_running:
            self._scheduler.shutdown(wait=False)
            self._is_running = False
            logger.info("scheduler.shutdown")

    def schedule_pipeline(
        self,
        pipeline_id: str,
        cron_expression: str,
        job_func: Callable[[], Coroutine[Any, Any, Any]],
    ) -> bool:
        """
        Schedule or update a pipeline job using a standard 5-part cron expression (e.g. '0 2 * * *').
        """
        job_id = f"pipeline_job_{pipeline_id}"

        try:
            # Remove existing job if updated
            if self._scheduler.get_job(job_id):
                self._scheduler.remove_job(job_id)

            parts = cron_expression.strip().split()
            if len(parts) != 5:
                raise ValueError("Cron expression must have 5 fields (minute, hour, day, month, day_of_week)")

            trigger = CronTrigger.from_crontab(cron_expression)
            self._scheduler.add_job(
                job_func,
                trigger=trigger,
                id=job_id,
                name=f"Pipeline {pipeline_id}",
                replace_existing=True,
            )
            logger.info("scheduler.job_added", pipeline_id=pipeline_id, cron=cron_expression)
            return True
        except Exception as exc:
            logger.error("scheduler.add_job_failed", pipeline_id=pipeline_id, error=str(exc))
            return False

    def unschedule_pipeline(self, pipeline_id: str) -> bool:
        """Unschedule a pipeline job."""
        job_id = f"pipeline_job_{pipeline_id}"
        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)
            logger.info("scheduler.job_removed", pipeline_id=pipeline_id)
            return True
        return False

    def list_jobs(self) -> list[dict[str, Any]]:
        """List active scheduled pipeline jobs and their next run times."""
        jobs = []
        for job in self._scheduler.get_jobs():
            next_run = job.next_run_time.isoformat() if job.next_run_time else None
            jobs.append({
                "job_id": job.id,
                "name": job.name,
                "next_run_time": next_run,
            })
        return jobs
