from celery import shared_task
import time

@shared_task
def long_running_task(task_id: str):
    """Simulates a long-running job."""
    print(f"Starting long-running task {task_id}...")
    for i in range(5):
        print(f"Processing step {i+1}/5 for task {task_id}...")
        time.sleep(2)  # Simulating computation delay
    return {"task_id": task_id, "status": "completed"}