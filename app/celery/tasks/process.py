"""
Celery tasks related to NeuroAnalyst Processes.
"""
from ...models.core.process import ProcessImage

from uuid import uuid4
from typing import Optional
from pathlib import Path, PosixPath

from celery import shared_task

@shared_task
def build_process_image(process: ProcessImage, dest_dir: str | PosixPath, task_id: Optional[str] = None) -> dict:
    """Build Docker image for a process."""
    if task_id is None:
        task_id = str(uuid4())
    dest_dir = Path(dest_dir)
    try:
        process.build_image(dest_dir)
    except Exception as e:
        return {"task_id": task_id, "status": "failed", "error": str(e)}
    return {"task_id": task_id, "status": "completed"}