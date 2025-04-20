"""
Celery tasks related to NeuroAnalyst Processes.
"""
from ..utils import get_custom_logger
from ...models.core.pipeline import Pipeline

from uuid import uuid4
from typing import Optional
from pathlib import Path, PosixPath
import logging, os

from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def run_pipeline(pipeline_json: str, task_id: Optional[str] = None) -> dict:
    """Run pipeline."""
    if task_id is None:
        task_id = str(uuid4())
    
    # Parse the pipeline JSON to extract the pipeline ID
    try:
        pipeline: Pipeline = Pipeline.model_validate_json(pipeline_json)
        pipeline_id = pipeline.id
    except Exception as e:
        logger.warning(f"Could not extract pipeline ID, defaulting to task ID: {e}")
        return {"task_id": task_id, "status": "failed", "error": str(e)}
    logger = get_custom_logger(task_name=f"pipeline_{pipeline_id}")
    
    try:
        logger.info(f"Executing pipeline {pipeline.id}")
        pipeline.execute()
    except Exception as e:
        logger.exception(f"Failed to execute pipeline : {e}")
        return {"task_id": task_id, "status": "failed", "error": str(e)}
    
    logger.info(f"Pipeline {pipeline.id} executed successfully.")
    return {"task_id": task_id, "status": "completed"}