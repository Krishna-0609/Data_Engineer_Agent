"""
Application — Pipeline Service

CRUD and execution operations for pipelines.
"""

from __future__ import annotations

from typing import Any

import structlog

from app.application.exceptions import AuthorizationError, NotFoundError
from app.domain.entities import Pipeline, PipelineExecution
from app.domain.repositories import PipelineExecutionRepository, PipelineRepository, ProjectRepository
from app.domain.value_objects import PipelineId, PipelineStatus, ProjectId, UserId, UserRole

logger = structlog.get_logger()


class PipelineService:
    def __init__(
        self,
        pipeline_repo: PipelineRepository,
        execution_repo: PipelineExecutionRepository,
        project_repo: ProjectRepository,
        execution_engine: Any | None = None,
    ) -> None:
        self._pipeline_repo = pipeline_repo
        self._execution_repo = execution_repo
        self._project_repo = project_repo
        self._execution_engine = execution_engine

    async def _check_project_access(
        self, project_id: str, user_id: UserId, user_role: UserRole
    ) -> None:
        project = await self._project_repo.get_by_id(ProjectId.from_str(project_id))
        if not project:
            raise NotFoundError("Project", project_id)
        if user_role != UserRole.ADMIN and project.owner_id != user_id:
            raise AuthorizationError("No access to this project")

    async def create_pipeline(
        self,
        project_id: str,
        name: str,
        description: str,
        user_id: UserId,
        user_role: UserRole,
        spec: dict[str, Any] | None = None,
    ) -> Pipeline:
        await self._check_project_access(project_id, user_id, user_role)
        pipeline = Pipeline.create(
            project_id=ProjectId.from_str(project_id),
            name=name,
            description=description,
            created_by=user_id,
            spec=spec,
        )
        created = await self._pipeline_repo.create(pipeline)
        logger.info("pipeline.created", pipeline_id=str(created.id), name=name)
        return created

    async def get_pipeline(
        self, pipeline_id: str, user_id: UserId, user_role: UserRole
    ) -> Pipeline:
        pipeline = await self._pipeline_repo.get_by_id(PipelineId.from_str(pipeline_id))
        if not pipeline:
            raise NotFoundError("Pipeline", pipeline_id)
        await self._check_project_access(str(pipeline.project_id), user_id, user_role)
        return pipeline

    async def list_pipelines(
        self,
        project_id: str,
        user_id: UserId,
        user_role: UserRole,
        offset: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> tuple[list[Pipeline], int]:
        await self._check_project_access(project_id, user_id, user_role)
        pipeline_status = PipelineStatus(status) if status else None
        return await self._pipeline_repo.list_by_project(
            ProjectId.from_str(project_id),
            offset=offset,
            limit=limit,
            status=pipeline_status,
        )

    async def update_pipeline(
        self,
        pipeline_id: str,
        user_id: UserId,
        user_role: UserRole,
        name: str | None = None,
        description: str | None = None,
        spec: dict[str, Any] | None = None,
    ) -> Pipeline:
        pipeline = await self.get_pipeline(pipeline_id, user_id, user_role)
        pipeline.update(name=name, description=description, spec=spec)
        updated = await self._pipeline_repo.update(pipeline)
        logger.info("pipeline.updated", pipeline_id=pipeline_id)
        return updated

    async def archive_pipeline(
        self, pipeline_id: str, user_id: UserId, user_role: UserRole
    ) -> Pipeline:
        pipeline = await self.get_pipeline(pipeline_id, user_id, user_role)
        pipeline.archive()
        updated = await self._pipeline_repo.update(pipeline)
        logger.info("pipeline.archived", pipeline_id=pipeline_id)
        return updated

    async def execute_pipeline(
        self, pipeline_id: str, user_id: UserId, user_role: UserRole
    ) -> PipelineExecution:
        pipeline = await self.get_pipeline(pipeline_id, user_id, user_role)
        execution = PipelineExecution.create(
            pipeline_id=pipeline.id,
            triggered_by=user_id,
        )
        created = await self._execution_repo.create(execution)
        logger.info(
            "pipeline.execution.started",
            pipeline_id=pipeline_id,
            execution_id=str(created.id),
        )

        if self._execution_engine:
            return await self._execution_engine.run_execution(str(created.id))

        execution.start()
        return await self._execution_repo.update(execution)

    async def get_execution_history(
        self,
        pipeline_id: str,
        user_id: UserId,
        user_role: UserRole,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[PipelineExecution], int]:
        await self.get_pipeline(pipeline_id, user_id, user_role)
        return await self._execution_repo.list_by_pipeline(
            PipelineId.from_str(pipeline_id), offset=offset, limit=limit
        )
