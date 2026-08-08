"""
Domain Layer — Repository Interfaces

Abstract repository contracts that the infrastructure layer must implement.
These follow the Repository Pattern, keeping the domain layer decoupled
from any specific persistence technology.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities import AuditLog, Connection, Pipeline, PipelineExecution, Project, User
from app.domain.value_objects import (
    ConnectionId,
    Email,
    ExecutionId,
    PipelineId,
    PipelineStatus,
    ProjectId,
    UserId,
)


class UserRepository(ABC):
    """Abstract repository for User aggregate persistence."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persist a new user. Raises if email already exists."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> User | None:
        """Retrieve a user by their unique identifier."""
        ...

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """Retrieve a user by their email address."""
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """Persist changes to an existing user."""
        ...

    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """Hard-delete a user. Prefer deactivation via entity method."""
        ...

    @abstractmethod
    async def list_all(
        self,
        offset: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[User], int]:
        """
        Return a paginated list of users and total count.

        Args:
            offset: Number of records to skip.
            limit: Maximum number of records to return.
            filters: Optional dict of field-value pairs to filter by.

        Returns:
            Tuple of (users, total_count).
        """
        ...


class ProjectRepository(ABC):
    """Abstract repository for Project aggregate persistence."""

    @abstractmethod
    async def create(self, project: Project) -> Project:
        ...

    @abstractmethod
    async def get_by_id(self, project_id: ProjectId) -> Project | None:
        ...

    @abstractmethod
    async def update(self, project: Project) -> Project:
        ...

    @abstractmethod
    async def delete(self, project_id: ProjectId) -> None:
        ...

    @abstractmethod
    async def list_by_owner(
        self,
        owner_id: UserId,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Project], int]:
        """List projects owned by or accessible to a specific user."""
        ...

    @abstractmethod
    async def list_all(
        self,
        offset: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[Project], int]:
        ...


class PipelineRepository(ABC):
    """Abstract repository for Pipeline aggregate persistence."""

    @abstractmethod
    async def create(self, pipeline: Pipeline) -> Pipeline:
        ...

    @abstractmethod
    async def get_by_id(self, pipeline_id: PipelineId) -> Pipeline | None:
        ...

    @abstractmethod
    async def update(self, pipeline: Pipeline) -> Pipeline:
        ...

    @abstractmethod
    async def delete(self, pipeline_id: PipelineId) -> None:
        ...

    @abstractmethod
    async def list_by_project(
        self,
        project_id: ProjectId,
        offset: int = 0,
        limit: int = 50,
        status: PipelineStatus | None = None,
    ) -> tuple[list[Pipeline], int]:
        """List pipelines within a project, optionally filtered by status."""
        ...

    @abstractmethod
    async def list_all(
        self,
        offset: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[Pipeline], int]:
        ...


class PipelineExecutionRepository(ABC):
    """Abstract repository for PipelineExecution persistence."""

    @abstractmethod
    async def create(self, execution: PipelineExecution) -> PipelineExecution:
        ...

    @abstractmethod
    async def get_by_id(self, execution_id: ExecutionId) -> PipelineExecution | None:
        ...

    @abstractmethod
    async def update(self, execution: PipelineExecution) -> PipelineExecution:
        ...

    @abstractmethod
    async def list_by_pipeline(
        self,
        pipeline_id: PipelineId,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[PipelineExecution], int]:
        ...


class AuditLogRepository(ABC):
    """Abstract repository for AuditLog persistence."""

    @abstractmethod
    async def create(self, audit_log: AuditLog) -> AuditLog:
        ...

    @abstractmethod
    async def list_by_user(
        self,
        user_id: UserId,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditLog], int]:
        ...

    @abstractmethod
    async def list_by_resource(
        self,
        resource_type: str,
        resource_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditLog], int]:
        ...


class ConnectionRepository(ABC):
    """Abstract repository for Connection aggregate persistence."""

    @abstractmethod
    async def create(self, connection: Connection) -> Connection:
        ...

    @abstractmethod
    async def get_by_id(self, connection_id: ConnectionId) -> Connection | None:
        ...

    @abstractmethod
    async def update(self, connection: Connection) -> Connection:
        ...

    @abstractmethod
    async def delete(self, connection_id: ConnectionId) -> None:
        ...

    @abstractmethod
    async def list_by_project(
        self,
        project_id: ProjectId,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Connection], int]:
        ...
