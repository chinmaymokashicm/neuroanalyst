from ..utils import get_static_json_response
from ...utils.constants import *
from ...utils.db import find_one_from_db, find_many_from_db, insert_to_db, update_db_record, search_by_keyword
from ...utils.form import FormSchema
from ...utils.envs import get_neuroanalyst_root_dirs
from ..to_table import convert_all_workdirs_to_table
from ...models.core.process import ProcessImageApptainer
from ...celery.tasks.process import build_process_image

import json, logging
from pathlib import Path, PosixPath

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/all", tags=["workdir"])
async def get_all_workdir() -> JSONResponse:
    return get_static_json_response(convert_all_workdirs_to_table, ())

@router.get("/id/{name}", tags=["workdir"])
async def get_workdir_info(name: str) -> JSONResponse:
    """
    Get workdir info
    """
    # set_neuroanalyst_root_dirs()
    neuroanalyst_workdir_root_value = get_neuroanalyst_root_dirs("workdir")
    if isinstance(neuroanalyst_workdir_root_value, dict):
        raise HTTPException(status_code=500, detail="Expected a string but got a dictionary.")
    neuroanalyst_workdir_root: str = neuroanalyst_workdir_root_value
    workdir_root: PosixPath = PosixPath(Path(neuroanalyst_workdir_root) / name)
    if not workdir_root.exists():
        raise HTTPException(status_code=404, detail=f"Workdir {name} not found.")
    # Return all file contents in the workdir as JSON
    workdir_info: dict = {}
    for item in workdir_root.iterdir():
        if item.is_dir():
            # workdir_info[item.name] = str(item)
            pass
        else:
            with open(item, "r") as f:
                content: str = f.read()
            workdir_info[item.name] = content
    # workdir_info["id"] = name
    return JSONResponse(status_code=201, content=workdir_info)