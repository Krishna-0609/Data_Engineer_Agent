"""
Infrastructure — Concrete Repository Implementations

PostgreSQL-backed repositories using SQLAlchemy 2.0 async sessions.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import AuditLog, Connection, Pipeline, PipelineExecution, Project, User
from app.domain.repositories import (
    AuditLogRepository,
    ConnectionRepository,
    PipelineExecutionRepository,
    PipelineRepository,
    ProjectRepository,
    UserRepository,
)
from app.domain.value_objects import (
    ConnectionId,
    Email,
    ExecutionId,
    PipelineId,
    PipelineStatus,
    ProjectId,
    UserId,
)
from app.infrastructure.database.mappers import (
    AuditLogMapper,
    ConnectionMapper,
    ExecutionMapper,
    PipelineMapper,
    ProjectMapper,
    UserMapper,
)
from app.infrastructure.database.models import (
    AuditLogModel,
    ConnectionModel,
    PipelineExecutionModel,
    PipelineModel,
    ProjectModel,
    UserModel,
)


class PostgresUserRepository(UserRepository):
    """PostgreSQL implementation of UserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user: User) -> User:
        model = UserMapper.to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)

    async def get_by_id(self, user_id: UserId) -> User | None:
        result = await self._session.get(UserModel, user_id.value)
        return UserMapper.to_entity(result) if result else None

    async def get_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_entity(model) if model else None

    async def update(self, user: User) -> User:
        model = await self._session.get(UserModel, user.id.value)
        if not model:
            raise ValueError(f"User {user.id} not found")
        UserMapper.update_model(model, user)
        await self._session.flush()
        await self._session.refresh(model)
        return UserMapper.to_entity(model)

    async def delete(self, user_id: UserId) -> None:
        model = await self._session.get(UserModel, user_id.value)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_all(
        self, offset: int = 0, limit: int = 50, filters: dict[str, Any] | None = None
    ) -> tuple[list[User], int]:
        stmt = select(UserModel)
        count_stmt = select(func.count()).select_from(UserModel)

        if filters:
            if "role" in filters:
                stmt = stmt.where(UserModel.role == filters["role"])
                count_stmt = count_stmt.where(UserModel.role == filters["role"])
            if "is_active" in filters:
                stmt = stmt.where(UserModel.is_active == filters["is_active"])
                count_stmt = count_stmt.where(UserModel.is_active == filters["is_active"])

        total = (await self._session.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit).order_by(UserModel.created_at.desc())
        result = await self._session.execute(stmt)
        users = [UserMapper.to_entity(m) for m in result.scalars().all()]
        return users, total


