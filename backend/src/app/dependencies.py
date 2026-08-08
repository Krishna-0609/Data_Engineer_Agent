"""
Dependency Injection — FastAPI Dependencies

Provides repositories, services, and auth context via FastAPI's Depends system.
This is the composition root — the only place that knows about concrete implementations.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import AuthenticationError
from app.application.services.auth_service import AuthService
from app.application.services.pipeline_service import PipelineService
from app.application.services.project_service import ProjectService
from app.domain.value_objects import UserId, UserRole
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.database.repositories import (
    PostgresAuditLogRepository,
    PostgresExecutionRepository,
    PostgresPipelineRepository,
    PostgresProjectRepository,
    PostgresUserRepository,
)
from app.infrastructure.database.session import get_async_session
from app.infrastructure.security.jwt import JWTService, TokenError

# -- Singleton instances --
_redis_cache = RedisCache()
_jwt_service = JWTService()


def get_redis_cache() -> RedisCache:
    return _redis_cache


def get_jwt_service() -> JWTService:
    return _jwt_service


# -- Repository Factories --

async def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PostgresUserRepository:
    return PostgresUserRepository(session)


async def get_project_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PostgresProjectRepository:
    return PostgresProjectRepository(session)


async def get_pipeline_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PostgresPipelineRepository:
    return PostgresPipelineRepository(session)


async def get_execution_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PostgresExecutionRepository:
    return PostgresExecutionRepository(session)


async def get_audit_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PostgresAuditLogRepository:
    return PostgresAuditLogRepository(session)


# -- Service Factories --

async def get_auth_service(
    user_repo: Annotated[PostgresUserRepository, Depends(get_user_repo)],
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        jwt_service=_jwt_service,
        cache=_redis_cache,
    )


async def get_project_service(
    project_repo: Annotated[PostgresProjectRepository, Depends(get_project_repo)],
) -> ProjectService:
    return ProjectService(project_repo=project_repo)


from app.application.services.agent_service import AgentService
from app.application.services.connection_service import ConnectionService
from app.application.services.execution_engine import ExecutionEngine
from app.infrastructure.database.repositories import PostgresConnectionRepository
from app.infrastructure.security.vault_service import VaultService

_vault_service = VaultService()


async def get_connection_repo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PostgresConnectionRepository:
    return PostgresConnectionRepository(session=session)


async def get_vault_service() -> VaultService:
    return _vault_service


async def get_connection_service(
    connection_repo: Annotated[PostgresConnectionRepository, Depends(get_connection_repo)],
    project_repo: Annotated[PostgresProjectRepository, Depends(get_project_repo)],
    vault_service: Annotated[VaultService, Depends(get_vault_service)],
) -> ConnectionService:
    return ConnectionService(
        connection_repo=connection_repo,
        project_repo=project_repo,
        vault_service=vault_service,
    )


async def get_execution_engine(
    execution_repo: Annotated[PostgresExecutionRepository, Depends(get_execution_repo)],
    pipeline_repo: Annotated[PostgresPipelineRepository, Depends(get_pipeline_repo)],
) -> ExecutionEngine:
    return ExecutionEngine(execution_repo=execution_repo, pipeline_repo=pipeline_repo)


async def get_agent_service(
    pipeline_repo: Annotated[PostgresPipelineRepository, Depends(get_pipeline_repo)],
    project_repo: Annotated[PostgresProjectRepository, Depends(get_project_repo)],
) -> AgentService:
    return AgentService(pipeline_repo=pipeline_repo, project_repo=project_repo)


async def get_pipeline_service(
    pipeline_repo: Annotated[PostgresPipelineRepository, Depends(get_pipeline_repo)],
    execution_repo: Annotated[PostgresExecutionRepository, Depends(get_execution_repo)],
    project_repo: Annotated[PostgresProjectRepository, Depends(get_project_repo)],
    execution_engine: Annotated[ExecutionEngine, Depends(get_execution_engine)],
) -> PipelineService:
    return PipelineService(
        pipeline_repo=pipeline_repo,
        execution_repo=execution_repo,
        project_repo=project_repo,
        execution_engine=execution_engine,
    )


# -- Auth Dependencies --

class CurrentUser:
    """Represents the authenticated user context."""

    def __init__(self, user_id: UserId, role: UserRole) -> None:
        self.user_id = user_id
        self.role = role


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)] = None,
) -> CurrentUser:
    """
    Extract and verify the JWT from the Authorization header via HTTPBearer security scheme.
    Returns a CurrentUser context with user_id and role.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = _jwt_service.verify_token(token, expected_type="access")
    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Check blacklist
    if await _redis_cache.is_token_blacklisted(payload.jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    return CurrentUser(
        user_id=UserId(payload.user_id),
        role=UserRole(payload.role),
    )


def require_role(*roles: UserRole):
    """Dependency factory that enforces role-based access control."""

    async def _check_role(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' is not authorized. "
                       f"Required: {[r.value for r in roles]}",
            )
        return current_user

    return _check_role
