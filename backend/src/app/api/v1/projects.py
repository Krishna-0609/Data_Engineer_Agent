"""
API v1 — Project Routes
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.schemas import (
    PaginatedResponse,
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)
from app.application.services.project_service import ProjectService
from app.dependencies import CurrentUser, get_current_user, get_project_service

router = APIRouter(prefix="/projects", tags=["Projects"])


def _project_to_response(p) -> dict:
    return {
        "id": str(p.id),
        "name": p.name,
        "description": p.description,
        "owner_id": str(p.owner_id),
        "status": p.status.value,
        "settings": p.settings,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> dict:
    project = await service.create_project(
        name=body.name,
        description=body.description,
        owner_id=current_user.user_id,
        settings=body.settings,
    )
    return _project_to_response(project)


@router.get("/", response_model=PaginatedResponse)
async def list_projects(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ProjectService, Depends(get_project_service)],
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> dict:
    projects, total = await service.list_projects(
        user_id=current_user.user_id,
        user_role=current_user.role,
        offset=offset,
        limit=limit,
    )
    return {
        "items": [_project_to_response(p) for p in projects],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> dict:
    project = await service.get_project(project_id, current_user.user_id, current_user.role)
    return _project_to_response(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    body: ProjectUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> dict:
    project = await service.update_project(
        project_id=project_id,
        user_id=current_user.user_id,
        user_role=current_user.role,
        name=body.name,
        description=body.description,
        settings=body.settings,
    )
    return _project_to_response(project)


@router.delete("/{project_id}", response_model=ProjectResponse)
async def archive_project(
    project_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ProjectService, Depends(get_project_service)],
) -> dict:
    project = await service.archive_project(
        project_id=project_id,
        user_id=current_user.user_id,
        user_role=current_user.role,
    )
    return _project_to_response(project)
