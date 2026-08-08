"""
API v1 — AI Agent Router

Endpoints for generating and refining data engineering pipelines using AI.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.api.v1.pipelines import PipelineResponse, pipeline_to_response
from app.application.services.agent_service import AgentService
from app.dependencies import CurrentUser, get_agent_service, get_current_user

router = APIRouter(prefix="/agent", tags=["AI Agent"])


class GeneratePipelineRequest(BaseModel):
    project_id: str = Field(..., description="Target project UUID")
    prompt: str = Field(..., min_length=5, description="Natural language pipeline specification")
    pipeline_name: str | None = Field(default=None, description="Optional custom name for the pipeline")


class RefinePipelineRequest(BaseModel):
    pipeline_id: str = Field(..., description="Target pipeline UUID")
    refinement_prompt: str = Field(..., min_length=3, description="Modification request prompt")


@router.post(
    "/generate",
    response_model=PipelineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate ETL/ELT Pipeline with AI Agent",
)
async def generate_pipeline(
    request: GeneratePipelineRequest,
    current_user: CurrentUser = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> Any:
    """
    Generates a production-ready ETL pipeline DAG, transformation code, and configuration
    from a natural language prompt.
    """
    pipeline = await agent_service.generate_pipeline_from_prompt(
        project_id=request.project_id,
        prompt=request.prompt,
        user_id=current_user.user_id,
        user_role=current_user.role,
        pipeline_name=request.pipeline_name,
    )
    return pipeline_to_response(pipeline)


@router.post(
    "/refine",
    response_model=PipelineResponse,
    summary="Refine Existing Pipeline Specification with AI Agent",
)
async def refine_pipeline(
    request: RefinePipelineRequest,
    current_user: CurrentUser = Depends(get_current_user),
    agent_service: AgentService = Depends(get_agent_service),
) -> Any:
    """
    Applies refinement instructions to an existing pipeline specification.
    """
    pipeline = await agent_service.refine_pipeline_spec(
        pipeline_id=request.pipeline_id,
        refinement_prompt=request.refinement_prompt,
        user_id=current_user.user_id,
        user_role=current_user.role,
    )
    return pipeline_to_response(pipeline)
