from ..utils.envs import get_neuroanalyst_root_dirs
from .utils import get_static_json_response, log_reader

import json, logging, asyncio
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, Request, Form, HTTPException, WebSocket
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Get all log file names
@router.get("/all", tags=["log"])
async def get_all_logs(filter: Optional[str] = None) -> JSONResponse:
    """
    Get all log file names
    """
    # set_neuroanalyst_root_dirs()
    neuroanalyst_logs_root: str = get_neuroanalyst_root_dirs("logs")
    if isinstance(neuroanalyst_logs_root, dict):
        logger.error(f"Expected a string but got a dictionary: {neuroanalyst_logs_root}")
        raise HTTPException(status_code=500, detail="Expected a string but got a dictionary.")
    log_files: list = []
    if filter is None:
        filter = ""
    filter = filter.lower()
    neuroanalyst_logs_root_path: Path = Path(neuroanalyst_logs_root)
    for f in neuroanalyst_logs_root_path.iterdir():
        if f.is_file() and f.name.lower().startswith(filter):
            log_files.append(f)
    log_files = [str(f) for f in log_files]
    log_files.sort(reverse=True)
    log_files = [{"name": f, "path": str(f)} for f in log_files]
    logger.info(f"Returning {len(log_files)} log files")
    return JSONResponse(status_code=201, content=log_files)

@router.websocket("/{file_name}")
async def stream(websocket: WebSocket, file_name: str):
    logger.info(f"Websocket connection established for {file_name}")
    last_line_number: int = 0
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(1)
            log_dir: str = get_neuroanalyst_root_dirs("logs")
            if isinstance(log_dir, dict):
                logger.error(f"Expected a string but got a dictionary: {log_dir}")
                await websocket.send_text("Log directory not found.")
                continue
            log_dir_path: Path = Path(log_dir)
            if not log_dir_path.exists():
                logger.error(f"Log directory {log_dir} does not exist.")
                await websocket.send_text("Log directory does not exist.")
                continue
            log_filepath: str = log_dir_path / f"{file_name.split('.')[0]}.log"
            if not log_filepath.exists():
                logger.error(f"Log file {log_filepath} does not exist.")
                await websocket.send_text("Log file does not exist.")
                continue
            logs = await log_reader(log_filepath, start_line=last_line_number)
            last_line_number += len(logs)  # Update the last line number
            await websocket.send_text("\n".join(logs))
    except Exception as e:
        logging.error(f"Websocket closed. Error: {e}")
        await websocket.close()
    finally:
        logging.info("Websocket closed.")
        await websocket.close()