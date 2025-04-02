from .execute import ProcessExecDocker
from ....utils.exceptions import DBRecordMissing

from pathlib import Path, PosixPath
import subprocess

def check_process_exec_status(process_exec_id: str) -> dict[str, bool]:
    """
    Check the status of a process execution.
    
    Args:
        process_exec_id (str): The ID of the process execution.
    """
    process_exec: ProcessExecDocker = ProcessExecDocker.from_db(process_exec_id)
    docker_container_id: str = process_exec.docker_container_id
    
    container_status_command: str = f"docker inspect --format='{{{{.State.Status}}}}' {docker_container_id}"
    result = subprocess.run(container_status_command, shell=True, capture_output=True, text=True)
    
    # If the Docker container does not exist, raise an error
    if result.returncode != 0:
        raise ValueError(f"Failed to inspect Docker container with ID {docker_container_id}. It may not exist.")
    
    # If the Docker container is running, set the status to "RUNNING"
    container_status: str = result.stdout.strip()
    is_docker_container_running: bool = False if container_status == "exited" else True
    
    if is_docker_container_running:
        status: str = "RUNNING"
    else:
        # If the Docker container is not running, check exit code
        container_exit_code_command: str = f"docker inspect --format='{{{{.State.ExitCode}}}}' {docker_container_id}"
        result = subprocess.run(container_exit_code_command, shell=True, capture_output=True, text=True)
        if int(result.stdout.strip()) == 0:
            status: str = "COMPLETED"
        else:
            status: str = "FAILED"
    
    return {
        "is_docker_container_running": is_docker_container_running,
        "status": status
    }
    
    
    # expected_outputs: list[str] = process_exec.process_image.expected_outputs
    # output_dirpath: PosixPath = Path("outputs") / process_exec_id
    # if not output_dirpath.exists():
    #     raise DBRecordMissing(f"Output directory {output_dirpath} does not exist.")
    # completed_outputs: list[str] = [output_file.stem for output_file in output_dirpath.iterdir() if output_file.is_file() and output_file.suffix == ".json"]
    # is_all_results_generated: bool = set(expected_outputs) == set(completed_outputs)
    
    # docker_container_id: str = process_exec.docker_container_id
    
    # container_status_command: str = f"docker inspect --format='{{{{.State.Status}}}}' {docker_container_id}"
    # result = subprocess.run(container_status_command, shell=True, capture_output=True, text=True)
    
    # if result.returncode != 0:
    #     raise ValueError(f"Failed to inspect Docker container with ID {docker_container_id}. It may not exist.")
    
    # container_status: str = result.stdout.strip()
    # is_docker_container_running: bool = False if container_status == "exited" else True
    
    # # if is_all_results_generated and not is_docker_container_running:
    # #     status: str = "COMPLETED"
    # # elif not is_all_results_generated and not is_docker_container_running:
    # #     status: str = "FAILED"
    # # else:
    # #     status: str = "RUNNING"
    # if is_docker_container_running:
    #     status: str = "RUNNING"
    # else:
    #     status: str = "COMPLETED"
    
    # return {
    #     "is_all_results_generated": is_all_results_generated,
    #     "is_docker_container_running": is_docker_container_running,
    #     "status": status
    # }