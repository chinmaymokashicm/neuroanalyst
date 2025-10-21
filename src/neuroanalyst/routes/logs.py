"""
Logs Routes

This module contains the API endpoints for retrieving and streaming log files.
"""
from typing import Optional, List
from pathlib import Path
import os
from fastapi import APIRouter, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from ..utils.constants import PATHS

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
def get_image_build_log(process_id: str, date_str: Optional[str] = Query(None, description="Date string in format YYYYMMDD_HHMMSS")):
    """
    Get the log file for a container image build process.
    
    Args:
        process_id: ID of the process
        date_str: Optional date string to retrieve a specific log file
        
    Returns:
        Streaming response with the log content
    """
    logs_dir = PATHS.logs
    
    if date_str:
        log_file_path = logs_dir / f"{process_id}_build_{date_str}.log"
    else:
        # Find the most recent log file for this process
        pattern = f"{process_id}_build_*.log"
        log_files = list(logs_dir.glob(pattern))
        
        if not log_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No image build logs found for process ID {process_id}"
            )
        
        # Sort by creation time (newest first)
        log_file_path = sorted(log_files, key=os.path.getctime, reverse=True)[0]
    
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
def get_venv_build_log(process_id: str, date_str: Optional[str] = Query(None, description="Date string in format YYYYMMDD_HHMMSS")):
    """
    Get the log file for a virtual environment build process.
    
    Args:
        process_id: ID of the process
        date_str: Optional date string to retrieve a specific log file
        
    Returns:
        Streaming response with the log content
    """
    logs_dir = PATHS.logs
    
    if date_str:
        log_file_path = logs_dir / f"{process_id}_venv_{date_str}.log"
    else:
        # Find the most recent log file for this process
        pattern = f"{process_id}_venv_*.log"
        log_files = list(logs_dir.glob(pattern))
        
        if not log_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No venv build logs found for process ID {process_id}"
            )
        
        # Sort by creation time (newest first)
        log_file_path = sorted(log_files, key=os.path.getctime, reverse=True)[0]
    
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
def get_pipeline_log(pipeline_id: str):
    """
    Get the log file for a pipeline execution.
    
    Args:
        pipeline_id: ID of the pipeline
        
    Returns:
        Streaming response with the log content
    """
    log_file_path = PATHS.logs / "pipelines" / pipeline_id / f"{pipeline_id}.log"
    
    if not log_file_path.exists():
        # Try alternative path format
        log_file_path = PATHS.logs / f"pipeline_{pipeline_id}.log"
        
        if not log_file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No logs found for pipeline ID {pipeline_id}"
            )
    
    return StreamingResponse(
        file_stream_generator(log_file_path),
        media_type="text/plain"
    )

@router.get("/process_exec/{exec_id}")
def get_process_exec_log(exec_id: str, error: bool = Query(False, description="Whether to retrieve error log instead of standard output")):
    """
    Get the log file for a process execution.
    
    Args:
        exec_id: ID of the process execution
        error: Whether to retrieve error log instead of standard output
        
    Returns:
        Streaming response with the log content
    """
    log_dir = PATHS.logs / "process_execs"
    
    if error:
        log_file_path = log_dir / f"{exec_id}.err"
    else:
        log_file_path = log_dir / f"{exec_id}.log"
    
    if not log_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{'Error' if error else 'Output'} log file not found for execution ID {exec_id}"
        )
    
    return StreamingResponse(
        file_stream_generator(log_file_path),
        media_type="text/plain"
    )

@router.get("/list")
def list_logs(type: str = Query(..., description="Type of logs to list (image, venv, pipeline, process_exec)"),
              id: Optional[str] = Query(None, description="Optional ID to filter logs by")):
    """
    List available log files for a given type and optional ID.
    
    Args:
        type: Type of logs to list (image, venv, pipeline, process_exec)
        id: Optional ID to filter logs by
        
    Returns:
        List of available log files
    """
    logs_dir = PATHS.logs
    
    if type == "image":
        if id:
            pattern = f"{id}_build_*.log"
        else:
            pattern = "*_build_*.log"
        log_files = list(logs_dir.glob(pattern))
    elif type == "venv":
        if id:
            pattern = f"{id}_venv_*.log"
        else:
            pattern = "*_venv_*.log"
        log_files = list(logs_dir.glob(pattern))
    elif type == "pipeline":
        if id:
            pipeline_logs_dir = logs_dir / "pipelines" / id
            if pipeline_logs_dir.exists():
                log_files = list(pipeline_logs_dir.glob("*.log"))
            else:
                log_files = list(logs_dir.glob(f"pipeline_{id}*.log"))
        else:
            pipeline_logs_dir = logs_dir / "pipelines"
            if pipeline_logs_dir.exists():
                log_files = []
                for pipeline_dir in pipeline_logs_dir.iterdir():
                    if pipeline_dir.is_dir():
                        log_files.extend(list(pipeline_dir.glob("*.log")))
            log_files.extend(list(logs_dir.glob("pipeline_*.log")))
    elif type == "process_exec":
        process_execs_dir = logs_dir / "process_execs"
        if id:
            log_files = list(process_execs_dir.glob(f"{id}.log")) + list(process_execs_dir.glob(f"{id}.err"))
        else:
            log_files = list(process_execs_dir.glob("*.log")) + list(process_execs_dir.glob("*.err"))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid log type: {type}. Valid types are 'image', 'venv', 'pipeline', or 'process_exec'"
        )
    
    # Sort by modification time (newest first)
    log_files = sorted(log_files, key=os.path.getmtime, reverse=True)
    
    return {
        "logs": [
            {
                "path": str(log_file),
                "filename": log_file.name,
                "size": log_file.stat().st_size,
                "modified": os.path.getmtime(log_file),
                "type": type
            }
            for log_file in log_files
        ]
    }