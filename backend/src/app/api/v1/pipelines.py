"""
API v1 — Pipeline Routes
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from app.api.schemas import (
    ExecutionResponse,
    PaginatedResponse,
    PipelineCreateRequest,
    PipelineResponse,
    PipelineUpdateRequest,
)
from app.application.exporters.airflow_exporter import AirflowDAGExporter
from app.application.exporters.dagster_exporter import DagsterExporter
from app.application.exporters.dbt_exporter import DBTExporter
from app.application.exporters.prefect_exporter import PrefectExporter
from app.application.services.pipeline_service import PipelineService
from app.dependencies import CurrentUser, get_current_user, get_pipeline_service

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@router.get("/{pipeline_id}/export/dbt", summary="Export Pipeline as dbt Project Models")
async def export_dbt_models(
    pipeline_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> dict:
    pipeline = await service.get_pipeline(pipeline_id, current_user.user_id, current_user.role)
    exporter = DBTExporter()
    return exporter.export_dbt_project(pipeline)


@router.get("/{pipeline_id}/export/dagster", summary="Export Pipeline as Dagster Script (.py)")
async def export_dagster_job(
    pipeline_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> Response:
    pipeline = await service.get_pipeline(pipeline_id, current_user.user_id, current_user.role)
    exporter = DagsterExporter()
    code = exporter.export_dagster_code(pipeline)
    return Response(
        content=code,
        media_type="text/x-python",
        headers={"Content-Disposition": f"attachment; filename=dagster_job_{pipeline_id[:8]}.py"},
    )



def pipeline_to_response(p) -> dict:
    return {
        "id": str(p.id),
        "project_id": str(p.project_id),
        "name": p.name,
        "description": p.description,
        "status": p.status.value,
        "version": p.version,
        "spec": p.spec,
        "created_by": str(p.created_by) if p.created_by else None,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


def _execution_to_response(e) -> dict:
    return {
        "id": str(e.id),
        "pipeline_id": str(e.pipeline_id),
        "status": e.status.value,
        "started_at": e.started_at,
        "completed_at": e.completed_at,
        "logs": e.logs,
        "metrics": e.metrics,
        "error": e.error,
        "triggered_by": str(e.triggered_by) if e.triggered_by else None,
        "created_at": e.created_at,
    }


@router.post("/", response_model=PipelineResponse, status_code=201)
async def create_pipeline(
    body: PipelineCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> dict:
    pipeline = await service.create_pipeline(
        project_id=body.project_id,
        name=body.name,
        description=body.description,
        user_id=current_user.user_id,
        user_role=current_user.role,
        spec=body.spec,
    )
    return pipeline_to_response(pipeline)


@router.get("/", response_model=PaginatedResponse)
async def list_pipelines(
    project_id: str = Query(..., description="Project ID to list pipelines for"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str | None = Query(None),
    current_user: Annotated[CurrentUser, Depends(get_current_user)] = None,
    service: Annotated[PipelineService, Depends(get_pipeline_service)] = None,
) -> dict:
    pipelines, total = await service.list_pipelines(
        project_id=project_id,
        user_id=current_user.user_id,
        user_role=current_user.role,
        offset=offset,
        limit=limit,
        status=status,
    )
    return {
        "items": [pipeline_to_response(p) for p in pipelines],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> dict:
    pipeline = await service.get_pipeline(pipeline_id, current_user.user_id, current_user.role)
    return pipeline_to_response(pipeline)


@router.patch("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: str,
    body: PipelineUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> dict:
    pipeline = await service.update_pipeline(
        pipeline_id=pipeline_id,
        user_id=current_user.user_id,
        user_role=current_user.role,
        name=body.name,
        description=body.description,
        spec=body.spec,
    )
    return pipeline_to_response(pipeline)


@router.delete("/{pipeline_id}", response_model=PipelineResponse)
async def archive_pipeline(
    pipeline_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> dict:
    pipeline = await service.archive_pipeline(pipeline_id, current_user.user_id, current_user.role)
    return pipeline_to_response(pipeline)


@router.post("/{pipeline_id}/execute", response_model=ExecutionResponse, status_code=201)
async def execute_pipeline(
    pipeline_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> dict:
    execution = await service.execute_pipeline(
        pipeline_id, current_user.user_id, current_user.role
    )
    return _execution_to_response(execution)


@router.get("/{pipeline_id}/history", response_model=PaginatedResponse)
async def get_execution_history(
    pipeline_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> dict:
    executions, total = await service.get_execution_history(
        pipeline_id=pipeline_id,
        user_id=current_user.user_id,
        user_role=current_user.role,
        offset=offset,
        limit=limit,
    )
    return {
        "items": [_execution_to_response(e) for e in executions],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/{pipeline_id}/export/airflow", summary="Export Pipeline as Apache Airflow DAG (.py)")
async def export_airflow_dag(
    pipeline_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> Response:
    pipeline = await service.get_pipeline(pipeline_id, current_user.user_id, current_user.role)
    exporter = AirflowDAGExporter()
    code = exporter.export_dag_code(pipeline)
    return Response(
        content=code,
        media_type="text/x-python",
        headers={"Content-Disposition": f"attachment; filename=airflow_dag_{pipeline_id[:8]}.py"},
    )


@router.get("/{pipeline_id}/export/prefect", summary="Export Pipeline as Prefect Flow Script (.py)")
async def export_prefect_flow(
    pipeline_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> Response:
    pipeline = await service.get_pipeline(pipeline_id, current_user.user_id, current_user.role)
    exporter = PrefectExporter()
    code = exporter.export_flow_code(pipeline)
    return Response(
        content=code,
        media_type="text/x-python",
        headers={"Content-Disposition": f"attachment; filename=prefect_flow_{pipeline_id[:8]}.py"},
    )


from app.application.services.lineage_service import DataLineageService


@router.get("/{pipeline_id}/lineage", summary="Get Column-Level Data Lineage Graph")
async def get_pipeline_lineage(
    pipeline_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> dict:
    pipeline = await service.get_pipeline(pipeline_id, current_user.user_id, current_user.role)
    lineage_service = DataLineageService()
    return lineage_service.generate_lineage(pipeline.spec)
