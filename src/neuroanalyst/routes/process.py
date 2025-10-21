"""
Process Routes

This module contains the API endpoints for NeuProcess operations.
"""
from ..models import (
    NeuProcess,
    NeuProcessDir,
    NeuProcessDirConfig,
    NeuProcessLogic
)
from ..utils.constants import PATHS

from typing import Literal, Optional, List, Dict, Any
from pathlib import Path
import shutil

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Body
from pydantic import BaseModel, Field

# Router definition
router = APIRouter(
    prefix="/process",
    tags=["process"],
)
    
class ProcessDirRequest(BaseModel):
    """
    Request model for creating a NeuProcessDir
    """
    logic_name: Optional[str] = Field(None, description="ID of the NeuProcessLogic to use")
    config: Optional[NeuProcessDirConfig | dict] = Field(None, description="Configuration for the NeuProcessDir")
    generate: bool = Field(False, description="Whether to generate the process directory after creation")
    
class ProcessRequest(BaseModel):
    """
    Request model for creating a NeuProcess
    """
    process_id: str = Field(..., description="ID of the NeuProcessDir to create the process from")
    image_or_venv: Literal["image", "venv"] = Field(
        "image",
        description="Whether to create a container image or virtual environment"
    )
    scheduler: Literal["slurm", "pbs", "lsf", "local"] | None = Field(
        None,
        description="Scheduler to use for building the process"
    )
    build: bool = Field(
        False,
        description="Whether to build the process after creation"
    )

class ProcessResponse(BaseModel):
    """
    Response model for Process operations
    """
    id: str = Field(..., description="ID of the created resource")
    name: str = Field(..., description="Name of the resource")
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Descriptive message about the operation")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data if applicable")

# Logic endpoints have been moved to the logic router

@router.post("/dir", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
async def create_process_dir(request: ProcessDirRequest):
    """
    Create a new NeuProcessDir from either a NeuProcessLogic or provided scripts.
    """
    try:
        config: NeuProcessDirConfig = NeuProcessDirConfig.model_validate(request.config) if request.config else NeuProcessDirConfig()
        
        logic: NeuProcessLogic = NeuProcessLogic.from_func_name(request.logic_name)
        process_dir: NeuProcessDir = NeuProcessDir.from_logic(logic, config=config)
        
        if request.generate:
            process_dir.generate()
        
        return {
            "id": process_dir.process_id,
            "name": process_dir.process_name,
            "status": "created" if request.generate else "initialized",
            "message": f"NeuProcessDir {process_dir.process_id} created successfully",
            "data": {
                "path": str(process_dir.working_dir),
                "dir": process_dir.model_dump()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create NeuProcessDir: {str(e)}"
        )

@router.post("/", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
async def build_process(request: ProcessRequest):
    """
    Create a new NeuProcess from a NeuProcessDir.
    """
    try:
        process: NeuProcess = NeuProcess.from_process_id(request.process_id)
        if request.build:
            if request.image_or_venv == "image":
                image_path, job_id = process.build_singularity_image(scheduler=request.scheduler)
            elif request.image_or_venv == "venv":
                venv_path, job_id = process.create_virtual_env(scheduler=request.scheduler)
            data = {
                "image_path": str(image_path) if request.image_or_venv == "image" else None,
                "venv_path": str(venv_path) if request.image_or_venv == "venv" else None,
                "job_id": job_id if job_id else None
            }
        else:
            job_id = None
            data = {}
        return {
            "id": process.process_id,
            "name": process.process_name,
            "status": "building" if job_id else "ready",
            "message": f"NeuProcess {process.process_id} build initiated successfully" if job_id else f"NeuProcess {process.process_id} built successfully",
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create NeuProcess: {str(e)}"
        )

@router.get("/id/{process_id}", response_model=NeuProcess)
async def get_process(process_id: str):
    """
    Get information about a specific NeuProcess.
    """
    try:
        process: NeuProcess = NeuProcess.from_process_id(process_id)
        return process
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process {process_id} not found: {str(e)}"
        )

@router.get("/", response_model=List[NeuProcess] | List[str])
async def list_processes(id_only: bool = False):
    """
    List all available NeuProcesses.
    """
    try:
        process_ids: list[str] = [subdir.name for subdir in PATHS.workdir.iterdir() if subdir.is_dir()]
        if id_only:
            return [NeuProcess.from_process_id(pid).process_id for pid in process_ids]
        return [NeuProcess.from_process_id(pid) for pid in process_ids]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list processes: {str(e)}"
        )

@router.get("/base-images", response_model=List[str])
async def get_available_base_images() -> List[str]:
    """
    Get a list of available base images for process creation.
    """
    try:
        base_images_path = PATHS.base_images
        if not base_images_path.exists():
            return []
        images = [str(item) for item in base_images_path.iterdir() if item.is_file() and item.suffix in {".sif"}]
        return images
    except Exception as e:
        print(f"Error retrieving base images: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving base images: {str(e)}"
        )