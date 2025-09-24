"""
NeuroAnalyst BIDS Router

This module defines the FastAPI router for the BIDS endpoints.
It provides endpoints to extract BIDS entities from file names.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
from pathlib import Path as PathLib

from ..models.database.mongo_client import MongoDBClient
from ..models.database.collections import CollectionNames
from .dependencies import get_db_client
from ..utils.constants import NeuroAnalystPaths

# Create router
router = APIRouter()


class BIDSValidationRequest(BaseModel):
    """Request model for validating a BIDS dataset."""
    dataset_id: str
    ignore_warnings: bool = False


@router.get("/entities/file_name", response_model=Dict[str, Any])
async def get_file_name_entities(file_name: str = Query(..., description="The BIDS file name to extract entities from")):
    """
    Get the BIDS entities of a specific file given its name.
    
    Args:
        file_name: The name of the BIDS file to extract entities from.
        
    Returns:
        Dict[str, Any]: The extracted BIDS entities.
    """
    try:
        # Try using PyBIDS if available
        try:
            from bids.layout import parse_file_entities
            entities = parse_file_entities(file_name)
        except ImportError:
            # Fall back to simple parsing if PyBIDS is not available
            entities = {}
            parts = file_name.split('_')
            
            for part in parts:
                if '-' in part:
                    key_value = part.split('-', 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        entities[key] = value
                elif '.' in part:
                    # Handle suffix and extension
                    suffix = part.split('.')[0]
                    extension = '.' + '.'.join(part.split('.')[1:])
                    entities['suffix'] = suffix
                    entities['extension'] = extension
        
        result = {
            "status": "success",
            "file_name": file_name,
            "entities": entities
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=Dict[str, Any])
async def validate_bids_dataset(
    request: BIDSValidationRequest,
    db_client: MongoDBClient = Depends(get_db_client)
):
    """
    Validate a BIDS dataset using the BIDS Validator.
    
    Args:
        request: The request object containing the dataset ID and validation options.
        db_client: MongoDB client for database operations.
        
    Returns:
        Dict[str, Any]: The validation results.
    """
    try:
        # Get dataset path from database or file system
        dataset_path = None
        
        # Try database first
        dataset_collection = db_client.get_collection(CollectionNames.DATASETS)
        dataset_doc = dataset_collection.find_one({"dataset_id": request.dataset_id})
        
        if dataset_doc:
            dataset_path = PathLib(dataset_doc.get("path", ""))
        else:
            # Try file system fallback
            if request.dataset_id.startswith("DS-"):
                try:
                    dataset_index = int(request.dataset_id.split("-")[1]) - 1
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
                detail=f"Dataset with ID {request.dataset_id} not found"
            )
        
        # Check if the bids-validator is installed
        try:
            import subprocess
            import json
            
            # Run the BIDS validator
            cmd = ["bids-validator", str(dataset_path)]
            if request.ignore_warnings:
                cmd.append("--ignoreWarnings")
            
            # Run validator and capture output
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True
            )
            
            # Parse output
            if result.returncode == 0:
                validation_status = "valid"
                validation_message = "Dataset is BIDS valid"
            else:
                validation_status = "invalid"
                validation_message = "Dataset is not BIDS valid"
            
            # Try to parse the JSON output from the validator
            validation_details = {}
            try:
                # Look for JSON in stdout
                stdout = result.stdout
                if stdout:
                    # Try to find and extract JSON part
                    json_start = stdout.find("{")
                    json_end = stdout.rfind("}")
                    if json_start >= 0 and json_end > json_start:
                        json_part = stdout[json_start:json_end+1]
                        validation_details = json.loads(json_part)
            except Exception:
                # If JSON parsing fails, use raw output
                validation_details = {
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            
            return {
                "status": "success",
                "dataset_id": request.dataset_id,
                "validation_status": validation_status,
                "validation_message": validation_message,
                "details": validation_details
            }
            
        except FileNotFoundError:
            return {
                "status": "error",
                "message": "BIDS validator not installed. Please install with 'npm install -g bids-validator'."
            }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/common_entities", response_model=Dict[str, Any])
async def get_common_bids_entities():
    """
    Get a list of common BIDS entities and their descriptions.
    
    Returns:
        Dict[str, Any]: A dictionary of common BIDS entities and their descriptions.
    """
    entities = {
        "sub": "Subject identifier",
        "ses": "Session identifier",
        "task": "Task identifier",
        "acq": "Acquisition identifier",
        "ce": "Contrast enhancing agent",
        "dir": "Phase-encoding direction",
        "rec": "Reconstruction identifier",
        "run": "Run index",
        "mod": "Modality identifier",
        "echo": "Echo identifier",
        "flip": "Flip angle",
        "mt": "Magnetization transfer",
        "part": "Part identifier",
        "proc": "Processed (on device)",
        "hemi": "Hemisphere",
        "space": "Coordinate space",
        "res": "Resolution",
        "den": "Density",
        "label": "Label",
        "desc": "Description"
    }
    
    suffixes = {
        "T1w": "T1-weighted MRI",
        "T2w": "T2-weighted MRI",
        "T2star": "T2*-weighted MRI",
        "FLAIR": "Fluid-attenuated inversion recovery MRI",
        "bold": "Blood-oxygen-level dependent MRI",
        "dwi": "Diffusion-weighted MRI",
        "phasediff": "Phase difference map",
        "magnitude": "Magnitude map",
        "epi": "Echo-planar imaging",
        "fieldmap": "Field map",
        "confounds": "Confounds table",
        "mask": "Binary mask",
        "dseg": "Discrete segmentation",
        "timeseries": "Time series data",
        "physio": "Physiological recordings",
        "events": "Task events file"
    }
    
    return {
        "status": "success",
        "entities": entities,
        "suffixes": suffixes
    }
