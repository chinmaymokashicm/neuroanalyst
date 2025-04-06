import logging
from enum import Enum

from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class AppTypeEnum(Enum):
    fastapi = "fastapi"
    celery = "celery"


# Wrapper to generate static JSON response to a query function.
def get_static_json_response(query_func: callable, query_params: iter, success_status: int = 200, error_status: int = 500):
    """
    Wrapper to generate static response for query functions.
    """
    try:
        content = query_func(*query_params)
        status_code = success_status
        logging.info(f"Function {query_func} called successfully with params: {query_params}")
    except Exception as e:
        content = {"message": f"Failed to get data. Error: {e}"}
        status_code = error_status
        logging.error(f"Error calling function {query_func} with params: {query_params}")
    return JSONResponse(status_code=status_code, content=content)

# Asynchronous log stream reader with formatting as per error, warning, info, etc. and chunking.
async def log_reader(log_file: str, n_lines: int = 10) -> list[str]:
    log_lines: list[str] = []
    with open(log_file, "r") as f:
        for line in f.readlines()[-n_lines:]:
            if "ERROR" in line:
                log_lines.append(f"<span style='color:red'>{line}</span><br>")
            elif "WARNING" in line:
                log_lines.append(f"<span style='color:orange'>{line}</span><br>")
            else:
                log_lines.append(f"{line}<br>")
    return log_lines