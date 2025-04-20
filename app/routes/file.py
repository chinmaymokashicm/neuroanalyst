"""
Send file
"""
from ..utils.envs import get_neuroanalyst_root_dirs

from pathlib import Path
import logging

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_class=FileResponse)
async def get_file(path: str, dir: str = "dataset"):
    """
    Send file from the server.
    """
    if dir == "dataset":
        dataset_dir: str = get_neuroanalyst_root_dirs("datasets")
    else:
        return JSONResponse(status_code=400, content={"error": "Incorrect dir type"})
    file_path = Path(dataset_dir) / path
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return JSONResponse(status_code=404, content={"error": "File not found"})
    logger.info(f"Sending file: {file_path}")
    if str(file_path).endswith(".json"):
        media_type: str = "application/json"
    elif str(file_path).endswith((".nii", ".nii.gz")):
        media_type: str = "application/nifti"
    else:
        media_type: str = "application/unknown" # TODO
    return FileResponse(file_path, media_type=media_type)