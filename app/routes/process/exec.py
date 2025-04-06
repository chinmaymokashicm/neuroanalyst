from ...models.core.process import ProcessExecApptainer
from ..utils import get_static_json_response
from ...utils.constants import COLLECTION_PROCESS_EXECS
from ...utils.db import find_one_from_db, find_many_from_db, insert_to_db, update_db_record, search_by_keyword
from ..to_table import convert_all_process_execs_to_table
from ...celery.tasks.process import execute_process

import json, logging

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/all/", tags=["process", "exec"])
async def get_all_execs():
    # return get_static_json_response(find_many_from_db, (COLLECTION_PROCESS_EXECS, {}))
    return get_static_json_response(convert_all_process_execs_to_table, ())

@router.get("/id/{exec_id}/", tags=["process", "exec"])
async def get_exec_by_id(exec_id: str):
    return get_static_json_response(find_one_from_db, (COLLECTION_PROCESS_EXECS, {"id": exec_id}))

@router.get("/filter/", tags=["process", "exec"])
async def search_execs_by_filter(filters: dict = {}):
    return get_static_json_response(find_many_from_db, (COLLECTION_PROCESS_EXECS, filters))

@router.get("/search/{keyword}/", tags=["process", "exec"])
async def search_execs_by_keyword(keyword: str):
    if keyword == "":
        return JSONResponse(status_code=400, content={"message": "Keyword cannot be empty"})
    return get_static_json_response(search_by_keyword, (COLLECTION_PROCESS_EXECS, keyword))

# ==================================================================================================

@router.post("/execute/", tags=["process", "exec"])
async def execute_process(form_data: str = Form(...)) -> JSONResponse:
    try:
        form_dict: dict = json.loads(form_data)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid form data")

    # Execute process and return process exec id.
    try:
        process_exec: ProcessExecApptainer = ProcessExecApptainer.from_user(**form_dict)
        process_id: str = process_exec.process_image.id
        process_exec_id: str = process_exec.id
        execute_process.apply_async(args=[process_exec.model_dump_json()]) # Push to Celery task
        success_content: dict = {"message": f"Process {process_id} executed with PID - {process_exec_id}"}
        logging.info(success_content["message"])
        return JSONResponse(status_code=201, content=success_content)
    except Exception as e:
        logging.error(f"Error executing process: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create process exec. Error: {e}")

@router.put("/{exec_id}/update/", tags=["process", "exec"])
async def update_exec(exec_id: str):
    return {"message": f"Update exec with id {exec_id}"}

@router.delete("/{exec_id}/delete/", tags=["process", "exec"])
async def delete_exec(exec_id: str):
    return {"message": f"Delete exec with id {exec_id}"}

# ==================================================================================================

@router.get("/{exec_id}/status/", tags=["process", "exec"])
async def get_exec_status(exec_id: str):
    return {"message": f"Get status of exec with id {exec_id}"}