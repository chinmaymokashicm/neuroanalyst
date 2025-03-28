from ..utils import get_static_json_response
from ...utils.constants import COLLECTION_PROCESS_EXECS
from ...utils.db import find_one_from_db, find_many_from_db, insert_to_db, update_db_record, search_by_keyword
from ..to_table import convert_all_process_execs_to_table

from fastapi import APIRouter
from fastapi.responses import JSONResponse

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

@router.post("/create/", tags=["process", "exec"])
async def create_exec():
    return {"message": "Create exec"}

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