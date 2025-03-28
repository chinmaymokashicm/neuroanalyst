# from process import build_process_image


# from celery import shared_task
# import subprocess
# # from utils.db import update_job_status  # Function to update job status in MongoDB

# @shared_task(bind=True)
# def run_pipeline(self, job_id: str, docker_image: str, script: str):
#     """
#     Execute a neuroimaging pipeline inside a Docker container.

#     Args:
#         job_id (str): Unique job identifier.
#         docker_image (str): Name of the Docker image to run.
#         script (str): The script or command to execute inside the container.
#     """
#     try:
#         # update_job_status(job_id, "running")

#         # Example: Run a Docker container
#         command = f"docker run --rm {docker_image} {script}"
#         # subprocess.run(command, shell=True, check=True)
#         print(f"Running command: {command}")

#         # update_job_status(job_id, "completed")
#         return {"job_id": job_id, "status": "completed"}

#     except Exception as e:
#         # update_job_status(job_id, "failed")
#         return {"job_id": job_id, "status": "failed", "error": str(e)}
