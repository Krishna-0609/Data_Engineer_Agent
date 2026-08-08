"""
API Layer — Pydantic Request/Response Schemas

Defines the API contract. Separate from domain entities and ORM models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# =============================================================================
# Generic
# =============================================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: list[Any]
    total: int
    offset: int
    limit: int


class ErrorResponse(BaseModel):
    """Standard error response."""
    code: str
    message: str
    details: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    environment: str


# =============================================================================
# Auth
# =============================================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


# =============================================================================
# User
# =============================================================================

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: str
    created_at: datetime | None = None


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    role: str | None = None


# =============================================================================
# Project
# =============================================================================

class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=5000)
    settings: dict[str, Any] | None = None


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    settings: dict[str, Any] | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    owner_id: str
    status: str
    settings: dict[str, Any]
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Pipeline
# =============================================================================

class PipelineCreateRequest(BaseModel):
    project_id: str
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=5000)
    spec: dict[str, Any] | None = None


class PipelineUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    spec: dict[str, Any] | None = None


class PipelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    description: str
    status: str
    version: int
    spec: dict[str, Any]
    created_by: str | None
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Pipeline Execution
# =============================================================================

class ExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    pipeline_id: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    logs: list[dict[str, Any]]
    metrics: dict[str, Any]
    error: str | None
    triggered_by: str | None
    created_at: datetime


# Fix forward reference
TokenResponse.model_rebuild()
