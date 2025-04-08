from ..models.core.pipeline import Pipeline
from .utils import get_static_json_response
from ..utils.constants import COLLECTION_PIPELINES
from ..utils.db import find_one_from_db, find_many_from_db, insert_to_db, update_db_record, search_by_keyword, delete_db_record
from .to_table import convert_all_pipelines_to_table
from ..celery.tasks.pipeline import run_pipeline

import json, logging

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/all", tags=["pipeline"])
async def get_all_pipelines():
    return get_static_json_response(convert_all_pipelines_to_table, ())

@router.get("/id/{id}/", tags=["pipeline"])
async def get_pipeline(id: str):
    return get_static_json_response(find_one_from_db, (COLLECTION_PIPELINES, {"id": id}))

@router.get("/filter/", tags=["pipeline"])
async def search_pipelines_by_filter(filters: dict = {}):
    return get_static_json_response(find_many_from_db, (COLLECTION_PIPELINES, filters))

@router.get("/search/{keyword}/", tags=["pipeline"])
async def search_pipelines_by_keyword(keyword: str):
    if keyword == "":
        return JSONResponse(status_code=400, content={"message": "Keyword cannot be empty"})
    return get_static_json_response(search_by_keyword, (COLLECTION_PIPELINES, keyword))

# ==================================================================================================

@router.post("/create/", tags=["pipeline"])
async def create_pipeline(form_data: str = Form(...)) -> JSONResponse:
    try:
        form_dict: dict = json.loads(form_data)
        logger.info("Form data:", form_dict)
    except json.JSONDecodeError as e:
        logger.info(f"Error decoding JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid form data")

    # Create pipeline and save it to database.
    try:
        pipeline: Pipeline = Pipeline.from_user(**form_dict)
        pipeline_id: str = pipeline.id
        pipeline.to_db()
        return JSONResponse(status_code=201, content={"message": f"Pipeline created with PID - {pipeline_id}"})
    except Exception as e:
        logger.exception(f"Error executing process: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to run pipeline. Error: {e}")

@router.post("/execute/{pipeline_id}", tags=["pipeline"])
async def execute_pipeline(pipeline_id: str) -> JSONResponse:
    # Execute pipeline.
    try:
        pipeline: Pipeline = Pipeline.from_db(pipeline_id=pipeline_id)
        run_pipeline.apply_async(args=[pipeline.model_dump_json()]) # Push to Celery task
        return JSONResponse(status_code=201, content={"message": f"Pipeline executed. Check database for updates."})
    except Exception as e:
        logger.exception(f"Error executing process: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to run pipeline. Error: {e}")
    
@router.post("/delete/{pipeline_id}", tags=["pipeline"])
async def delete_pipeline(pipeline_id: str):
    try:
        delete_db_record(COLLECTION_PIPELINES, {"id": pipeline_id})
    except Exception as e:
        logger.exception(f"Error deleting pipeline: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to delete pipeline. Error: {e}") 