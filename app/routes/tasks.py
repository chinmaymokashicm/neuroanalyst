from fastapi import APIRouter
from app.celery.tasks.example import long_running_task
from app.celery.tasks.process import build_process_image
from uuid import uuid4

router = APIRouter()

@router.get("/submit-task/")
async def submit_task():
    """Submit a long-running task to Celery."""
    task_id = str(uuid4())  # Generate a unique ID
    result = long_running_task.apply_async(args=[task_id])
    return {"task_id": task_id, "status": "submitted", "celery_id": result.id}