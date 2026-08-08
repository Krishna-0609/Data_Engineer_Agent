"""
API Router — Connections & Credentials Vault

Endpoints for managing multi-source data connectors and BI analytics endpoints safely.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.application.services.connection_service import ConnectionService
from app.dependencies import CurrentUser, get_connection_service, get_current_user

router = APIRouter(prefix="/connections", tags=["Connections & Vault"])


class ConnectionCreateRequest(BaseModel):
    project_id: str = Field(..., description="ID of the parent project")
    name: str = Field(..., description="Friendly connector name")
    category: str = Field(..., description="source | destination | bi_analytics")
    connection_type: str = Field(..., description="aws_s3 | aws_rds_postgres | snowflake | rest_api | aws_quicksight | power_bi")
    description: str | None = Field(None, description="Optional description")
    config: dict[str, Any] = Field(..., description="Connector parameters and secret credentials")


class ConnectionResponse(BaseModel):
    id: str
    project_id: str
    name: str
    category: str
    connection_type: str
    description: str | None = None
    status: str
    config: dict[str, Any]
    created_at: str
    updated_at: str


class ConnectionTestResponse(BaseModel):
    healthy: bool
    message: str
    latency_ms: int


@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    payload: ConnectionCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ConnectionService, Depends(get_connection_service)],
) -> dict:
    try:
        connection = await service.create_connection(
            project_id=payload.project_id,
            name=payload.name,
            category=payload.category,
            connection_type=payload.connection_type,
            config=payload.config,
            user_id=current_user.user_id,
            description=payload.description,
        )
        return connection
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("/", response_model=dict)
async def list_connections(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ConnectionService, Depends(get_connection_service)],
    project_id: str = Query(..., description="Project ID to filter connections"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> dict:
    items, total = await service.list_connections_by_project(
        project_id=project_id, offset=offset, limit=limit
    )
    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ConnectionService, Depends(get_connection_service)],
) -> dict:
    try:
        return await service.get_connection(connection_id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.post("/{connection_id}/test", response_model=ConnectionTestResponse)
async def test_connection_health(
    connection_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[ConnectionService, Depends(get_connection_service)],
) -> dict:
    try:
        return await service.test_connection_health(connection_id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
