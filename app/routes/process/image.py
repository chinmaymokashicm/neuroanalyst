from ..utils import get_static_json_response
from ...utils.constants import COLLECTION_PROCESS_IMAGES
from ...utils.db import find_one_from_db, find_many_from_db, insert_to_db, update_db_record, search_by_keyword, delete_db_record
from ...utils.form import FormSchema
from ..to_table import convert_all_process_images_to_table
from ...models.core.process import ProcessImageApptainer
from ...celery.tasks.process import build_process_image
from ...utils.envs import get_neuroanalyst_root_dirs

import json, traceback, logging
from pathlib import Path, PosixPath

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/all", tags=["process", "image"])
async def get_all_processes() -> JSONResponse:
    return get_static_json_response(convert_all_process_images_to_table, ())

@router.get("/id/{image_id}/", tags=["process", "image"])
async def get_process_by_id(image_id: str) -> JSONResponse:
    return get_static_json_response(find_one_from_db, (COLLECTION_PROCESS_IMAGES, {"id": image_id}))

@router.get("/filter/", tags=["process", "image"])
async def search_processes_by_filter(filters: dict = {}) -> JSONResponse:
    return get_static_json_response(find_many_from_db, (COLLECTION_PROCESS_IMAGES, filters))

@router.get("/search/{keyword}", tags=["process", "image"])
async def search_processes_by_keyword(keyword: str) -> JSONResponse:
    if keyword == "":
        return JSONResponse(status_code=400, content={"message": "Keyword cannot be empty"})
    return get_static_json_response(search_by_keyword, (COLLECTION_PROCESS_IMAGES, keyword))

@router.get("/schema/", tags=["process", "image"])
async def load_process_image_schema() -> FormSchema:
    schema = ProcessImageApptainer.get_ui_form_schema()
    return schema

# ==================================================================================================

@router.post("/preview/", tags=["process", "image"])
async def preview_process(form_data: str = Form(...)) -> JSONResponse:
    try:
        form_dict: dict = json.loads(form_data)
        logger.info(f"Returning process preview")
    except json.JSONDecodeError:
        logger.exception(f"Error getting process preview. Invalid form data!")
        raise HTTPException(status_code=400, detail="Invalid form data")
    
    return ProcessImageApptainer.get_ui_submission_preview(form_dict)

@router.post("/create/", tags=["process", "image"])
async def create_process(form_data: str | dict = Form(...)) -> JSONResponse:
    try:
        form_dict: dict = form_data
        if isinstance(form_data, str):
            form_dict: dict = json.loads(form_data)
    except json.JSONDecodeError as e:
        logger.info(f"Error decoding JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid form data")

    # Run process and return process id.
    try:
        process_image: ProcessImageApptainer = ProcessImageApptainer.from_user(**form_dict)
        build_process_image.apply_async(args=[process_image.model_dump_json()]) # Push to Celery task
        success_content: dict = {"message": f"Process created with PID - {process_image.id}"}
        logger.info(success_content["message"])
        return JSONResponse(status_code=201, content=success_content)
    except Exception as e:
        logger.exception(f"Error creating process: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create process. Error: {e}")

# @router.put("/update/{image_id}", tags=["process", "image"])
# async def update_process(image_id: str):
#     return {"message": f"Update process with id {image_id}"}

@router.post("/delete/{image_id}", tags=["process", "image"])
async def delete_process(image_id: str):
    try:
        image_dir: str = get_neuroanalyst_root_dirs("images")
        if isinstance(image_dir, dict):
            raise HTTPException(status_code=500, detail="Expected a string but got a dictionary.")
        image_dir = Path(image_dir)
        image_path: Path = image_dir / f"{image_id}.sif"
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image {image_id} not found.")
        image_path.unlink()
        logger.info(f"Deleted image: {image_path}")
        
        docs_dir: str = get_neuroanalyst_root_dirs("docs")
        if isinstance(docs_dir, dict):
            raise HTTPException(status_code=500, detail="Expected a string but got a dictionary.")
        docs_dir = Path(docs_dir)
        if not docs_dir.exists():
            raise HTTPException(status_code=404, detail=f"Docs directory {docs_dir} not found.")
        # Delete the entire docs directory
        docs_path: Path = docs_dir / image_id
        if docs_path.exists():
            for item in docs_path.iterdir():
                if item.is_dir():
                    item.rmdir()
                else:
                    item.unlink()
            docs_path.rmdir()
            logger.info(f"Deleted docs directory: {docs_path}")
        else:
            logger.info(f"Docs directory {docs_path} does not exist.")
        
        # Delete from database
        delete_db_record(COLLECTION_PROCESS_IMAGES, {"id": image_id})
    except Exception as e:
        logger.exception(f"Error deleting process: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to delete process. Error: {e}") 