"""
Celery tasks related to NeuroAnalyst Processes.
"""
from ...models.core.pipeline import Pipeline

from uuid import uuid4
from typing import Optional
from pathlib import Path, PosixPath
import logging

from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def run_pipeline(pipeline_json: str, task_id: Optional[str] = None) -> dict:
    """Run pipeline."""
    if task_id is None:
        task_id = str(uuid4())
    try:
        pipeline: Pipeline = Pipeline.model_validate_json(pipeline_json)
        logger.info(f"Executing pipeline {pipeline.id}")
        pipeline.execute()
    except Exception as e:
        logger.exception(f"Failed to execute pipeline : {e}")
        return {"task_id": task_id, "status": "failed", "error": str(e)}
    return {"task_id": task_id, "status": "completed"}