"""
Celery tasks related to NeuroAnalyst Processes.
"""
from ...models.core.process import ProcessImageApptainer, ProcessExecApptainer

from uuid import uuid4
from typing import Optional
from pathlib import Path, PosixPath

from celery import shared_task

@shared_task
def build_process_image(process_json: str, task_id: Optional[str] = None) -> dict:
    """Build Apptainer image for a process."""
    if task_id is None:
        task_id = str(uuid4())
    try:
        process: ProcessImageApptainer = ProcessImageApptainer.model_validate_json(process_json)
        process.build_image()
    except Exception as e:
        return {"task_id": task_id, "status": "failed", "error": str(e)}
    return {"task_id": task_id, "status": "completed"}

@shared_task
def execute_process(process_exec_json: str, task_id: Optional[str] = None) -> dict:
    """Execute process."""
    if task_id is None:
        task_id = str(uuid4())
    try:
        process_exec: ProcessExecApptainer = ProcessExecApptainer.model_validate_json(process_exec_json)
        process_exec.execute()
    except Exception as e:
        return {"task_id": task_id, "status": "failed", "error": str(e)}
    return {"task_id": task_id, "status": "completed"}