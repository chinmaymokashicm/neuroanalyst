from ..utils.constants import *
from ..utils.envs import get_neuroanalyst_root_dirs

import datetime, logging, os
from typing import Any

def generate_log_file_name(task_name: str) -> str:
    """
    Generate a log file name based on the task name.
    """
    current_time: datetime.datetime = datetime.datetime.now()
    timestamp: str = current_time.strftime("%Y%m%d_%H%M%S")
    log_file_name: str = f"{task_name}_{timestamp}.log"
    return log_file_name

def get_custom_logger(task_name: str) -> logging.Logger:
    """
    Create a custom logger for a specific task.
    """
    log_dir_path: str = get_neuroanalyst_root_dirs("logs")
    if isinstance(log_dir_path, dict):
        raise ValueError("Expected a string but got a dictionary.")
    log_dir_path: str = os.path.join(log_dir_path, task_name)
    os.makedirs(log_dir_path, exist_ok=True)
    log_file_name: str = generate_log_file_name(task_name)
    log_file_path: str = os.path.join(log_dir_path, log_file_name)

    logger: logging.Logger = logging.getLogger(task_name)
    logger.setLevel(logging.INFO)

    # Create a file handler
    file_handler: logging.FileHandler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)

    # Create a formatter and set it for the handler
    formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    return logger