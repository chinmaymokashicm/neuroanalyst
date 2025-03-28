from ..utils import get_static_json_response
from ...utils.constants import COLLECTION_PROCESS_IMAGES
from ...utils.db import find_one_from_db, find_many_from_db, insert_to_db, update_db_record, search_by_keyword
from ...utils.form import FormSchema
from ..to_table import convert_all_process_images_to_table
from ...models.core.process import ProcessImage
from ...celery.tasks.process import build_process_image

import json

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse

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
    schema = ProcessImage.get_ui_form_schema()
    return schema

# ==================================================================================================

@router.post("/preview/", tags=["process", "image"])
async def preview_process(form_data: str = Form(...)) -> JSONResponse:
    try:
        form_dict: dict = json.loads(form_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid form data")
    
    return ProcessImage.get_ui_submission_preview(form_dict)

@router.post("/create/", tags=["process", "image"])
async def create_process(form_data: str = Form(...)) -> JSONResponse:
    try:
        form_dict: dict = json.loads(form_data)
        print("Form data:", form_dict)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid form data")

    # Run process and return process id.
    try:
        process_image: ProcessImage = ProcessImage.from_user(**form_dict)
        process_image_id, dest_dir = process_image.create_image_workdir()
        # process_image.build_image(dest_dir=dest_dir)
        build_process_image.apply_async(args=[process_image, dest_dir]) # Push to Celery task    
        return JSONResponse(status_code=201, content={"message": f"Process created with PID - {process_image_id}"})
    except Exception as e:
        print(f"Error creating process: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create process. Error: {e}")

@router.put("/{image_id}/update/", tags=["process", "image"])
async def update_process(image_id: str):
    return {"message": f"Update process with id {image_id}"}

@router.delete("/{image_id}/delete/", tags=["process", "image"])
async def delete_process(image_id: str):
    return {"message": f"Delete process with id {image_id}"}