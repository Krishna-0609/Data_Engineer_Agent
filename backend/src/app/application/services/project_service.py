"""
Application — Project Service

CRUD operations for projects with authorization checks.
"""

from __future__ import annotations

from typing import Any

import structlog

from app.application.exceptions import AuthorizationError, NotFoundError
from app.domain.entities import Project
from app.domain.repositories import ProjectRepository
from app.domain.value_objects import ProjectId, UserId, UserRole

logger = structlog.get_logger()


class ProjectService:
    def __init__(self, project_repo: ProjectRepository) -> None:
        self._repo = project_repo

    async def create_project(
        self,
        name: str,
        description: str,
        owner_id: UserId,
        settings: dict[str, Any] | None = None,
    ) -> Project:
        project = Project.create(
            name=name,
            description=description,
            owner_id=owner_id,
            settings=settings,
        )
        created = await self._repo.create(project)
        logger.info("project.created", project_id=str(created.id), name=name)
        return created

    async def get_project(self, project_id: str, user_id: UserId, user_role: UserRole) -> Project:
        project = await self._repo.get_by_id(ProjectId.from_str(project_id))
        if not project:
            raise NotFoundError("Project", project_id)
        if user_role != UserRole.ADMIN and project.owner_id != user_id:
            raise AuthorizationError("You do not have access to this project")
        return project

    async def list_projects(
        self,
        user_id: UserId,
        user_role: UserRole,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Project], int]:
        if user_role == UserRole.ADMIN:
            return await self._repo.list_all(offset=offset, limit=limit)
        return await self._repo.list_by_owner(user_id, offset=offset, limit=limit)

    async def update_project(
        self,
        project_id: str,
        user_id: UserId,
        user_role: UserRole,
        name: str | None = None,
        description: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> Project:
        project = await self.get_project(project_id, user_id, user_role)
        project.update(name=name, description=description, settings=settings)
        updated = await self._repo.update(project)
        logger.info("project.updated", project_id=project_id)
        return updated

    async def archive_project(
        self, project_id: str, user_id: UserId, user_role: UserRole
    ) -> Project:
        project = await self.get_project(project_id, user_id, user_role)
        project.archive()
        updated = await self._repo.update(project)
        logger.info("project.archived", project_id=project_id)
        return updated
