from .utils import get_static_json_response
from ..utils.constants import COLLECTION_PIPELINES
from ..utils.db import find_one_from_db, find_many_from_db, insert_to_db, update_db_record, search_by_keyword
from .to_table import convert_all_pipelines_to_table

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/all/", tags=["pipeline"])
async def get_all_pipelines():
    # return get_static_json_response(find_many_from_db, (COLLECTION_PIPELINES, {}))
    return get_static_json_response(convert_all_pipelines_to_table, ())

@router.get("/id/{pipeline_id}/", tags=["pipeline"])
async def get_pipeline_by_id(pipeline_id: str):
    return get_static_json_response(find_one_from_db, (COLLECTION_PIPELINES, {"id": pipeline_id}))

@router.get("/filter/", tags=["pipeline"])
async def search_pipelines_by_filter(filters: dict = {}):
    return get_static_json_response(find_many_from_db, (COLLECTION_PIPELINES, filters))

@router.get("/search/{keyword}/", tags=["pipeline"])
async def search_pipelines_by_keyword(keyword: str = ""):
    if keyword == "":
        return JSONResponse(status_code=400, content={"message": "Keyword cannot be empty"})
    return get_static_json_response(search_by_keyword, (COLLECTION_PIPELINES, keyword))

# ==================================================================================================

@router.post("/create/", tags=["pipeline"])
async def create_pipeline():
    return {"message": "Create pipeline"}

@router.put("/{pipeline_id}/update/", tags=["pipeline"])
async def update_pipeline(pipeline_id: str):
    return {"message": f"Update pipeline with id {pipeline_id}"}

@router.delete("/{pipeline_id}/delete/", tags=["pipeline"])
async def delete_pipeline(pipeline_id: str):
    return {"message": f"Delete pipeline with id {pipeline_id}"}

# ==================================================================================================

@router.get("/{pipeline_id}/status/", tags=["pipeline"])
async def get_pipeline_status(pipeline_id: str):
    return {"message": f"Get status of pipeline with id {pipeline_id}"}