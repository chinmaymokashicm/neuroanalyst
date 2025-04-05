from ..models.core.pipeline import Pipeline
from .utils import get_static_json_response
from ..utils.constants import COLLECTION_PIPELINES
from ..utils.db import find_one_from_db, find_many_from_db, insert_to_db, update_db_record, search_by_keyword
from .to_table import convert_all_pipelines_to_table
from ..celery.tasks.pipeline import run_pipeline

import json

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/all/", tags=["pipeline"])
async def get_all_pipelines():
    return get_static_json_response(convert_all_pipelines_to_table(), ())

@router.get("/id/{id}/", tags=["pipeline"])
async def get_pipeline(pipeline_id: str):
    return get_static_json_response(find_one_from_db, (COLLECTION_PIPELINES, {"id": pipeline_id}))

@router.get("/filter/", tags=["pipeline"])
async def search_pipelines_by_filter(filters: dict = {}):
    return get_static_json_response(find_many_from_db, (COLLECTION_PIPELINES, filters))

@router.get("/search/{keyword}/", tags=["pipeline"])
async def search_pipelines_by_keyword(keyword: str):
    if keyword == "":
        return JSONResponse(status_code=400, content={"message": "Keyword cannot be empty"})
    return get_static_json_response(search_by_keyword, (COLLECTION_PIPELINES, keyword))

# ==================================================================================================

@router.post("/execute/", tags=["pipeline"])
async def execute_pipeline(form_data: str = Form(...)) -> JSONResponse:
    try:
        form_dict: dict = json.loads(form_data)
        print("Form data:", form_dict)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid form data")

    # Execute process and return process exec id.
    try:
        pipeline: Pipeline = Pipeline.from_user(**form_dict)
        pipeline_id: str = pipeline.id
        run_pipeline.apply_async(args=[pipeline.model_dump_json()]) # Push to Celery task
        return JSONResponse(status_code=201, content={"message": f"Pipeline executed with PID - {pipeline_id}"})
    except Exception as e:
        print(f"Error executing process: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to run pipeline. Error: {e}")