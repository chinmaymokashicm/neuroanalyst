"""
Pipeline Routes

This module contains the API endpoints for NeuPipeline operations.
"""
from ..models import About, NeuPipeline
from ..utils.constants import NeuroAnalystPaths
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Body
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

# Router definition
router = APIRouter(
    prefix="/pipeline",
    tags=["pipeline"],
)

# Pydantic models for request/response validation
class ProcessStep(BaseModel):
    """
    Represents a process step in a pipeline
    """
    process_id: str = Field(..., description="ID of the NeuProcess to use in this step")
    name: str = Field(..., description="Name of this step")
    depends_on: List[str] = Field(default_factory=list, description="Names of steps this step depends on")
    bind_paths: Dict[str, str] = Field(default_factory=dict, description="Path bindings for this step")
    env_vars: Dict[str, str] = Field(default_factory=dict, description="Environment variables for this step")

class PipelineRequest(BaseModel):
    """
    Request model for creating a NeuPipeline
    """
    about_pipeline: About = Field(..., description="About information for the pipeline")
    bids_root: str = Field(..., description="BIDS root directory for the pipeline")
    step_defs: list[list[str | list[str]]] = Field(..., description="Definitions of steps in the pipeline. For each step, provide name, description, and list of process IDs.")
    starting_bids_filters: dict = Field(default_factory=dict, description="BIDS filters to apply at the start of the pipeline")
    execution_mode: Literal["venv", "container"] = Field("container", description="Execution mode for the pipeline (e.g., local, lsf, slurm)")
    scheduler: Optional[Literal["slurm", "pbs", "lsf", "local"]] = Field(
        None,
        description="Scheduler to use for the pipeline"
    )
    starting_scope: str = Field("raw", description="Scope for the first step of the pipeline (e.g., raw, derivatives)")

class PipelineResponse(BaseModel):
    """
    Response model for Pipeline operations
    """
    id: str = Field(..., description="ID of the pipeline")
    name: str = Field(..., description="Name of the pipeline")
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Descriptive message about the operation")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data if applicable")

@router.post("/", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(request: PipelineRequest, save: bool = Body(True, description="Whether to save the pipeline after creation")):
    """
    Create a new NeuPipeline.
    """
    try:
        pipeline: NeuPipeline = NeuPipeline.constructor(**request.model_dump())
        pipeline.apply_standard_exec_params()
        missing_configs: dict[str, dict[str, set[str]]] = pipeline.get_missing_configs()
        if save:
            pipeline.create_pipeline_dir()
        return {
            "id": pipeline.pipeline_id,
            "name": pipeline.about.name,
            "status": "created" if not missing_configs else "incomplete",
            "message": "Pipeline created successfully",
            "data": {
                "missing_configs": missing_configs
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pipeline: {str(e)}"
        )

@router.get("/{pipeline_id}", response_model=NeuPipeline)
async def get_pipeline(pipeline_id: str):
    """
    Get information about a specific pipeline.
    """
    try:
        pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id)
        return pipeline
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline {pipeline_id} not found: {str(e)}"
        )

@router.get("/", response_model=List[NeuPipeline])
async def list_pipelines(username: Optional[str] = None):
    """
    List all available pipelines.
    """
    try:
        paths = NeuroAnalystPaths()
        pipeline_dir: Path = paths.pipelines
        pipelines: List[NeuPipeline] = []
        for pipeline_path in pipeline_dir.iterdir():
            if pipeline_path.is_dir():
                try:
                    pipeline = NeuPipeline.from_pipeline_id(pipeline_path.name)
                    pipelines.append(pipeline)
                except Exception:
                    continue
        return pipelines
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list pipelines: {str(e)}"
        )