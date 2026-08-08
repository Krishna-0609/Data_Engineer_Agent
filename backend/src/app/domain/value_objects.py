"""
Domain Layer — Value Objects

Immutable value types used across the domain. These encapsulate validation rules
and ensure type-safety throughout the application.
"""

from __future__ import annotations

import enum
import re
import uuid
from dataclasses import dataclass
from typing import Self


# =============================================================================
# ID Types — Typed wrappers around UUID for domain safety
# =============================================================================


@dataclass(frozen=True, slots=True)
class UserId:
    """Unique identifier for a User aggregate."""

    value: uuid.UUID

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_str(cls, raw: str) -> Self:
        return cls(value=uuid.UUID(raw))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ProjectId:
    """Unique identifier for a Project aggregate."""

    value: uuid.UUID

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_str(cls, raw: str) -> Self:
        return cls(value=uuid.UUID(raw))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class PipelineId:
    """Unique identifier for a Pipeline aggregate."""

    value: uuid.UUID

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_str(cls, raw: str) -> Self:
        return cls(value=uuid.UUID(raw))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ExecutionId:
    """Unique identifier for a Pipeline Execution."""

    value: uuid.UUID

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_str(cls, raw: str) -> Self:
        return cls(value=uuid.UUID(raw))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class OrganizationId:
    """Unique identifier for an Organization."""

    value: uuid.UUID

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_str(cls, raw: str) -> Self:
        return cls(value=uuid.UUID(raw))

    def __str__(self) -> str:
        return str(self.value)


# =============================================================================
# Email — Validated email value object
# =============================================================================

_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


@dataclass(frozen=True, slots=True)
class Email:
    """
    Validated email address.

    Normalizes to lowercase on construction and validates format.
    """

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        # frozen=True requires object.__setattr__
        object.__setattr__(self, "value", normalized)
        if not _EMAIL_REGEX.match(normalized):
            raise ValueError(f"Invalid email address: {self.value}")
        if len(normalized) > 255:
            raise ValueError("Email address must be 255 characters or fewer")

    def __str__(self) -> str:
        return self.value


# =============================================================================
# Enumerations
# =============================================================================


class UserRole(str, enum.Enum):
    """Authorization roles for users."""

    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    """Lifecycle status for user accounts."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class ProjectStatus(str, enum.Enum):
    """Lifecycle status for projects."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class PipelineStatus(str, enum.Enum):
    """Lifecycle status for pipeline definitions."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    FAILED = "failed"


class ExecutionStatus(str, enum.Enum):
    """Runtime status for pipeline executions."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass(frozen=True, slots=True)
class ConnectionId:
    """Unique identifier for a Connection."""

    value: uuid.UUID

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_str(cls, raw: str) -> Self:
        return cls(value=uuid.UUID(raw))

    def __str__(self) -> str:
        return str(self.value)


class ConnectionCategory(str, enum.Enum):
    """Category of data connection."""

    SOURCE = "source"
    DESTINATION = "destination"
    BI_ANALYTICS = "bi_analytics"


class ConnectionType(str, enum.Enum):
    """Supported connector types."""

    AWS_S3 = "aws_s3"
    AWS_RDS_POSTGRES = "aws_rds_postgres"
    AWS_RDS_MYSQL = "aws_rds_mysql"
    SNOWFLAKE = "snowflake"
    REST_API = "rest_api"
    AWS_QUICKSIGHT = "aws_quicksight"
    POWER_BI = "power_bi"


class AuditAction(str, enum.Enum):
    """Types of auditable actions."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXECUTE = "execute"
    DEPLOY = "deploy"
