"""
Logs Routes

This module contains the API endpoints for retrieving and streaming log files.
"""
from ..utils.constants import NeuroAnalystPaths
from ..models.pipeline.core import NeuPipeline
from ..models.process.exec.core import NeuProcessExec
from ..models.process.process.core import NeuProcess

from typing import Optional, List
from pathlib import Path
import os
from fastapi import APIRouter, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse

# Router definition
router = APIRouter(
    prefix="/logs",
    tags=["logs"],
)

def file_stream_generator(file_path: Path):
    """
    Generator function to stream a file in chunks.
    
    Args:
        file_path: Path to the file to stream
        
    Yields:
        Chunks of the file
    """
    try:
        with open(file_path, "r") as file:
            for line in file:
                yield line
    except Exception as e:
        yield f"Error streaming log file: {str(e)}"

@router.get("/image/{process_id}")
def get_image_build_log(process_id: str, username: Optional[str] = None):
    """
    Get the log file for a container image build process.
    
    Args:
        process_id: ID of the process
        
    Returns:
        Streaming response with the log content
    """
    process: NeuProcess = NeuProcess.from_process_id(process_id, username=username)
    log_file_path = process.build_image_log_path
    
    if not log_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log file {log_file_path} not found"
        )
    
    return StreamingResponse(
        file_stream_generator(log_file_path),
        media_type="text/plain"
    )

@router.get("/venv/{process_id}")
def get_venv_build_log(process_id: str, username: Optional[str] = None):
    """
    Get the log file for a virtual environment build process.
    
    Args:
        process_id: ID of the process
        
    Returns:
        Streaming response with the log content
    """
    process: NeuProcess = NeuProcess.from_process_id(process_id, username=username)
    log_file_path = process.build_venv_log_path
    
    if not log_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log file {log_file_path} not found"
        )
    
    return StreamingResponse(
        file_stream_generator(log_file_path),
        media_type="text/plain"
    )

@router.get("/pipeline/{pipeline_id}")
def get_pipeline_log(pipeline_id: str, username: Optional[str] = None):
    """
    Get the log file for a pipeline execution.
    
    Args:
        pipeline_id: ID of the pipeline
        
    Returns:
        Streaming response with the log content
    """
    pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id, username=username)
    log_file_path = pipeline.log_file_path
    
    return StreamingResponse(
        file_stream_generator(log_file_path),
        media_type="text/plain"
    )