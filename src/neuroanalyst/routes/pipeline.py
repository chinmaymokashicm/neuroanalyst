"""
NeuroAnalyst NeuPipeline Router

This module defines the FastAPI router for the NeuPipeline endpoints.
It provides endpoints to create and manage NeuPipeline instances.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Path
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Literal, Union
import os
import json
from pathlib import Path as PathLib

from ..models.pipeline.core import NeuPipeline, NeuPipelineStep
from ..models.process.exec.core import NeuProcessExec, HPCScheduler
from ..models.about import About
from ..models.database.mongo_client import MongoDBClient
from ..models.database.collections import CollectionNames
from .dependencies import get_db_client
from ..utils.constants import NeuroAnalystPaths

# Create router
router = APIRouter()


class PipelineStep(BaseModel):
    """Model for a pipeline step in a request."""
    step_number: int
    name: str
    description: Optional[str] = None
    process_exec_ids: List[str]


class CreatePipelineRequest(BaseModel):
    """Request model for creating a NeuPipeline."""
    name: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    steps: List[PipelineStep]
    scheduler: Literal["lsf", "slurm", "pbs"] = "lsf"


@router.post("/create", response_model=Dict[str, Any])
async def create_pipeline(request: CreatePipelineRequest, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Create a new NeuPipeline from a list of NeuProcessExec instances.
    
    Args:
        request: The request object containing the pipeline configuration.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: The created NeuPipeline details.
    """
    try:
        # Create the About object
        about = About(
            name=request.name,
            description=request.description,
            version=request.version,
            author=request.author
        )

        # Convert scheduler string to enum
        scheduler_map = {
            "lsf": HPCScheduler.LSF,
            "slurm": HPCScheduler.SLURM,
            "pbs": HPCScheduler.PBS
        }
        scheduler = scheduler_map.get(request.scheduler, HPCScheduler.LSF)
        
        # Process each step and retrieve the NeuProcessExec instances
        pipeline_steps = []
        for step_data in sorted(request.steps, key=lambda x: x.step_number):
            # Fetch process exec objects from database
            process_execs = []
            for exec_id in step_data.process_exec_ids:
                # Try to get the process exec from database
                exec_collection = db_client.get_collection(CollectionNames.EXECUTIONS)
                exec_doc = exec_collection.find_one({"exec_id": exec_id})
                
                if exec_doc:
                    # Create NeuProcessExec from database document
                    process_exec = NeuProcessExec.model_validate(exec_doc)
                    process_execs.append(process_exec)
                else:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"NeuProcessExec with ID {exec_id} not found"
                    )
            
            # Create pipeline step
            pipeline_step = NeuPipelineStep(
                name=step_data.name,
                description=step_data.description,
                process_execs=process_execs
            )
            pipeline_steps.append(pipeline_step)
        
        # Create the pipeline
        pipeline = NeuPipeline(
            about=about,
            steps=pipeline_steps,
            scheduler=scheduler
        )
        
        # Create the pipeline directory and generate script
        pipeline_dir = pipeline.create_pipeline_dir()
        
        # Save to database
        pipeline_dict = json.loads(pipeline.model_dump_json())
        pipeline_collection = db_client.get_collection(CollectionNames.PIPELINES)
        pipeline_collection.insert_one(pipeline_dict)
        
        # Prepare response
        result = {
            "status": "success",
            "message": "NeuPipeline created successfully",
            "pipeline": {
                "id": pipeline.pipeline_id,
                "name": pipeline.about.name,
                "description": pipeline.about.description or "",
                "author": pipeline.about.author or "unknown",
                "version": pipeline.about.version or "0.1.0",
                "steps": [
                    {
                        "step_number": i,
                        "name": step.name,
                        "description": step.description or "",
                        "process_exec_ids": [proc.exec_id for proc in step.process_execs]
                    }
                    for i, step in enumerate(pipeline.steps)
                ],
                "scheduler": pipeline.scheduler.value,
                "script_path": str(pipeline.script_path)
            }
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=Dict[str, Any])
async def get_all_pipelines(
    skip: int = Query(0, description="Number of pipelines to skip"),
    limit: int = Query(10, description="Maximum number of pipelines to return"),
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Get a list of all NeuPipelines.
    
    Args:
        skip: Number of pipelines to skip.
        limit: Maximum number of pipelines to return.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: A list of NeuPipeline instances.
    """
    try:
        # Query database for all pipelines
        pipeline_collection = db_client.get_collection(CollectionNames.PIPELINES)
        
        # Get count of all pipelines
        total_count = pipeline_collection.count_documents({})
        
        # Get pipelines with pagination
        cursor = pipeline_collection.find({}).skip(skip).limit(limit)
        
        # Extract basic information for each pipeline
        pipelines = []
        for doc in cursor:
            step_count = len(doc.get("steps", []))
            pipelines.append({
                "id": doc.get("pipeline_id"),
                "name": doc.get("about", {}).get("name", "Unknown"),
                "description": doc.get("about", {}).get("description", ""),
                "author": doc.get("about", {}).get("author", "Unknown"),
                "version": doc.get("about", {}).get("version", "0.1.0"),
                "scheduler": doc.get("scheduler", "lsf"),
                "step_count": step_count
            })
        
        # Fallback to file system if no pipelines found in database
        if not pipelines:
            paths = NeuroAnalystPaths()
            pipeline_dir = PathLib(paths.pipelines)
            
            if pipeline_dir.exists():
                # Get all pipeline directories
                pipeline_ids = [d.name for d in pipeline_dir.iterdir() if d.is_dir() and (d / "model.json").exists()]
                pipeline_ids = sorted(pipeline_ids)[skip:skip + limit]
                
                # Load pipeline models from files
                for pipeline_id in pipeline_ids:
                    model_path = pipeline_dir / pipeline_id / "model.json"
                    with open(model_path, "r") as f:
                        model_data = json.load(f)
                    
                    about = model_data.get("about", {})
                    step_count = len(model_data.get("steps", []))
                    
                    pipelines.append({
                        "id": pipeline_id,
                        "name": about.get("name", "Unknown"),
                        "description": about.get("description", ""),
                        "author": about.get("author", "Unknown"),
                        "version": about.get("version", "0.1.0"),
                        "scheduler": model_data.get("scheduler", "lsf"),
                        "step_count": step_count
                    })
                
                total_count = len(pipeline_ids)
        
        result = {
            "status": "success",
            "count": total_count,
            "pipelines": pipelines
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pipeline_id}", response_model=Dict[str, Any])
async def get_pipeline(
    pipeline_id: str = Path(..., description="The ID of the pipeline to retrieve"),
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Get details of a specific NeuPipeline.
    
    Args:
        pipeline_id: The ID of the NeuPipeline to get.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: The NeuPipeline details.
    """
    try:
        # Try to find pipeline in database
        pipeline_collection = db_client.get_collection(CollectionNames.PIPELINES)
        pipeline_doc = pipeline_collection.find_one({"pipeline_id": pipeline_id})
        
        if pipeline_doc:
            # Create NeuPipeline from database document
            pipeline = NeuPipeline.model_validate(pipeline_doc)
        else:
            # Try to load from file system
            paths = NeuroAnalystPaths()
            model_path = PathLib(paths.pipelines) / pipeline_id / "model.json"
            
            if not model_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"NeuPipeline with ID {pipeline_id} not found"
                )
            
            try:
                pipeline = NeuPipeline.from_model_file(model_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to load pipeline from file: {str(e)}"
                )
        
        # Prepare response
        result = {
            "status": "success",
            "pipeline": {
                "id": pipeline.pipeline_id,
                "name": pipeline.about.name,
                "description": pipeline.about.description or "",
                "author": pipeline.about.author or "unknown",
                "version": pipeline.about.version or "0.1.0",
                "steps": [
                    {
                        "step_number": i,
                        "name": step.name,
                        "description": step.description or "",
                        "process_exec_ids": [proc.exec_id for proc in step.process_execs]
                    }
                    for i, step in enumerate(pipeline.steps)
                ],
                "scheduler": pipeline.scheduler.value,
                "script_path": str(pipeline.script_path)
            }
        }
        
        # Try to get pipeline status if available
        try:
            status_path = PathLib(paths.pipelines) / pipeline_id / "status.json"
            if status_path.exists():
                with open(status_path, "r") as f:
                    status_data = json.load(f)
                result["pipeline"]["status"] = status_data
        except Exception:
            pass  # Ignore status loading errors
        
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{pipeline_id}", response_model=Dict[str, Any])
async def delete_pipeline(
    pipeline_id: str = Path(..., description="The ID of the pipeline to delete"),
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Delete a specific NeuPipeline and its associated directory.
    
    Args:
        pipeline_id: The ID of the NeuPipeline to delete.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: The deletion status.
    """
    try:
        # Check if the pipeline exists in the database
        pipeline_collection = db_client.get_collection(CollectionNames.PIPELINES)
        pipeline_doc = pipeline_collection.find_one({"pipeline_id": pipeline_id})
        
        # Delete from database if it exists
        if pipeline_doc:
            pipeline_collection.delete_one({"pipeline_id": pipeline_id})
        
        # Delete from file system if directory exists
        paths = NeuroAnalystPaths()
        pipeline_dir = PathLib(paths.pipelines) / pipeline_id
        
        if pipeline_dir.exists():
            # Recursive delete of pipeline directory
            import shutil
            shutil.rmtree(pipeline_dir)
        
        # Return success response
        result = {
            "status": "success",
            "message": f"NeuPipeline {pipeline_id} deleted successfully"
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{pipeline_id}/execute", response_model=Dict[str, Any])
async def execute_pipeline(
    pipeline_id: str = Path(..., description="The ID of the pipeline to execute"),
    resume: bool = Query(False, description="Whether to resume from the last successful step"),
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Execute a specific NeuPipeline.
    
    Args:
        pipeline_id: The ID of the NeuPipeline to execute.
        resume: If True, resume execution from the last successful step.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: The execution status.
    """
    try:
        # Try to find pipeline in database
        pipeline_collection = db_client.get_collection(CollectionNames.PIPELINES)
        pipeline_doc = pipeline_collection.find_one({"pipeline_id": pipeline_id})
        
        if pipeline_doc:
            # Create NeuPipeline from database document
            pipeline = NeuPipeline.model_validate(pipeline_doc)
        else:
            # Try to load from file system
            paths = NeuroAnalystPaths()
            model_path = PathLib(paths.pipelines) / pipeline_id / "model.json"
            
            if not model_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"NeuPipeline with ID {pipeline_id} not found"
                )
            
            try:
                pipeline = NeuPipeline.from_model_file(model_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to load pipeline from file: {str(e)}"
                )
        
        # Execute the pipeline
        result_message = pipeline.execute_via_bash(resume=resume)
        
        # Return execution status
        result = {
            "status": "success",
            "message": "Pipeline execution started",
            "pipeline_id": pipeline_id,
            "execution_result": result_message
        }
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pipeline_id}/status", response_model=Dict[str, Any])
async def get_pipeline_status(
    pipeline_id: str = Path(..., description="The ID of the pipeline to get status for"),
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Get the current status of a specific NeuPipeline.
    
    Args:
        pipeline_id: The ID of the NeuPipeline to get status for.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: The pipeline status.
    """
    try:
        # Try to find pipeline in database
        pipeline_collection = db_client.get_collection(CollectionNames.PIPELINES)
        pipeline_doc = pipeline_collection.find_one({"pipeline_id": pipeline_id})
        
        if pipeline_doc:
            # Create NeuPipeline from database document
            pipeline = NeuPipeline.model_validate(pipeline_doc)
        else:
            # Try to load from file system
            paths = NeuroAnalystPaths()
            model_path = PathLib(paths.pipelines) / pipeline_id / "model.json"
            
            if not model_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"NeuPipeline with ID {pipeline_id} not found"
                )
            
            try:
                pipeline = NeuPipeline.from_model_file(model_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to load pipeline from file: {str(e)}"
                )
        
        # Get the pipeline status
        try:
            status_data = pipeline.get_pipeline_status()
            
            result = {
                "status": "success",
                "pipeline_id": pipeline_id,
                "pipeline_status": status_data
            }
            return result
        except FileNotFoundError:
            result = {
                "status": "success",
                "pipeline_id": pipeline_id,
                "pipeline_status": {
                    "status": "not_started",
                    "message": "Pipeline execution has not started yet"
                }
            }
            return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
