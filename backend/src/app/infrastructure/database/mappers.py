"""
Infrastructure — Entity-Model Mappers

Bidirectional mapping between domain entities and ORM models.
Keeps the domain layer clean from persistence concerns.
"""

from __future__ import annotations

import uuid

from app.domain.entities import AuditLog, Connection, Pipeline, PipelineExecution, Project, User
from app.domain.value_objects import (
    AuditAction,
    ConnectionCategory,
    ConnectionId,
    ConnectionType,
    Email,
    ExecutionId,
    ExecutionStatus,
    OrganizationId,
    PipelineId,
    PipelineStatus,
    ProjectId,
    ProjectStatus,
    UserId,
    UserRole,
    UserStatus,
)
from app.infrastructure.database.models import (
    AuditLogModel,
    ConnectionModel,
    PipelineExecutionModel,
    PipelineModel,
    ProjectModel,
    UserModel,
)


class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        status = UserStatus.ACTIVE if model.is_active else UserStatus.INACTIVE
        return User(
            id=UserId(model.id),
            email=Email(model.email),
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role=UserRole(model.role),
            organization_id=OrganizationId(model.organization_id) if model.organization_id else None,
            status=status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id.value,
            email=str(entity.email),
            hashed_password=entity.hashed_password,
            full_name=entity.full_name,
            role=entity.role.value,
            organization_id=entity.organization_id.value if entity.organization_id else None,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: UserModel, entity: User) -> UserModel:
        model.email = str(entity.email)
        model.hashed_password = entity.hashed_password
        model.full_name = entity.full_name
        model.role = entity.role.value
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        return model


class ProjectMapper:
    @staticmethod
    def to_entity(model: ProjectModel) -> Project:
        return Project(
            id=ProjectId(model.id),
            name=model.name,
            description=model.description or "",
            owner_id=UserId(model.owner_id),
            organization_id=OrganizationId(model.organization_id) if model.organization_id else None,
            settings=model.settings or {},
            status=ProjectStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Project) -> ProjectModel:
        return ProjectModel(
            id=entity.id.value,
            name=entity.name,
            description=entity.description,
            owner_id=entity.owner_id.value,
            organization_id=entity.organization_id.value if entity.organization_id else None,
            settings=entity.settings,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: ProjectModel, entity: Project) -> ProjectModel:
        model.name = entity.name
        model.description = entity.description
        model.settings = entity.settings
        model.status = entity.status.value
        model.updated_at = entity.updated_at
        return model


class PipelineMapper:
    @staticmethod
    def to_entity(model: PipelineModel) -> Pipeline:
        return Pipeline(
            id=PipelineId(model.id),
            project_id=ProjectId(model.project_id),
            name=model.name,
            description=model.description or "",
            status=PipelineStatus(model.status),
            version=model.version,
            spec=model.spec or {},
            created_by=UserId(model.created_by) if model.created_by else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Pipeline) -> PipelineModel:
        return PipelineModel(
            id=entity.id.value,
            project_id=entity.project_id.value,
            name=entity.name,
            description=entity.description,
            status=entity.status.value,
            version=entity.version,
            spec=entity.spec,
            created_by=entity.created_by.value if entity.created_by else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: PipelineModel, entity: Pipeline) -> PipelineModel:
        model.name = entity.name
        model.description = entity.description
        model.status = entity.status.value
        model.version = entity.version
        model.spec = entity.spec
        model.updated_at = entity.updated_at
        return model


class ExecutionMapper:
    @staticmethod
    def to_entity(model: PipelineExecutionModel) -> PipelineExecution:
        return PipelineExecution(
            id=ExecutionId(model.id),
            pipeline_id=PipelineId(model.pipeline_id),
            status=ExecutionStatus(model.status),
            started_at=model.started_at,
            completed_at=model.completed_at,
            logs=model.logs or [],
            metrics=model.metrics or {},
            error=model.error,
            triggered_by=UserId(model.triggered_by) if model.triggered_by else None,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: PipelineExecution) -> PipelineExecutionModel:
        return PipelineExecutionModel(
            id=entity.id.value,
            pipeline_id=entity.pipeline_id.value,
            status=entity.status.value,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            logs=entity.logs,
            metrics=entity.metrics,
            error=entity.error,
            triggered_by=entity.triggered_by.value if entity.triggered_by else None,
            created_at=entity.created_at,
        )

    @staticmethod
    def update_model(
        model: PipelineExecutionModel, entity: PipelineExecution
    ) -> PipelineExecutionModel:
        model.status = entity.status.value
        model.started_at = entity.started_at
        model.completed_at = entity.completed_at
        model.logs = entity.logs
        model.metrics = entity.metrics
        model.error = entity.error
        return model


class AuditLogMapper:
    @staticmethod
    def to_entity(model: AuditLogModel) -> AuditLog:
        return AuditLog(
            id=model.id,
            user_id=UserId(model.user_id) if model.user_id else UserId(uuid.UUID(int=0)),
            action=AuditAction(model.action),
            resource_type=model.resource_type or "",
            resource_id=model.resource_id,
            details=model.details or {},
            ip_address=str(model.ip_address) if model.ip_address else None,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: AuditLog) -> AuditLogModel:
        return AuditLogModel(
            id=entity.id,
            user_id=entity.user_id.value,
            action=entity.action.value,
            resource_type=entity.resource_type,
            resource_id=entity.resource_id,
            details=entity.details,
            ip_address=entity.ip_address,
            created_at=entity.created_at,
        )


class ConnectionMapper:
    @staticmethod
    def to_entity(model: ConnectionModel) -> Connection:
        return Connection(
            id=ConnectionId(model.id),
            project_id=ProjectId(model.project_id),
            name=model.name,
            category=ConnectionCategory(model.category),
            connection_type=ConnectionType(model.connection_type),
            encrypted_config=model.encrypted_config,
            description=model.description,
            status=model.status,
            created_by=UserId(model.created_by) if model.created_by else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Connection) -> ConnectionModel:
        return ConnectionModel(
            id=entity.id.value,
            project_id=entity.project_id.value,
            name=entity.name,
            category=entity.category.value,
            connection_type=entity.connection_type.value,
            encrypted_config=entity.encrypted_config,
            description=entity.description,
            status=entity.status,
            created_by=entity.created_by.value if entity.created_by else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
