"""
NeuroAnalyst Dataset Router

This module defines the FastAPI router for the Dataset endpoints.
It provides endpoints to list and filter datasets.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
import os
import json
from pathlib import Path as PathLib
import shutil
from datetime import datetime

from ..models.database.mongo_client import MongoDBClient
from ..models.database.collections import CollectionNames
from .dependencies import get_db_client
from ..utils.constants import NeuroAnalystPaths

# Create router
router = APIRouter()


class BIDSFilter(BaseModel):
    """Model for a BIDS filter."""
    subject: Optional[str] = None
    session: Optional[str] = None
    datatype: Optional[str] = None
    extension: Optional[str] = None
    suffix: Optional[str] = None
    # Add more BIDS entities as needed


class RegisterDatasetRequest(BaseModel):
    """Request model for registering a dataset."""
    name: str
    path: str
    description: Optional[str] = None
    dataset_type: Optional[str] = "bids"  # bids, dicom, nifti, other


def _get_directory_info(path: PathLib, max_depth: int = 2, current_depth: int = 0) -> Dict[str, Any]:
    """
    Get information about a directory, including its children up to a specified depth.
    
    Args:
        path: Path to the directory
        max_depth: Maximum depth to traverse
        current_depth: Current depth of recursion
        
    Returns:
        Dict[str, Any]: Information about the directory
    """
    if not path.exists():
        return {"type": "not_found", "name": path.name}
    
    if path.is_file():
        return {"type": "file", "name": path.name, "size": path.stat().st_size}
    
    result = {
        "type": "directory",
        "name": path.name,
        "size": 0,
        "children": []
    }
    
    # If we've reached the maximum depth, don't recurse further
    if current_depth >= max_depth:
        result["truncated"] = True
        return result
    
    # Get children
    try:
        for child in path.iterdir():
            if child.name.startswith('.'):
                continue  # Skip hidden files
                
            child_info = _get_directory_info(child, max_depth, current_depth + 1)
            result["children"].append(child_info)
            
            # Add file/directory size to total
            if "size" in child_info:
                result["size"] += child_info["size"]
    except (PermissionError, OSError):
        result["error"] = "Permission denied or I/O error"
    
    return result


def _get_dataset_metadata(dataset_path: PathLib) -> Dict[str, Any]:
    """
    Get metadata about a dataset.
    
    Args:
        dataset_path: Path to the dataset
        
    Returns:
        Dict[str, Any]: Metadata about the dataset
    """
    if not dataset_path.exists():
        return {}
    
    # Basic file stats
    file_count = 0
    total_size = 0
    subjects = []
    sessions = []
    datatypes = []
    
    # BIDS specific files
    dataset_description = None
    participants_file = None
    
    # Track BIDS entities
    for root, dirs, files in os.walk(dataset_path):
        root_path = PathLib(root)
        rel_path = root_path.relative_to(dataset_path)
        
        # Count files and add size
        for file in files:
            file_path = root_path / file
            try:
                file_size = file_path.stat().st_size
                total_size += file_size
                file_count += 1
                
                # Check for BIDS metadata files
                if file == "dataset_description.json":
                    try:
                        with open(file_path, "r") as f:
                            dataset_description = json.load(f)
                    except Exception:
                        pass
                elif file == "participants.tsv":
                    participants_file = str(file_path)
            except OSError:
                pass
        
        # Check for BIDS entities in directory names
        for dirname in dirs:
            # Check for subjects
            if dirname.startswith("sub-"):
                subjects.append(dirname)
            # Check for sessions
            elif dirname.startswith("ses-"):
                sessions.append(dirname)
            # Check for common BIDS datatypes
            elif dirname in ["anat", "func", "dwi", "fmap", "pet", "meg", "eeg", "ieeg", "beh"]:
                datatypes.append(dirname)
    
    # Create metadata
    metadata = {
        "file_count": file_count,
        "size": total_size,
        "size_human": f"{total_size / (1024**2):.2f} MB" if total_size < 1024**3 else f"{total_size / (1024**3):.2f} GB"
    }
    
    # Add BIDS specific metadata if available
    if subjects:
        metadata["subjects"] = sorted(list(set(subjects)))
    if sessions:
        metadata["sessions"] = sorted(list(set(sessions)))
    if datatypes:
        metadata["datatypes"] = sorted(list(set(datatypes)))
    if dataset_description:
        metadata["description"] = dataset_description
    if participants_file:
        metadata["participants_file"] = participants_file
    
    return metadata


@router.post("/register", response_model=Dict[str, Any])
async def register_dataset(
    request: RegisterDatasetRequest,
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Register a new dataset in the system.
    
    Args:
        request: The request object containing dataset information.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: The registered dataset details.
    """
    try:
        # Validate that the path exists
        dataset_path = PathLib(request.path)
        if not dataset_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Dataset path does not exist: {request.path}"
            )
        
        # Generate dataset ID
        from ..utils.id_generators import generate_id
        dataset_id = generate_id("dataset_id")
        
        # Get dataset metadata
        metadata = _get_dataset_metadata(dataset_path)
        
        # Create dataset document
        dataset_doc = {
            "dataset_id": dataset_id,
            "name": request.name,
            "path": str(dataset_path),
            "description": request.description,
            "dataset_type": request.dataset_type,
            "metadata": metadata,
            "created_at": datetime.now().isoformat()
        }
        
        # Save to database
        dataset_collection = db_client.get_collection(CollectionNames.DATASETS)
        dataset_collection.insert_one(dataset_doc)
        
        # Return success response
        result = {
            "status": "success",
            "message": "Dataset registered successfully",
            "dataset": {
                "id": dataset_id,
                "name": request.name,
                "path": str(dataset_path),
                "description": request.description,
                "dataset_type": request.dataset_type,
                **metadata
            }
        }
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=Dict[str, Any])
async def get_all_datasets(
    skip: int = Query(0, description="Number of datasets to skip"),
    limit: int = Query(10, description="Maximum number of datasets to return"),
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Get a list of all registered datasets.
    
    Args:
        skip: Number of datasets to skip.
        limit: Maximum number of datasets to return.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: A list of datasets.
    """
    try:
        # Query database for all datasets
        dataset_collection = db_client.get_collection(CollectionNames.DATASETS)
        
        # Get count of all datasets
        total_count = dataset_collection.count_documents({})
        
        # Get datasets with pagination
        cursor = dataset_collection.find({}).skip(skip).limit(limit)
        
        # Extract basic information for each dataset
        datasets = []
        for doc in cursor:
            metadata = doc.get("metadata", {})
            datasets.append({
                "id": doc.get("dataset_id"),
                "name": doc.get("name", "Unknown"),
                "path": doc.get("path", ""),
                "description": doc.get("description", ""),
                "dataset_type": doc.get("dataset_type", "bids"),
                "size": metadata.get("size_human", "Unknown"),
                "file_count": metadata.get("file_count", 0)
            })
        
        # If no datasets found in database, try to list from the datasets directory
        if not datasets:
            paths = NeuroAnalystPaths()
            datasets_dir = PathLib(paths.datasets)
            
            if datasets_dir.exists():
                # Get all dataset directories
                dataset_dirs = [d for d in datasets_dir.iterdir() if d.is_dir()]
                dataset_dirs = sorted(dataset_dirs)[skip:skip + limit]
                
                # Process each directory
                for i, dataset_dir in enumerate(dataset_dirs):
                    # Get basic metadata
                    metadata = _get_dataset_metadata(dataset_dir)
                    
                    datasets.append({
                        "id": f"DS-{i+1}",
                        "name": dataset_dir.name,
                        "path": str(dataset_dir),
                        "description": "",
                        "dataset_type": "bids" if (dataset_dir / "dataset_description.json").exists() else "other",
                        "size": metadata.get("size_human", "Unknown"),
                        "file_count": metadata.get("file_count", 0)
                    })
                
                total_count = len(dataset_dirs)
        
        result = {
            "status": "success",
            "count": total_count,
            "datasets": datasets
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dataset_id}", response_model=Dict[str, Any])
async def get_dataset(
    dataset_id: str = Path(..., description="The ID of the dataset to retrieve"),
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Get details of a specific dataset.
    
    Args:
        dataset_id: The ID of the dataset to get.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: The dataset details.
    """
    try:
        # Try to find dataset in database
        dataset_collection = db_client.get_collection(CollectionNames.DATASETS)
        dataset_doc = dataset_collection.find_one({"dataset_id": dataset_id})
        
        if dataset_doc:
            # Create dataset from database document
            metadata = dataset_doc.get("metadata", {})
            dataset_path = PathLib(dataset_doc.get("path", ""))
            
            # Get directory structure
            directory_structure = _get_directory_info(dataset_path, max_depth=2)
            
            result = {
                "status": "success",
                "dataset": {
                    "id": dataset_doc.get("dataset_id"),
                    "name": dataset_doc.get("name", "Unknown"),
                    "path": dataset_doc.get("path", ""),
                    "description": dataset_doc.get("description", ""),
                    "dataset_type": dataset_doc.get("dataset_type", "bids"),
                    "size": metadata.get("size_human", "Unknown"),
                    "file_count": metadata.get("file_count", 0),
                    "subjects": metadata.get("subjects", []),
                    "sessions": metadata.get("sessions", []),
                    "datatypes": metadata.get("datatypes", []),
                    "directory_structure": directory_structure
                }
            }
            
            # Add BIDS description if available
            if "description" in metadata:
                result["dataset"]["bids_description"] = metadata["description"]
                
            return result
        else:
            # Try to find dataset in file system
            # This is for backward compatibility or datasets not registered in DB
            paths = NeuroAnalystPaths()
            datasets_dir = PathLib(paths.datasets)
            
            # Generate a simple lookup for dataset ID
            if dataset_id.startswith("DS-"):
                try:
                    dataset_index = int(dataset_id.split("-")[1]) - 1
                    dataset_dirs = sorted([d for d in datasets_dir.iterdir() if d.is_dir()])
                    
                    if 0 <= dataset_index < len(dataset_dirs):
                        dataset_path = dataset_dirs[dataset_index]
                        metadata = _get_dataset_metadata(dataset_path)
                        directory_structure = _get_directory_info(dataset_path, max_depth=2)
                        
                        result = {
                            "status": "success",
                            "dataset": {
                                "id": dataset_id,
                                "name": dataset_path.name,
                                "path": str(dataset_path),
                                "description": "",
                                "dataset_type": "bids" if (dataset_path / "dataset_description.json").exists() else "other",
                                "size": metadata.get("size_human", "Unknown"),
                                "file_count": metadata.get("file_count", 0),
                                "subjects": metadata.get("subjects", []),
                                "sessions": metadata.get("sessions", []),
                                "datatypes": metadata.get("datatypes", []),
                                "directory_structure": directory_structure
                            }
                        }
                        
                        # Add BIDS description if available
                        if "description" in metadata:
                            result["dataset"]["bids_description"] = metadata["description"]
                            
                        return result
                except (ValueError, IndexError):
                    pass
            
            raise HTTPException(
                status_code=404,
                detail=f"Dataset with ID {dataset_id} not found"
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{dataset_id}/filter", response_model=Dict[str, Any])
async def filter_dataset(
    dataset_id: str = Path(..., description="The ID of the dataset to filter"),
    bids_filter: BIDSFilter = None,
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Get a list of files in a specific dataset that match the provided BIDS filters.
    
    Args:
        dataset_id: The ID of the dataset to filter.
        bids_filter: The BIDS filter to apply.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: A list of matching files.
    """
    try:
        # Initialize filter if not provided
        if not bids_filter:
            bids_filter = BIDSFilter()
        
        # Get dataset path from database or file system
        dataset_path = None
        
        # Try database first
        dataset_collection = db_client.get_collection(CollectionNames.DATASETS)
        dataset_doc = dataset_collection.find_one({"dataset_id": dataset_id})
        
        if dataset_doc:
            dataset_path = PathLib(dataset_doc.get("path", ""))
        else:
            # Try file system fallback
            if dataset_id.startswith("DS-"):
                try:
                    dataset_index = int(dataset_id.split("-")[1]) - 1
                    paths = NeuroAnalystPaths()
                    datasets_dir = PathLib(paths.datasets)
                    dataset_dirs = sorted([d for d in datasets_dir.iterdir() if d.is_dir()])
                    
                    if 0 <= dataset_index < len(dataset_dirs):
                        dataset_path = dataset_dirs[dataset_index]
                except (ValueError, IndexError):
                    pass
        
        if not dataset_path or not dataset_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Dataset with ID {dataset_id} not found"
            )
        
        # Initialize list of matching files
        files = []
        
        # Extract non-None filter values
        filter_dict = {k: v for k, v in bids_filter.dict().items() if v is not None}
        
        # Try to use PyBIDS if it's installed
        try:
            from bids import BIDSLayout
            layout = BIDSLayout(dataset_path)
            bids_files = layout.get(**filter_dict)
            
            for bf in bids_files:
                files.append({
                    "path": str(bf.path),
                    "entities": bf.entities
                })
        except ImportError:
            # Fall back to simple file system traversal if PyBIDS is not available
            # This is a simplified implementation that doesn't fully parse BIDS
            for root, _, filenames in os.walk(dataset_path):
                for filename in filenames:
                    # Skip hidden files and non-data files
                    if filename.startswith('.') or filename in ["dataset_description.json", "participants.tsv"]:
                        continue
                    
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, dataset_path)
                    
                    # Very simple filter matching
                    match = True
                    
                    # Check subject
                    if bids_filter.subject and f"sub-{bids_filter.subject}" not in rel_path:
                        match = False
                    
                    # Check session
                    if bids_filter.session and f"ses-{bids_filter.session}" not in rel_path:
                        match = False
                    
                    # Check datatype (anat, func, etc.)
                    if bids_filter.datatype:
                        datatype_pattern = f"/{bids_filter.datatype}/"
                        if datatype_pattern not in rel_path:
                            match = False
                    
                    # Check extension
                    if bids_filter.extension and not filename.endswith(bids_filter.extension):
                        match = False
                    
                    # Check suffix (T1w, bold, etc.)
                    if bids_filter.suffix and f"_{bids_filter.suffix}" not in filename:
                        match = False
                    
                    if match:
                        # Extract entities from filename (very simplified)
                        entities = {}
                        parts = os.path.basename(filename).split('_')
                        
                        for part in parts:
                            if '-' in part:
                                key, value = part.split('-', 1)
                                entities[key] = value
                            elif '.' in part:
                                # Handle suffix and extension
                                suffix_ext = part.split('.', 1)
                                if len(suffix_ext) > 0:
                                    entities["suffix"] = suffix_ext[0]
                        
                        # Add extension
                        entities["extension"] = os.path.splitext(filename)[1]
                        
                        files.append({
                            "path": file_path,
                            "entities": entities
                        })
        
        result = {
            "status": "success",
            "count": len(files),
            "files": files
        }
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{dataset_id}", response_model=Dict[str, Any])
async def unregister_dataset(
    dataset_id: str = Path(..., description="The ID of the dataset to unregister"),
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Unregister a dataset from the system. This does not delete the actual data.
    
    Args:
        dataset_id: The ID of the dataset to unregister.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: The unregistration status.
    """
    try:
        # Check if the dataset exists in the database
        dataset_collection = db_client.get_collection(CollectionNames.DATASETS)
        dataset_doc = dataset_collection.find_one({"dataset_id": dataset_id})
        
        if not dataset_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset with ID {dataset_id} not found"
            )
        
        # Delete from database
        dataset_collection.delete_one({"dataset_id": dataset_id})
        
        # Return success response
        result = {
            "status": "success",
            "message": f"Dataset {dataset_id} unregistered successfully"
        }
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
