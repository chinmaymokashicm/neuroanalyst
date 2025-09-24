"""
NeuroAnalyst NeuProcess Router

This module defines the FastAPI router for the NeuProcess endpoints.
It provides endpoints to create and manage NeuProcess instances.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import shutil

from ..models.process.process.core import NeuProcess
from ..models.process.dir.core import NeuProcessDir
from ..models.database.mongo_client import MongoDBClient
from ..models.database.collections import CollectionNames
from .dependencies import get_db_client
from ..utils.constants import NeuroAnalystPaths

# Initialize paths
PATHS = NeuroAnalystPaths()

# Create router
router = APIRouter()


class CreateProcessRequest(BaseModel):
    """Request model for creating a NeuProcess from a NeuProcessDir."""
    process_dir_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None


@router.get("/all", response_model=Dict[str, Any])
async def get_all_processes(
    skip: int = Query(0, description="Number of processes to skip"),
    limit: int = Query(10, description="Maximum number of processes to return"),
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Get a list of all NeuProcesses.
    
    Args:
        skip: Number of processes to skip.
        limit: Maximum number of processes to return.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: A list of NeuProcess instances.
    """
    try:
        # Fetch processes from database if connected
        processes = []
        if db_client.is_connected():
            cursor = db_client.find_documents(
                CollectionNames.PROCESS, 
                query={}, 
                skip=skip, 
                limit=limit
            )
            processes = list(cursor)
        else:
            # If database not connected, list processes from filesystem
            workdir = PATHS.workdir
            image_dir = PATHS.images
            
            # List all process directories
            process_dirs = []
            if os.path.exists(workdir):
                process_dirs = [d for d in os.listdir(workdir) if d.startswith("PR-")]
            
            # List all process images
            process_images = []
            if os.path.exists(image_dir):
                process_images = [f for f in os.listdir(image_dir) if f.endswith(".sif")]
            
            # Create process objects
            for i, dir_name in enumerate(process_dirs[skip:skip+limit]):
                process_id = dir_name
                process_dir_path = os.path.join(workdir, dir_name)
                
                # Check if model.json exists
                model_file = os.path.join(process_dir_path, "model.json")
                if os.path.exists(model_file):
                    try:
                        # Load NeuProcessDir from model.json
                        process_dir = NeuProcessDir.from_json(model_file)
                        
                        # Check if image exists
                        image_path = ""
                        image_file = f"{process_id}.sif"
                        if image_file in process_images:
                            image_path = os.path.join(image_dir, image_file)
                        
                        # Create process object
                        process = {
                            "process_id": process_id,
                            "name": process_dir.name,
                            "description": process_dir.description,
                            "author": process_dir.author,
                            "version": process_dir.version,
                            "image_path": image_path,
                            "process_dir_id": process_dir.dir_id
                        }
                        processes.append(process)
                    except Exception as e:
                        # Skip invalid process dirs
                        continue
        
        result = {
            "status": "success",
            "count": len(processes),
            "processes": processes
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{process_id}", response_model=Dict[str, Any])
async def get_process(process_id: str, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Get details of a specific NeuProcess.
    
    Args:
        process_id: The ID of the NeuProcess to get.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: The NeuProcess details.
    """
    try:
        # Try to fetch from database first
        process_data = None
        if db_client.is_connected():
            process_data = db_client.find_one_document(
                CollectionNames.PROCESS, 
                query={"process_id": process_id}
            )
        
        # If not found in database, try to load from filesystem
        if not process_data:
            try:
                # Try to find the process directory
                process_dir_path = os.path.join(PATHS.workdir, process_id)
                if os.path.exists(process_dir_path):
                    # Load NeuProcessDir from model.json
                    model_file = os.path.join(process_dir_path, "model.json")
                    if os.path.exists(model_file):
                        process_dir = NeuProcessDir.from_json(model_file)
                        
                        # Check if image exists
                        image_path = ""
                        image_file = f"{process_id}.sif"
                        if os.path.exists(os.path.join(PATHS.images, image_file)):
                            image_path = os.path.join(PATHS.images, image_file)
                        
                        # Create NeuProcess
                        process = NeuProcess(
                            process_id=process_id,
                            process_dir=process_dir,
                            image_path=image_path
                        )
                        
                        # Convert to dict
                        process_data = process.model_dump()
                    else:
                        raise HTTPException(status_code=404, detail=f"Process {process_id} model file not found")
                else:
                    raise HTTPException(status_code=404, detail=f"Process {process_id} directory not found")
            except Exception as e:
                raise HTTPException(status_code=404, detail=f"Process {process_id} not found: {str(e)}")
        
        # Return the process data
        result = {
            "status": "success",
            "process": process_data
        }
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", response_model=Dict[str, Any])
async def create_process(request: CreateProcessRequest, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Create a new NeuProcess from a NeuProcessDir.
    
    Args:
        request: The request object containing the process configuration.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: The created NeuProcess details.
    """
    try:
        # Try to find the NeuProcessDir
        process_dir = None
        
        # Check if it exists in the database
        process_dir_data = None
        if db_client.is_connected():
            process_dir_data = db_client.find_one_document(
                CollectionNames.PROCESS_DIR, 
                query={"dir_id": request.process_dir_id}
            )
        
        # If found in database, load from data
        if process_dir_data:
            process_dir = NeuProcessDir(**process_dir_data)
        else:
            # Try to find it in the filesystem
            process_dir_path = os.path.join(PATHS.workdir, request.process_dir_id)
            if os.path.exists(process_dir_path):
                # Load from model.json
                model_file = os.path.join(process_dir_path, "model.json")
                if os.path.exists(model_file):
                    process_dir = NeuProcessDir.from_json(model_file)
                else:
                    raise HTTPException(status_code=404, detail=f"ProcessDir {request.process_dir_id} model file not found")
            else:
                raise HTTPException(status_code=404, detail=f"ProcessDir {request.process_dir_id} not found")
        
        # Create the NeuProcess
        process = NeuProcess(
            process_dir=process_dir,
            name=request.name or process_dir.name,
            description=request.description or process_dir.description,
            author=request.author or process_dir.author,
            version=request.version or process_dir.version
        )
        
        # Save to database if connected
        process_dict = process.model_dump()
        if db_client.is_connected():
            db_client.insert_document(CollectionNames.PROCESS, process_dict)
        
        result = {
            "status": "success",
            "message": "NeuProcess created successfully",
            "process": process_dict
        }
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{process_id}/build_image", response_model=Dict[str, Any])
async def build_image(process_id: str, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Build the Singularity image for a specific NeuProcess.
    
    Args:
        process_id: The ID of the NeuProcess to build the image for.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: The build status and details.
    """
    try:
        # Get the process
        process = None
        
        # Try to fetch from database
        process_data = None
        if db_client.is_connected():
            process_data = db_client.find_one_document(
                CollectionNames.PROCESS, 
                query={"process_id": process_id}
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
                process_dir_path = os.path.join(PATHS.workdir, process_id)
                if os.path.exists(process_dir_path):
                    # Load NeuProcessDir from model.json
                    model_file = os.path.join(process_dir_path, "model.json")
                    if os.path.exists(model_file):
                        process_dir = NeuProcessDir.from_json(model_file)
                        
                        # Create NeuProcess
                        process = NeuProcess(
                            process_id=process_id,
                            process_dir=process_dir
                        )
                    else:
                        raise HTTPException(status_code=404, detail=f"Process {process_id} model file not found")
                else:
                    raise HTTPException(status_code=404, detail=f"Process {process_id} directory not found")
            except Exception as e:
                raise HTTPException(status_code=404, detail=f"Process {process_id} not found: {str(e)}")
        
        # Build the image
        image_path = process.build_image()
        
        # Update the process data in database if connected
        if db_client.is_connected():
            db_client.update_document(
                CollectionNames.PROCESS,
                query={"process_id": process_id},
                update={"$set": {"image_path": str(image_path)}}
            )
        
        result = {
            "status": "success",
            "message": "Singularity image built successfully",
            "image_path": str(image_path)
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{process_id}/create_venv", response_model=Dict[str, Any])
async def create_venv(process_id: str, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Create the virtual environment for a specific NeuProcess.
    
    Args:
        process_id: The ID of the NeuProcess to create the venv for.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: The venv creation status and details.
    """
    try:
        # Get the process (using similar logic as build_image)
        process = None
        
        # Try to fetch from database
        process_data = None
        if db_client.is_connected():
            process_data = db_client.find_one_document(
                CollectionNames.PROCESS, 
                query={"process_id": process_id}
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
                process_dir_path = os.path.join(PATHS.workdir, process_id)
                if os.path.exists(process_dir_path):
                    # Load NeuProcessDir from model.json
                    model_file = os.path.join(process_dir_path, "model.json")
                    if os.path.exists(model_file):
                        process_dir = NeuProcessDir.from_json(model_file)
                        
                        # Create NeuProcess
                        process = NeuProcess(
                            process_id=process_id,
                            process_dir=process_dir
                        )
                    else:
                        raise HTTPException(status_code=404, detail=f"Process {process_id} model file not found")
                else:
                    raise HTTPException(status_code=404, detail=f"Process {process_id} directory not found")
            except Exception as e:
                raise HTTPException(status_code=404, detail=f"Process {process_id} not found: {str(e)}")
        
        # Create the virtual environment
        venv_path = process.create_venv()
        
        # Update the process data in database if connected
        if db_client.is_connected():
            db_client.update_document(
                CollectionNames.PROCESS,
                query={"process_id": process_id},
                update={"$set": {"venv_path": str(venv_path)}}
            )
        
        result = {
            "status": "success",
            "message": "Virtual environment created successfully",
            "venv_path": str(venv_path)
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{process_id}", response_model=Dict[str, Any])
async def delete_process(process_id: str, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Delete a specific NeuProcess and its associated image and venv.
    
    Args:
        process_id: The ID of the NeuProcess to delete.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: The deletion status.
    """
    try:
        # Try to fetch from database
        process_data = None
        if db_client.is_connected():
            process_data = db_client.find_one_document(
                CollectionNames.PROCESS, 
                query={"process_id": process_id}
            )
        
        # Delete from database if exists
        if process_data and db_client.is_connected():
            db_client.delete_document(
                CollectionNames.PROCESS,
                query={"process_id": process_id}
            )
        
        # Check if image exists and delete it
        image_path = os.path.join(PATHS.images, f"{process_id}.sif")
        if os.path.exists(image_path):
            os.remove(image_path)
        
        # Check if venv exists and delete it
        venv_path = os.path.join(PATHS.venvs, process_id)
        if os.path.exists(venv_path):
            shutil.rmtree(venv_path)
        
        result = {
            "status": "success",
            "message": f"NeuProcess {process_id} deleted successfully"
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
