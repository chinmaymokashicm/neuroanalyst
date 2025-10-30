"""
Dataset Routes

This module contains the API endpoints for datasets operations.
"""
from ..utils.constants import NeuroAnalystPaths
from ..utils.dir import generate_directory_tree

from typing import Optional, List, Dict, Any
from pathlib import Path
import os
import json
import mimetypes
import shutil

from fastapi import APIRouter, HTTPException, status, Response, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field

# Router definition
router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
)

@router.get("/list", response_model=List[Dict[str, str]])
async def list_datasets(username: Optional[str] = None):
    """
    List all available datasets with their names and paths.
    
    Returns:
        List[Dict[str, str]]: A list of datasets with their names and paths.
    """
    try:
        paths = NeuroAnalystPaths(username=username)
        datasets_path = Path(paths.datasets)
        
        if not datasets_path.exists():
            return []
        
        datasets = []
        for item in datasets_path.iterdir():
            if item.is_dir():
                datasets.append({
                    "name": item.name,
                    "path": str(item.absolute())
                })
        
        return datasets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing datasets: {str(e)}"
        )

@router.get("/tree/{dataset_name}")
async def get_dataset_tree(dataset_name: str, path: Optional[str] = None, username: Optional[str] = None):
    """
    Generate directory tree for a dataset, recursively listing all files and folders.
    
    Args:
        dataset_name (str): Name of the dataset
        path (str, optional): Specific subdirectory path within the dataset. Defaults to None.
    
    Returns:
        Dict: Directory tree with files and folders information.
    """
    try:
        # Get base path for the dataset
        neuroanalyst_paths = NeuroAnalystPaths(username=username)
        dataset_base_path = Path(neuroanalyst_paths.datasets) / dataset_name
        
        if not dataset_base_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_name}' not found"
            )
        
        # If a specific path is provided, use it
        if path:
            target_path = dataset_base_path / path
            if not target_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Path '{path}' not found in dataset '{dataset_name}'"
                )
        else:
            target_path = dataset_base_path
        
        # Generate the directory tree
        result = generate_directory_tree(target_path, dataset_base_path)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating directory tree: {str(e)}"
        )

@router.get("/load")
async def load_dataset_file(file_path: str):
    """
    Load data from a specified file path and return it.
    
    Args:
        file_path (str): Absolute path to the file
    
    Returns:
        Any: The data from the file
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_path}' not found"
            )
        
        # Handle different file types
        suffix = file_path.suffix.lower()
        
        # JSON files
        if suffix == '.json':
            with open(file_path, 'r') as f:
                return json.load(f)
                
        # Text files
        elif suffix in ['.txt', '.csv', '.tsv']:
            with open(file_path, 'r') as f:
                content = f.read()
                return {"content": content}
        
        # Other file types - return basic info
        else:
            file_stat = file_path.stat()
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_stat.st_size,
                "last_modified": file_stat.st_mtime,
                "content_type": "binary",
                "message": "Binary file content not displayed. Use appropriate tools to download and view this file."
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading file: {str(e)}"
        )

@router.get("/file")
async def get_file(file_path: str, download: bool = False, username: Optional[str] = None):
    """
    Serve a file directly through the API.
    
    Args:
        file_path (str): Absolute path to the file
        download (bool): If True, file will be served as an attachment for download
    
    Returns:
        FileResponse: The file served directly to the client
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_path}' not found"
            )
            
        # Ensure the file is within the datasets directory for security
        try:
            neuroanalyst_paths = NeuroAnalystPaths(username=username)
            datasets_path = Path(neuroanalyst_paths.datasets)
            # Check if the file_path is within the datasets directory
            if not str(file_path.absolute()).startswith(str(datasets_path.absolute())):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: File is outside the datasets directory"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot verify file path"
            )
        
        # Get the filename and determine content type
        filename = file_path.name
        media_type, _ = mimetypes.guess_type(filename)
        
        if media_type is None:
            # Default to binary stream if type is unknown
            media_type = "application/octet-stream"
        
        # Return the file as a response
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename,
            # Set as attachment if download is requested
            content_disposition_type="attachment" if download else "inline"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving file: {str(e)}"
        )

@router.get("/stream")
async def stream_file(file_path: str, username: Optional[str] = None):
    """
    Stream a file through the API with chunked transfer.
    This is useful for large files that should be streamed rather than loaded into memory.
    
    Args:
        file_path (str): Absolute path to the file
    
    Returns:
        StreamingResponse: The file streamed directly to the client
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_path}' not found"
            )
            
        # Ensure the file is within the datasets directory for security
        
        neuroanalyst_paths = NeuroAnalystPaths(username=username)
        datasets_path = Path(neuroanalyst_paths.datasets)
        if not str(file_path.absolute()).startswith(str(datasets_path.absolute())):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: File is outside the datasets directory"
            )
        
        # Get the filename and determine content type
        filename = file_path.name
        media_type, _ = mimetypes.guess_type(filename)
        
        if media_type is None:
            media_type = "application/octet-stream"
            
        def file_iterator(file_path, chunk_size=8192):
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    yield chunk
        
        # Create streaming response
        response = StreamingResponse(
            file_iterator(file_path), 
            media_type=media_type
        )
        
        # Set filename for download
        response.headers["Content-Disposition"] = f"inline; filename={filename}"
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming file: {str(e)}"
        )
