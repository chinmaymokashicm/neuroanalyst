from ..utils import get_static_json_response
from ...utils.constants import *
from ...utils.db import find_one_from_db, find_many_from_db, insert_to_db, update_db_record, search_by_keyword
from ...utils.form import FormSchema
from ..to_table import convert_all_workdirs_to_table
from ...models.core.process import ProcessImageApptainer
from ...celery.tasks.process import build_process_image

import json

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/all", tags=["workdir"])
async def get_all_workdir() -> JSONResponse:
    return get_static_json_response(convert_all_workdirs_to_table, ())