class PostgresProjectRepository(ProjectRepository):
    """PostgreSQL implementation of ProjectRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, project: Project) -> Project:
        model = ProjectMapper.to_model(project)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ProjectMapper.to_entity(model)

    async def get_by_id(self, project_id: ProjectId) -> Project | None:
        result = await self._session.get(ProjectModel, project_id.value)
        return ProjectMapper.to_entity(result) if result else None

    async def update(self, project: Project) -> Project:
        model = await self._session.get(ProjectModel, project.id.value)
        if not model:
            raise ValueError(f"Project {project.id} not found")
        ProjectMapper.update_model(model, project)
        await self._session.flush()
        await self._session.refresh(model)
        return ProjectMapper.to_entity(model)

    async def delete(self, project_id: ProjectId) -> None:
        model = await self._session.get(ProjectModel, project_id.value)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_by_owner(
        self, owner_id: UserId, offset: int = 0, limit: int = 50
    ) -> tuple[list[Project], int]:
        stmt = select(ProjectModel).where(ProjectModel.owner_id == owner_id.value)
        count_stmt = (
            select(func.count())
            .select_from(ProjectModel)
            .where(ProjectModel.owner_id == owner_id.value)
        )
        total = (await self._session.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit).order_by(ProjectModel.created_at.desc())
        result = await self._session.execute(stmt)
        projects = [ProjectMapper.to_entity(m) for m in result.scalars().all()]
        return projects, total

    async def list_all(
        self, offset: int = 0, limit: int = 50, filters: dict[str, Any] | None = None
    ) -> tuple[list[Project], int]:
        stmt = select(ProjectModel)
        count_stmt = select(func.count()).select_from(ProjectModel)

        if filters and "status" in filters:
            stmt = stmt.where(ProjectModel.status == filters["status"])
            count_stmt = count_stmt.where(ProjectModel.status == filters["status"])

        total = (await self._session.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit).order_by(ProjectModel.created_at.desc())
        result = await self._session.execute(stmt)
        projects = [ProjectMapper.to_entity(m) for m in result.scalars().all()]
        return projects, total


class PostgresPipelineRepository(PipelineRepository):
    """PostgreSQL implementation of PipelineRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, pipeline: Pipeline) -> Pipeline:
        model = PipelineMapper.to_model(pipeline)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return PipelineMapper.to_entity(model)

    async def get_by_id(self, pipeline_id: PipelineId) -> Pipeline | None:
        result = await self._session.get(PipelineModel, pipeline_id.value)
        return PipelineMapper.to_entity(result) if result else None

    async def update(self, pipeline: Pipeline) -> Pipeline:
        model = await self._session.get(PipelineModel, pipeline.id.value)
        if not model:
            raise ValueError(f"Pipeline {pipeline.id} not found")
        PipelineMapper.update_model(model, pipeline)
        await self._session.flush()
        await self._session.refresh(model)
        return PipelineMapper.to_entity(model)

    async def delete(self, pipeline_id: PipelineId) -> None:
        model = await self._session.get(PipelineModel, pipeline_id.value)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_by_project(
        self,
        project_id: ProjectId,
        offset: int = 0,
        limit: int = 50,
        status: PipelineStatus | None = None,
    ) -> tuple[list[Pipeline], int]:
        stmt = select(PipelineModel).where(PipelineModel.project_id == project_id.value)
        count_stmt = (
            select(func.count())
            .select_from(PipelineModel)
            .where(PipelineModel.project_id == project_id.value)
        )
        if status:
            stmt = stmt.where(PipelineModel.status == status.value)
            count_stmt = count_stmt.where(PipelineModel.status == status.value)

        total = (await self._session.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit).order_by(PipelineModel.created_at.desc())
        result = await self._session.execute(stmt)
        pipelines = [PipelineMapper.to_entity(m) for m in result.scalars().all()]
        return pipelines, total

    async def list_all(
        self, offset: int = 0, limit: int = 50, filters: dict[str, Any] | None = None
    ) -> tuple[list[Pipeline], int]:
        stmt = select(PipelineModel)
        count_stmt = select(func.count()).select_from(PipelineModel)

        if filters and "status" in filters:
            stmt = stmt.where(PipelineModel.status == filters["status"])
            count_stmt = count_stmt.where(PipelineModel.status == filters["status"])

        total = (await self._session.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit).order_by(PipelineModel.created_at.desc())
        result = await self._session.execute(stmt)
        pipelines = [PipelineMapper.to_entity(m) for m in result.scalars().all()]
        return pipelines, total


