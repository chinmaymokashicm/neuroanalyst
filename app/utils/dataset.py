"""
Code related to working with datasets (usually BIDS).
"""
from .data import search_nested_key, match_dict_with_filters

from typing import Optional, Any
import re

from bids import BIDSLayout
from bids.layout.models import BIDSJSONFile

def get_info_from_sidecar(json_file: BIDSJSONFile, fields: Optional[list], nesting_sep: str = ".") -> dict:
    info: dict = json_file.get_dict()
    return {field: search_nested_key(info, field, nesting_sep) for field in fields}

def identify_sidecars(layout: BIDSLayout, sidecar_data_filters: dict) -> list[BIDSJSONFile]:
    selected_json_files: list[BIDSJSONFile] = []
    for json_file in layout.get(extension=".json"):
        if not isinstance(json_file, BIDSJSONFile):
            raise FileNotFoundError(f"{json_file} is not a BIDSJSONFile type.")
        data: dict = json_file.get_dict()
        if match_dict_with_filters(data, sidecar_data_filters):
            selected_json_files.append(json_file)
    return selected_json_files

def get_sidecar_info_from_dataset(layout: BIDSLayout, process_id: Optional[str] = None, process_exec_id: Optional[str] = None, pipeline_id: Optional[str] = None) -> list[dict]:
    sidecar_data_filters: dict = {key: value for key, value in [("process_id", process_id), ("process_exec_id", process_exec_id), ("pipeline_id", pipeline_id)] if value is not None}
    sidecars: list[BIDSJSONFile] = identify_sidecars(layout, sidecar_data_filters)
    selected_fields: list[str] = ["process_id", "process_exec_id", "pipeline_id", "name", "description", "pipeline_name", "metrics"]
    return [get_info_from_sidecar(sidecar, selected_fields) for sidecar in sidecars]