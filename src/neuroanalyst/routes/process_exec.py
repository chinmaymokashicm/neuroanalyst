"""
NeuroAnalyst NeuProcessExec Router

This module defines the FastAPI router for the NeuProcessExec endpoints.
It provides endpoints to create and manage NeuProcessExec instances.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Literal
import os
import shutil

from ..models.process.exec.core import NeuProcessExec, HPCScheduler
from ..models.process.process.core import NeuProcess
from ..models.process.dir.core import NeuProcessDir, ExecutionMode
from ..models.database.mongo_client import MongoDBClient
from ..models.database.collections import CollectionNames
from .dependencies import get_db_client
from ..utils.constants import NeuroAnalystPaths

# Initialize paths
PATHS = NeuroAnalystPaths()

# Create router
router = APIRouter()


class BindPathValue(BaseModel):
    """Model for a bind path value."""
    name: str
    value: str


class EnvironmentVariableValue(BaseModel):
    """Model for an environment variable value."""
    name: str
    value: str


class CreateProcessExecRequest(BaseModel):
    """Request model for creating a NeuProcessExec."""
    process_id: str
    bind_paths: List[BindPathValue]
    environment_variables: List[EnvironmentVariableValue]
    execution_type: Literal["container", "script"] = "container"
    environment: Literal["hpc", "local"] = "hpc"
    scheduler: Optional[Literal["lsf", "slurm", "pbs"]] = "lsf"


@router.post("/create", response_model=Dict[str, Any])
async def create_process_exec(request: CreateProcessExecRequest, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Create a new NeuProcessExec instance.
    
    Args:
        request: The request object containing the execution configuration.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: The created NeuProcessExec details.
    """
    try:
        # Get the process
        process = None
        
        # Try to fetch from database
        process_data = None
        if db_client.is_connected():
            process_data = db_client.find_one_document(
                CollectionNames.PROCESS, 
                query={"process_id": request.process_id}
            )
        
        # If found in database, load from data
        if process_data:
            # Get the process dir data
            process_dir_id = process_data.get("process_dir", {}).get("dir_id")
            process_dir_data = None
            if process_dir_id:
                process_dir_data = db_client.find_one_document(
                    CollectionNames.PROCESS_DIR,
                    query={"dir_id": process_dir_id}
                )
            
            if process_dir_data:
                process_dir = NeuProcessDir(**process_dir_data)
                process = NeuProcess(**process_data)
            else:
                # Try to load process dir from filesystem
                process_dir_path = os.path.join(PATHS.workdir, process_dir_id)
                if os.path.exists(process_dir_path):
                    model_file = os.path.join(process_dir_path, "model.json")
                    if os.path.exists(model_file):
                        process_dir = NeuProcessDir.from_json(model_file)
                        process = NeuProcess(**process_data)
                    else:
                        raise HTTPException(status_code=404, detail=f"ProcessDir {process_dir_id} model file not found")
                else:
                    raise HTTPException(status_code=404, detail=f"ProcessDir {process_dir_id} not found")
        else:
            # Try to load from filesystem
            try:
                # First get the process directory
                process_dir_path = os.path.join(PATHS.workdir, request.process_id)
                if os.path.exists(process_dir_path):
                    # Load NeuProcessDir from model.json
                    model_file = os.path.join(process_dir_path, "model.json")
                    if os.path.exists(model_file):
                        process_dir = NeuProcessDir.from_json(model_file)
                        
                        # Create NeuProcess
                        process = NeuProcess(
                            process_id=request.process_id,
                            process_dir=process_dir
                        )
                    else:
                        raise HTTPException(status_code=404, detail=f"Process {request.process_id} model file not found")
                else:
                    raise HTTPException(status_code=404, detail=f"Process {request.process_id} directory not found")
            except Exception as e:
                raise HTTPException(status_code=404, detail=f"Process {request.process_id} not found: {str(e)}")
        
        # Prepare bind paths dict
        bind_paths = {}
        for bp in request.bind_paths:
            bind_paths[bp.name] = bp.value
        
        # Prepare environment variables dict
        environment_variables = {}
        for ev in request.environment_variables:
            environment_variables[ev.name] = ev.value
        
        # Set execution mode
        execution_mode = ExecutionMode.CONTAINER if request.execution_type == "container" else ExecutionMode.VENV
        
        # Set scheduler
        scheduler = HPCScheduler.LSF
        if request.scheduler == "slurm":
            scheduler = HPCScheduler.SLURM
        elif request.scheduler == "pbs":
            scheduler = HPCScheduler.PBS
        elif request.scheduler == "local" or request.environment == "local":
            scheduler = HPCScheduler.LOCAL
        
        # Create the NeuProcessExec
        process_exec = NeuProcessExec(
            process=process,
            bind_paths=bind_paths,
            environment_variables=environment_variables,
            execution_mode=execution_mode,
            scheduler=scheduler
        )
        
        # Save to database if connected
        process_exec_dict = process_exec.model_dump()
        if db_client.is_connected():
            db_client.insert_document(CollectionNames.PROCESS_EXEC, process_exec_dict)
        
        result = {
            "status": "success",
            "message": "NeuProcessExec created successfully",
            "process_exec": process_exec_dict
        }
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{exec_id}", response_model=Dict[str, Any])
async def get_process_exec(exec_id: str, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Get details of a specific NeuProcessExec.
    
    Args:
        exec_id: The ID of the NeuProcessExec to get.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: The NeuProcessExec details.
    """
    try:
        # Try to fetch from database
        process_exec_data = None
        if db_client.is_connected():
            process_exec_data = db_client.find_one_document(
                CollectionNames.PROCESS_EXEC, 
                query={"exec_id": exec_id}
            )
        
        # If found in database, return it
        if process_exec_data:
            result = {
                "status": "success",
                "process_exec": process_exec_data
            }
            return result
        
        # If not found in database, try to load from filesystem
        process_exec_path = os.path.join(PATHS.process_execs, exec_id)
        if os.path.exists(process_exec_path):
            model_file = os.path.join(process_exec_path, "model.json")
            if os.path.exists(model_file):
                process_exec = NeuProcessExec.from_json(model_file)
                result = {
                    "status": "success",
                    "process_exec": process_exec.model_dump()
                }
                return result
            else:
                raise HTTPException(status_code=404, detail=f"ProcessExec {exec_id} model file not found")
        else:
            raise HTTPException(status_code=404, detail=f"ProcessExec {exec_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{exec_id}/generate_command", response_model=Dict[str, Any])
async def generate_command(exec_id: str, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Generate the execution command for a specific NeuProcessExec.
    
    Args:
        exec_id: The ID of the NeuProcessExec to generate the command for.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: The generated command.
    """
    try:
        # Get the process exec
        process_exec = None
        
        # Try to fetch from database
        process_exec_data = None
        if db_client.is_connected():
            process_exec_data = db_client.find_one_document(
                CollectionNames.PROCESS_EXEC, 
                query={"exec_id": exec_id}
            )
        
        # If found in database, load from data
        if process_exec_data:
            process_exec = NeuProcessExec(**process_exec_data)
        else:
            # Try to load from filesystem
            process_exec_path = os.path.join(PATHS.process_execs, exec_id)
            if os.path.exists(process_exec_path):
                model_file = os.path.join(process_exec_path, "model.json")
                if os.path.exists(model_file):
                    process_exec = NeuProcessExec.from_json(model_file)
                else:
                    raise HTTPException(status_code=404, detail=f"ProcessExec {exec_id} model file not found")
            else:
                raise HTTPException(status_code=404, detail=f"ProcessExec {exec_id} not found")
        
        # Generate the command
        command = process_exec.generate_command()
        
        result = {
            "status": "success",
            "message": "Command generated successfully",
            "command": command
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{exec_id}", response_model=Dict[str, Any])
async def delete_process_exec(exec_id: str, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Delete a specific NeuProcessExec.
    
    Args:
        exec_id: The ID of the NeuProcessExec to delete.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: The deletion status.
    """
    try:
        # Try to fetch from database
        if db_client.is_connected():
            db_client.delete_document(
                CollectionNames.PROCESS_EXEC,
                query={"exec_id": exec_id}
            )
        
        # Try to delete from filesystem
        process_exec_path = os.path.join(PATHS.process_execs, exec_id)
        if os.path.exists(process_exec_path):
            shutil.rmtree(process_exec_path)
        
        result = {
            "status": "success",
            "message": f"NeuProcessExec {exec_id} deleted successfully"
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
