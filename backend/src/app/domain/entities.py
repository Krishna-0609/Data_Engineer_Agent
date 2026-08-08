"""
Domain Layer — Entity Definitions

Core business entities following DDD principles. Each entity encapsulates
its own invariants and business rules. Entities are persistence-agnostic.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

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


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# =============================================================================
# User Entity
# =============================================================================


@dataclass
class User:
    """
    User aggregate root.

    Represents an authenticated user of the platform. Users belong to an
    organization and have a role that determines their authorization level.
    """

    id: UserId
    email: Email
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.USER
    organization_id: OrganizationId | None = None
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        email: str,
        hashed_password: str,
        full_name: str,
        role: UserRole = UserRole.USER,
        organization_id: OrganizationId | None = None,
    ) -> User:
        """Factory method to create a new User with validated fields."""
        return cls(
            id=UserId.generate(),
            email=Email(email),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            role=role,
            organization_id=organization_id,
            status=UserStatus.ACTIVE,
        )

    def deactivate(self) -> None:
        """Deactivate this user account."""
        self.status = UserStatus.INACTIVE
        self.updated_at = _utcnow()

    def suspend(self) -> None:
        """Suspend this user account."""
        self.status = UserStatus.SUSPENDED
        self.updated_at = _utcnow()

    def activate(self) -> None:
        """Re-activate this user account."""
        self.status = UserStatus.ACTIVE
        self.updated_at = _utcnow()

    def update_profile(self, full_name: str | None = None, role: UserRole | None = None) -> None:
        """Update mutable profile fields."""
        if full_name is not None:
            self.full_name = full_name.strip()
        if role is not None:
            self.role = role
        self.updated_at = _utcnow()

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


# =============================================================================
# Project Entity
# =============================================================================


@dataclass
class Project:
    """
    Project aggregate root.

    Organizes pipelines under a named project within an organization.
    """

    id: ProjectId
    name: str
    description: str
    owner_id: UserId
    organization_id: OrganizationId | None = None
    settings: dict[str, Any] = field(default_factory=dict)
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        owner_id: UserId,
        organization_id: OrganizationId | None = None,
        settings: dict[str, Any] | None = None,
    ) -> Project:
        """Factory method to create a new Project."""
        return cls(
            id=ProjectId.generate(),
            name=name.strip(),
            description=description.strip(),
            owner_id=owner_id,
            organization_id=organization_id,
            settings=settings or {},
        )

    def archive(self) -> None:
        self.status = ProjectStatus.ARCHIVED
        self.updated_at = _utcnow()

    def restore(self) -> None:
        self.status = ProjectStatus.ACTIVE
        self.updated_at = _utcnow()

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> None:
        if name is not None:
            self.name = name.strip()
        if description is not None:
            self.description = description.strip()
        if settings is not None:
            self.settings = settings
        self.updated_at = _utcnow()

    @property
    def is_active(self) -> bool:
        return self.status == ProjectStatus.ACTIVE


# =============================================================================
# Pipeline Entity
# =============================================================================


@dataclass
class Pipeline:
    """
    Pipeline aggregate root.

    Represents an ETL/ELT pipeline definition with versioned specification.
    """

    id: PipelineId
    project_id: ProjectId
    name: str
    description: str
    status: PipelineStatus = PipelineStatus.DRAFT
    version: int = 1
    spec: dict[str, Any] = field(default_factory=dict)
    created_by: UserId | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        project_id: ProjectId,
        name: str,
        description: str,
        created_by: UserId,
        spec: dict[str, Any] | None = None,
    ) -> Pipeline:
        """Factory method to create a new Pipeline in draft status."""
        return cls(
            id=PipelineId.generate(),
            project_id=project_id,
            name=name.strip(),
            description=description.strip(),
            created_by=created_by,
            spec=spec or {},
        )

    def activate(self) -> None:
        self.status = PipelineStatus.ACTIVE
        self.updated_at = _utcnow()

    def pause(self) -> None:
        self.status = PipelineStatus.PAUSED
        self.updated_at = _utcnow()

    def archive(self) -> None:
        self.status = PipelineStatus.ARCHIVED
        self.updated_at = _utcnow()

    def update_spec(self, spec: dict[str, Any]) -> None:
        """Update pipeline spec and bump version."""
        self.spec = spec
        self.version += 1
        self.updated_at = _utcnow()

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        spec: dict[str, Any] | None = None,
    ) -> None:
        if name is not None:
            self.name = name.strip()
        if description is not None:
            self.description = description.strip()
        if spec is not None:
            self.update_spec(spec)
        self.updated_at = _utcnow()

    @property
    def is_active(self) -> bool:
        return self.status == PipelineStatus.ACTIVE


# =============================================================================
# Pipeline Execution Entity
# =============================================================================


@dataclass
class PipelineExecution:
    """
    Tracks a single execution run of a pipeline.

    This is a child entity of Pipeline, not an aggregate root.
    """

    id: ExecutionId
    pipeline_id: PipelineId
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    logs: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    triggered_by: UserId | None = None
    created_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(cls, pipeline_id: PipelineId, triggered_by: UserId) -> PipelineExecution:
        return cls(
            id=ExecutionId.generate(),
            pipeline_id=pipeline_id,
            triggered_by=triggered_by,
        )

    def start(self) -> None:
        self.status = ExecutionStatus.RUNNING
        self.started_at = _utcnow()

    def succeed(self, metrics: dict[str, Any] | None = None) -> None:
        self.status = ExecutionStatus.SUCCESS
        self.completed_at = _utcnow()
        if metrics:
            self.metrics = metrics

    def fail(self, error: str) -> None:
        self.status = ExecutionStatus.FAILED
        self.completed_at = _utcnow()
        self.error = error

    def cancel(self) -> None:
        self.status = ExecutionStatus.CANCELLED
        self.completed_at = _utcnow()

    def append_log(self, level: str, message: str, **extra: Any) -> None:
        self.logs.append(
            {"timestamp": _utcnow().isoformat(), "level": level, "message": message, **extra}
        )

    @property
    def duration_seconds(self) -> float | None:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


# =============================================================================
# Audit Log Entity
# =============================================================================


@dataclass
class AuditLog:
    """
    Immutable audit trail entry.

    Records every significant action for compliance and debugging.
    """

    id: uuid.UUID
    user_id: UserId
    action: AuditAction
    resource_type: str
    resource_id: uuid.UUID | None = None
    details: dict[str, Any] = field(default_factory=dict)
    ip_address: str | None = None
    created_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        user_id: UserId,
        action: AuditAction,
        resource_type: str,
        resource_id: uuid.UUID | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
        )


# =============================================================================
# Connection Entity
# =============================================================================


@dataclass
class Connection:
    """
    Data Connection entity representing secure integrations for sources,
    destinations, and BI analytics endpoints.
    """

    id: ConnectionId
    project_id: ProjectId
    name: str
    category: ConnectionCategory
    connection_type: ConnectionType
    encrypted_config: str
    description: str | None = None
    status: str = "active"
    created_by: UserId | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        project_id: ProjectId,
        name: str,
        category: ConnectionCategory,
        connection_type: ConnectionType,
        encrypted_config: str,
        user_id: UserId,
        description: str | None = None,
    ) -> Connection:
        now = _utcnow()
        return cls(
            id=ConnectionId.generate(),
            project_id=project_id,
            name=name,
            category=category,
            connection_type=connection_type,
            encrypted_config=encrypted_config,
            description=description,
            created_by=user_id,
            created_at=now,
            updated_at=now,
        )
