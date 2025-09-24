"""
NeuroAnalyst NeuProcessDir Router

This module defines the FastAPI router for the NeuProcessDir endpoints.
It provides endpoints to create and manage NeuProcessDir instances.
"""

from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import json
from pathlib import Path as PathLib

from ..models.process.dir.core import NeuProcessDir, NeuProcessDirConfig
from ..models.process.logic.core import NeuProcessLogic
from ..models.database.mongo_client import MongoDBClient
from ..models.database.collections import CollectionNames
from .dependencies import get_db_client
from ..utils.constants import NeuroAnalystPaths

# Create router
router = APIRouter()


class BindPath(BaseModel):
    """Model for a bind path definition."""
    name: str
    description: str
    required: bool = True


class EnvironmentVariable(BaseModel):
    """Model for an environment variable definition."""
    name: str
    description: str
    required: bool = True


class CreateDirFromLogicRequest(BaseModel):
    """Request model for creating a NeuProcessDir from NeuProcessLogic."""
    logic_model: Dict[str, Any]
    name: str
    description: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None
    base_image: Optional[str] = None
    system_packages: Optional[List[str]] = None
    python_packages: Optional[List[str]] = None
    bind_paths: Optional[List[BindPath]] = None
    environment_variables: Optional[List[EnvironmentVariable]] = None


@router.post("/create/logic", response_model=Dict[str, Any])
async def create_dir_from_logic(request: CreateDirFromLogicRequest, db_client: MongoDBClient = Depends(get_db_client)):
    """
    Create a new NeuProcessDir from NeuProcessLogic.
    
    Args:
        request: The request object containing the logic model and directory configuration.
        db_client: MongoDB client dependency
        
    Returns:
        Dict[str, Any]: The created NeuProcessDir details.
    """
    try:
        # Create a logic model from the provided data
        logic = NeuProcessLogic(**request.logic_model)
        
        # Prepare the configuration
        config = NeuProcessDirConfig()
        if request.system_packages:
            config.system_packages = request.system_packages
        
        if request.python_packages:
            config.language_packages = {"python": request.python_packages}
        
        # Create the bind paths
        bind_paths = {}
        if request.bind_paths:
            for bp in request.bind_paths:
                bind_paths[bp.name] = {
                    "description": bp.description,
                    "required": bp.required
                }
        
        # Create the environment variables
        env_vars = {}
        if request.environment_variables:
            for ev in request.environment_variables:
                env_vars[ev.name] = {
                    "description": ev.description,
                    "required": ev.required
                }
        
        # Create the NeuProcessDir
        process_dir = NeuProcessDir.from_logic(
            logic=logic,
            name=request.name,
            description=request.description or "",
            author=request.author or "unknown",
            version=request.version or "0.1.0",
            base_image=request.base_image or "",
            config=config,
            bind_paths=bind_paths,
            environment_variables=env_vars
        )
        
        # Generate the process directory files
        process_dir.generate()
        
        # Save to database if connected
        process_dir_dict = process_dir.model_dump()
        if db_client.is_connected():
            db_client.insert_document(CollectionNames.PROCESS_DIR, process_dir_dict)
        
        result = {
            "status": "success",
            "message": "NeuProcessDir created successfully",
            "process_dir": process_dir_dict
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dir_id}", response_model=Dict[str, Any])
async def get_process_dir(
    dir_id: str = Path(..., title="The ID of the NeuProcessDir to retrieve"),
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Get a specific NeuProcessDir by its ID.
    
    Args:
        dir_id: The ID of the NeuProcessDir to retrieve.
        db_client: MongoDB client dependency.
        
    Returns:
        Dict[str, Any]: The NeuProcessDir details.
    """
    try:
        # Try to get the process dir from database first
        if db_client.is_connected():
            process_dir_data = db_client.find_document(
                CollectionNames.PROCESS_DIR, 
                {"dir_id": dir_id}
            )
            
            if process_dir_data:
                return {
                    "status": "success",
                    "process_dir": process_dir_data
                }
        
        # Fallback to file system
        paths = NeuroAnalystPaths()
        workdir = PathLib(paths.workdir)
        process_dir_path = workdir / dir_id
        
        if not process_dir_path.exists() or not process_dir_path.is_dir():
            # Check if it's a prefixed ID
            if not dir_id.startswith("PR-"):
                process_dir_path = workdir / f"PR-{dir_id}"
            
            if not process_dir_path.exists() or not process_dir_path.is_dir():
                raise HTTPException(
                    status_code=404, 
                    detail=f"NeuProcessDir with ID {dir_id} not found"
                )
        
        # Load model.json
        model_path = process_dir_path / "model.json"
        if not model_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"NeuProcessDir model.json not found for ID {dir_id}"
            )
        
        with open(model_path, "r") as f:
            process_dir_data = json.load(f)
        
        return {
            "status": "success",
            "process_dir": process_dir_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=Dict[str, Any])
async def get_all_process_dirs(
    skip: int = 0,
    limit: int = 10,
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Get a list of all NeuProcessDirs.
    
    Args:
        skip: Number of process dirs to skip.
        limit: Maximum number of process dirs to return.
        db_client: MongoDB client dependency.
        
    Returns:
        Dict[str, Any]: A list of NeuProcessDirs.
    """
    try:
        process_dirs = []
        
        # Query database if connected
        if db_client.is_connected():
            # Get count of all process dirs
            total_count = db_client.count_documents(CollectionNames.PROCESS_DIR, {})
            
            # Get process dirs with pagination
            cursor = db_client.find_documents(
                CollectionNames.PROCESS_DIR, 
                {}, 
                skip=skip, 
                limit=limit
            )
            
            for doc in cursor:
                process_dirs.append({
                    "dir_id": doc.get("dir_id"),
                    "name": doc.get("name", "Unknown"),
                    "description": doc.get("description", ""),
                    "author": doc.get("author", "unknown"),
                    "version": doc.get("version", "0.1.0"),
                    "base_image": doc.get("base_image", ""),
                    "path": doc.get("dir_path", "")
                })
        else:
            # Fallback to file system
            paths = NeuroAnalystPaths()
            workdir = PathLib(paths.workdir)
            
            # Look for process dirs with model.json files
            process_dir_paths = []
            if workdir.exists():
                for item in workdir.iterdir():
                    if item.is_dir() and item.name.startswith("PR-"):
                        model_path = item / "model.json"
                        if model_path.exists():
                            process_dir_paths.append(item)
            
            # Sort and paginate
            process_dir_paths = sorted(process_dir_paths, key=lambda x: x.name)
            process_dir_paths = process_dir_paths[skip:skip + limit]
            
            # Get process dir details
            for path in process_dir_paths:
                model_path = path / "model.json"
                try:
                    with open(model_path, "r") as f:
                        model_data = json.load(f)
                    
                    process_dirs.append({
                        "dir_id": model_data.get("dir_id"),
                        "name": model_data.get("name", "Unknown"),
                        "description": model_data.get("description", ""),
                        "author": model_data.get("author", "unknown"),
                        "version": model_data.get("version", "0.1.0"),
                        "base_image": model_data.get("base_image", ""),
                        "path": str(path)
                    })
                except Exception as e:
                    # Skip invalid model files
                    continue
            
            total_count = len(process_dir_paths)
        
        result = {
            "status": "success",
            "count": total_count,
            "process_dirs": process_dirs
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
