"""
Work with BIDS datasets
"""

from .utils import get_static_json_response, get_folder_tree
from ..utils.envs import set_neuroanalyst_root_dirs, get_neuroanalyst_root_dirs
from ..utils.constants import *
from ..utils.db import find_one_from_db, find_many_from_db, insert_to_db, update_db_record, search_by_keyword
from ..utils.form import FormSchema
from .to_table import convert_all_datasets_to_table
from ..models.core.process import ProcessImageApptainer
from ..celery.tasks.process import build_process_image

import json, logging
from pathlib import Path, PosixPath

from imagelib.datasets.bids import SelectBIDSDatasetInfo

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse
from bids import BIDSLayout

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/all", tags=["process", "image"])
async def get_all_datasets(get_derivatives: bool = False) -> JSONResponse:
    return get_static_json_response(convert_all_datasets_to_table, ([get_derivatives]))

@router.get("/id/{name}", tags=["dataset"])
async def get_dataset_info(name: str, derivatives: bool = True) -> JSONResponse:
    """
    Get dataset info
    """
    # set_neuroanalyst_root_dirs()
    neuroanalyst_datasets_root_value = get_neuroanalyst_root_dirs("datasets")
    if isinstance(neuroanalyst_datasets_root_value, dict):
        raise HTTPException(status_code=500, detail="Expected a string but got a dictionary.")
    neuroanalyst_datasets_root: str = neuroanalyst_datasets_root_value
    dataset_root: PosixPath = PosixPath(Path(neuroanalyst_datasets_root) / name)
    try:
        dataset_info: SelectBIDSDatasetInfo = SelectBIDSDatasetInfo.from_path(dataset_root, get_derivatives=derivatives)
        dataset_info_dict: dict = dataset_info.to_dict()
        dataset_info_dict["id"] = name
        return JSONResponse(status_code=201, content=dataset_info_dict)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/tree/{name}", tags=["dataset"])
async def get_dataset_tree(name: str) -> JSONResponse:
    """
    Get dataset tree
    """
    # set_neuroanalyst_root_dirs()
    neuroanalyst_datasets_root = get_neuroanalyst_root_dirs("datasets")
    if isinstance(neuroanalyst_datasets_root, dict):
        raise HTTPException(status_code=500, detail="Expected a string but got a dictionary.")
    dataset_root: PosixPath = PosixPath(Path(neuroanalyst_datasets_root) / name)
    try:
        dataset_tree: dict = get_folder_tree(dataset_root)
        dataset_tree["id"] = name
        return JSONResponse(status_code=201, content=dataset_tree)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/entities/", tags=["dataset"])
async def filter_dataset_by_entities(name: str, entities: str) -> JSONResponse:
    """
    Filter dataset by entities
    """
    try:
        entities: dict = json.loads(entities)
    except json.JSONDecodeError as e:
        logger.info(f"Error decoding JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid entities format. Expected a JSON string.")
    # set_neuroanalyst_root_dirs()
    neuroanalyst_datasets_root = get_neuroanalyst_root_dirs("datasets")
    if isinstance(neuroanalyst_datasets_root, dict):
        raise HTTPException(status_code=500, detail="Expected a string but got a dictionary.")
    dataset_root: PosixPath = PosixPath(Path(neuroanalyst_datasets_root) / name)
    try:
        layout: BIDSLayout = BIDSLayout(dataset_root, derivatives=True)
        filtered_data: list = layout.get(entities)
        # Serialize the filtered data
        filtered_data = [str(item) for item in filtered_data]
        return JSONResponse(status_code=201, content=filtered_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))