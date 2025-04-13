import logging
from enum import Enum
from typing import Optional, Callable, Any, Iterable
from pathlib import Path, PosixPath

from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class AppTypeEnum(Enum):
    fastapi = "fastapi"
    celery = "celery"


# Wrapper to generate static JSON response to a query function.
def get_static_json_response(query_func: Callable, query_params: Iterable, success_status: int = 200, error_status: int = 500):
    """
    Wrapper to generate static response for query functions.
    """
    try:
        content = query_func(*query_params)
        status_code = success_status
        logging.info(f"Function {query_func.__name__} called successfully with params: {query_params}")
    except Exception as e:
        content = {"message": f"Failed to get data. Error: {e}"}
        status_code = error_status
        logging.error(f"Error calling function {query_func.__name__} with params: {query_params}")
    return JSONResponse(status_code=status_code, content=content)

# Asynchronous log stream reader with formatting as per error, warning, info, etc. and chunking.
async def log_reader(log_file: str, start_line: int = 0, n_lines: Optional[int] = None) -> list[str]:
    # log_lines: list[str] = []
    with open(log_file, "r") as f:
        lines = f.readlines()
        # for line in lines[start_line:start_line + n_lines]:
        #     if "INFO" in line:
        #         log_lines.append(f"<span style='color:green'>{line}</span><br>")
        #     elif "ERROR" in line:
        #         log_lines.append(f"<span style='color:red'>{line}</span><br>")
        #     elif "WARNING" in line:
        #         log_lines.append(f"<span style='color:orange'>{line}</span><br>")
        #     else:
        #         log_lines.append(f"{line}<br>")
    # return log_lines
    if n_lines is None:
        return lines[start_line:]
    return lines[start_line: start_line + n_lines]

def get_folder_tree(folderpath: str | PosixPath) -> dict[str, Any]:
    """
    Get folder tree structure.
    """
    folderpath = PosixPath(folderpath)
    folder_tree = {}
    for item in folderpath.iterdir():
        if item.is_dir():
            folder_tree[item.name] = get_folder_tree(item)
        else:
            folder_tree[item.name] = str(item)
    return folder_tree