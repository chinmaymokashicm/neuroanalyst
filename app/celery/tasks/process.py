"""
Celery tasks related to NeuroAnalyst Processes.
"""
from ...models.core.process import ProcessImageApptainer, ProcessExecApptainer

from uuid import uuid4
from typing import Optional
from pathlib import Path, PosixPath
import logging

from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def build_process_image(process_json: str, task_id: Optional[str] = None) -> dict:
    """Build Apptainer image for a process."""
    if task_id is None:
        task_id = str(uuid4())
    try:
        process: ProcessImageApptainer = ProcessImageApptainer.model_validate_json(process_json)
        logger.info(f"Building image with PID: {process.id}")
        process.build_image()
    except Exception as e:
        logger.exception(f"Failed to build image within Celery: {e}")
        return {"task_id": task_id, "status": "failed", "error": str(e)}
    return {"task_id": task_id, "status": "completed"}

@shared_task
def execute_process(process_exec_json: str, task_id: Optional[str] = None) -> dict:
    """Execute process."""
    if task_id is None:
        task_id = str(uuid4())
    try:
        process_exec: ProcessExecApptainer = ProcessExecApptainer.model_validate_json(process_exec_json)
        logger.info(f"Executing image {process_exec.process_image.id} with PID {process_exec.id}")
        process_exec.execute()
    except Exception as e:
        logger.exception(f"Failed to execute process: {e}")
        return {"task_id": task_id, "status": "failed", "error": str(e)}
    return {"task_id": task_id, "status": "completed"}