class PostgresExecutionRepository(PipelineExecutionRepository):
    """PostgreSQL implementation of PipelineExecutionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, execution: PipelineExecution) -> PipelineExecution:
        model = ExecutionMapper.to_model(execution)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ExecutionMapper.to_entity(model)

    async def get_by_id(self, execution_id: ExecutionId) -> PipelineExecution | None:
        result = await self._session.get(PipelineExecutionModel, execution_id.value)
        return ExecutionMapper.to_entity(result) if result else None

    async def update(self, execution: PipelineExecution) -> PipelineExecution:
        model = await self._session.get(PipelineExecutionModel, execution.id.value)
        if not model:
            raise ValueError(f"Execution {execution.id} not found")
        ExecutionMapper.update_model(model, execution)
        await self._session.flush()
        await self._session.refresh(model)
        return ExecutionMapper.to_entity(model)

    async def list_by_pipeline(
        self, pipeline_id: PipelineId, offset: int = 0, limit: int = 50
    ) -> tuple[list[PipelineExecution], int]:
        stmt = select(PipelineExecutionModel).where(
            PipelineExecutionModel.pipeline_id == pipeline_id.value
        )
        count_stmt = (
            select(func.count())
            .select_from(PipelineExecutionModel)
            .where(PipelineExecutionModel.pipeline_id == pipeline_id.value)
        )
        total = (await self._session.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit).order_by(
            PipelineExecutionModel.created_at.desc()
        )
        result = await self._session.execute(stmt)
        execs = [ExecutionMapper.to_entity(m) for m in result.scalars().all()]
        return execs, total


class PostgresAuditLogRepository(AuditLogRepository):
    """PostgreSQL implementation of AuditLogRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, audit_log: AuditLog) -> AuditLog:
        model = AuditLogMapper.to_model(audit_log)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return AuditLogMapper.to_entity(model)

    async def list_by_user(
        self, user_id: UserId, offset: int = 0, limit: int = 50
    ) -> tuple[list[AuditLog], int]:
        stmt = select(AuditLogModel).where(AuditLogModel.user_id == user_id.value)
        count_stmt = (
            select(func.count())
            .select_from(AuditLogModel)
            .where(AuditLogModel.user_id == user_id.value)
        )
        total = (await self._session.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit).order_by(AuditLogModel.created_at.desc())
        result = await self._session.execute(stmt)
        logs = [AuditLogMapper.to_entity(m) for m in result.scalars().all()]
        return logs, total

    async def list_by_resource(
        self,
        resource_type: str,
        resource_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditLog], int]:
        stmt = select(AuditLogModel).where(
            AuditLogModel.resource_type == resource_type,
            AuditLogModel.resource_id == resource_id,
        )
        count_stmt = (
            select(func.count())
            .select_from(AuditLogModel)
            .where(
                AuditLogModel.resource_type == resource_type,
                AuditLogModel.resource_id == resource_id,
            )
        )
        total = (await self._session.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit).order_by(AuditLogModel.created_at.desc())
        result = await self._session.execute(stmt)
        logs = [AuditLogMapper.to_entity(m) for m in result.scalars().all()]
        return logs, total


class PostgresConnectionRepository(ConnectionRepository):
    """PostgreSQL implementation of ConnectionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, connection: Connection) -> Connection:
        model = ConnectionMapper.to_model(connection)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return ConnectionMapper.to_entity(model)

    async def get_by_id(self, connection_id: ConnectionId) -> Connection | None:
        result = await self._session.get(ConnectionModel, connection_id.value)
        return ConnectionMapper.to_entity(result) if result else None

    async def update(self, connection: Connection) -> Connection:
        model = await self._session.get(ConnectionModel, connection.id.value)
        if not model:
            raise ValueError(f"Connection {connection.id} not found")
        model.name = connection.name
        model.category = connection.category.value
        model.connection_type = connection.connection_type.value
        model.encrypted_config = connection.encrypted_config
        model.description = connection.description
        model.status = connection.status
        model.updated_at = connection.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return ConnectionMapper.to_entity(model)

    async def delete(self, connection_id: ConnectionId) -> None:
        model = await self._session.get(ConnectionModel, connection_id.value)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_by_project(
        self, project_id: ProjectId, offset: int = 0, limit: int = 50
    ) -> tuple[list[Connection], int]:
        stmt = select(ConnectionModel).where(ConnectionModel.project_id == project_id.value)
        count_stmt = (
            select(func.count())
            .select_from(ConnectionModel)
            .where(ConnectionModel.project_id == project_id.value)
        )
        total = (await self._session.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit).order_by(ConnectionModel.created_at.desc())
        result = await self._session.execute(stmt)
        connections = [ConnectionMapper.to_entity(m) for m in result.scalars().all()]
        return connections, total
