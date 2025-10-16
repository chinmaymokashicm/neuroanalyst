"""
NeuroAnalyst File Router

This module defines the FastAPI router for the File endpoints.
It provides endpoints to access files in the NeuroAnalyst environment.
"""

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse
import os
from pathlib import Path as PathLib
import mimetypes
import json

from ..utils.constants import NeuroAnalystPaths

# Create router
router = APIRouter()


@router.get("/content/{path:path}", response_class=JSONResponse)
async def get_file_contents(
    path: str = Path(..., description="The relative path to the file from the NeuroAnalyst root directory")
):
    """
    Get the contents of a file given its relative path from the NeuroAnalyst root directory.
    
    Args:
        path: The relative path to the file.
        
    Returns:
        JSONResponse: The contents of the file.
    """
    try:
        # Parse the path to extract the root directory and the relative path
        paths = NeuroAnalystPaths()
        
        # Get the first part of the path which should be the root directory name
        parts = path.strip('/').split('/', 1)
        if len(parts) < 2:
            raise HTTPException(
                status_code=400,
                detail="Invalid path format. Path should be in the format /$ROOT_DIR/relative_path"
            )
        
        root_dir_name, relative_path = parts
        
        # Map the root directory name to the actual path
        root_dir_map = {
            "datasets": paths.datasets,
            "workdir": paths.workdir,
            "logs": paths.logs,
            "images": paths.process_images,
            "reports": paths.reports,
            "venvs": f"{paths.workdir}/venvs",
            "pipelines": paths.pipelines,
            "templates": f"{paths.logs}/templates"
        }
        
        if root_dir_name not in root_dir_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid root directory: {root_dir_name}. Valid options are: {', '.join(root_dir_map.keys())}"
            )
        
        # Construct the full path
        root_dir = root_dir_map[root_dir_name]
        full_path = PathLib(root_dir) / relative_path
        
        # Check if the file exists
        if not full_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {path}"
            )
        
        # Check if it's a file
        if not full_path.is_file():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a file: {path}"
            )
        
        # Check if the file is too large (>10MB)
        if full_path.stat().st_size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File is too large to display (>10MB). Use download parameter to download the file."
            )
        
        # Determine file type and set Content-Type header accordingly
        content_type, _ = mimetypes.guess_type(str(full_path))
        if content_type is None:
            content_type = "text/plain"
        
        # Read and return the file contents
        with open(full_path, "r") as f:
            contents = f.read()
        
        return {
            "status": "success",
            "content": contents,
            "path": path,
            "content_type": content_type
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{path:path}")
async def download_file(
    path: str = Path(..., description="The relative path to the file from the NeuroAnalyst root directory")
):
    """
    Download a file given its relative path from the NeuroAnalyst root directory.
    
    Args:
        path: The relative path to the file.
        
    Returns:
        FileResponse: The file for download.
    """
    try:
        # Parse the path to extract the root directory and the relative path
        paths = NeuroAnalystPaths()
        
        # Get the first part of the path which should be the root directory name
        parts = path.strip('/').split('/', 1)
        if len(parts) < 2:
            raise HTTPException(
                status_code=400,
                detail="Invalid path format. Path should be in the format /$ROOT_DIR/relative_path"
            )
        
        root_dir_name, relative_path = parts
        
        # Map the root directory name to the actual path
        root_dir_map = {
            "datasets": paths.datasets,
            "workdir": paths.workdir,
            "logs": paths.logs,
            "images": paths.process_images,
            "reports": paths.reports,
            "venvs": f"{paths.workdir}/venvs",
            "pipelines": paths.pipelines,
            "templates": f"{paths.logs}/templates"
        }
        
        if root_dir_name not in root_dir_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid root directory: {root_dir_name}. Valid options are: {', '.join(root_dir_map.keys())}"
            )
        
        # Construct the full path
        root_dir = root_dir_map[root_dir_name]
        full_path = PathLib(root_dir) / relative_path
        
        # Check if the file exists
        if not full_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {path}"
            )
        
        # Check if it's a file
        if not full_path.is_file():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a file: {path}"
            )
        
        # Return the file as a download
        return FileResponse(
            path=str(full_path), 
            filename=full_path.name,
            media_type="application/octet-stream"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dir/{path:path}")
async def list_directory(
    path: str = Path(..., description="The relative path to the directory from the NeuroAnalyst root directory")
):
    """
    List the contents of a directory given its relative path from the NeuroAnalyst root directory.
    
    Args:
        path: The relative path to the directory.
        
    Returns:
        Dict: The directory contents.
    """
    try:
        # Parse the path to extract the root directory and the relative path
        paths = NeuroAnalystPaths()
        
        # Get the first part of the path which should be the root directory name
        parts = path.strip('/').split('/', 1)
        root_dir_name = parts[0]
        relative_path = parts[1] if len(parts) > 1 else ""
        
        # Map the root directory name to the actual path
        root_dir_map = {
            "datasets": paths.datasets,
            "workdir": paths.workdir,
            "logs": paths.logs,
            "images": paths.process_images,
            "reports": paths.reports,
            "venvs": f"{paths.workdir}/venvs",
            "pipelines": paths.pipelines,
            "templates": f"{paths.logs}/templates"
        }
        
        if root_dir_name not in root_dir_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid root directory: {root_dir_name}. Valid options are: {', '.join(root_dir_map.keys())}"
            )
        
        # Construct the full path
        root_dir = root_dir_map[root_dir_name]
        full_path = PathLib(root_dir) / relative_path
        
        # Check if the directory exists
        if not full_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Directory not found: {path}"
            )
        
        # Check if it's a directory
        if not full_path.is_dir():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a directory: {path}"
            )
        
        # List directory contents
        items = []
        for item in full_path.iterdir():
            item_type = "directory" if item.is_dir() else "file"
            item_size = item.stat().st_size if item.is_file() else None
            item_modified = item.stat().st_mtime
            
            items.append({
                "name": item.name,
                "path": str(item.relative_to(PathLib(root_dir))),
                "type": item_type,
                "size": item_size,
                "modified": item_modified
            })
        
        # Sort items (directories first, then alphabetically)
        items.sort(key=lambda x: (0 if x["type"] == "directory" else 1, x["name"]))
        
        return {
            "status": "success",
            "path": path,
            "items": items
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
