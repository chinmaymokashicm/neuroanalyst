from ..models.core.process import ProcessImageApptainer, ProcessExecApptainer
from ..models.core.pipeline import PipelineStep, Pipeline
from ..utils.db import find_many_from_db, find_one_from_db
from ..utils.constants import COLLECTION_PROCESS_IMAGES, COLLECTION_PROCESS_EXECS, COLLECTION_PIPELINES
from ..utils.envs import set_neuroanalyst_root_dirs, get_neuroanalyst_root_dirs

from pathlib import Path, PosixPath
import re

from imagelib.datasets.bids import SelectBIDSDatasetInfo

def convert_all_process_images_to_table() -> list[dict]:
    """
    Convert all process images to a table format.
    """
    process_image_ids: list[str] = [result["id"] for result in find_many_from_db(COLLECTION_PROCESS_IMAGES, {}, field_names=["id"])]
    process_images: list[ProcessImageApptainer] = []
    for process_image_id in process_image_ids:
        try:
            process_images.append(ProcessImageApptainer.from_db(id=process_image_id))
        except Exception as e:
            print(e)
    return [
        {
            "id": process_image.id,
            "name": process_image.name,
            "description": process_image.description,
            "created_at": process_image.created_at.isoformat(),
            "bootstrap": process_image.bootstrap.value,
            "base_image_from": process_image.base_image_from,
        }
        for process_image in process_images
    ]
    
def convert_all_process_execs_to_table() -> list[dict]:
    """
    Convert all process executions to a table format.
    """
    # process_execs_dict: list[dict] = find_many_from_db(COLLECTION_PROCESS_EXECS, {})
    process_exec_ids: list[str] = [process_exec_dict["id"] for process_exec_dict in find_many_from_db(COLLECTION_PROCESS_EXECS, {}, field_names=["id"])]
    
    process_execs: list[ProcessExecApptainer] = []
    for process_exec_id in process_exec_ids:
        try:
            process_exec: ProcessExecApptainer = ProcessExecApptainer.from_db(id=process_exec_id)
            process_execs.append(process_exec)
        except Exception as e:
            print(e)
    
    # process_execs: list[ProcessExecApptainer] = [ProcessExecApptainer.from_db(id=process_exec_id) for process_exec_id in process_exec_ids]
    
    return [
        {
            "id": process_exec.id,
            "process_image": process_exec.process_image.name,
            "command": process_exec.command
        }
        for process_exec in process_execs
    ]

def convert_all_pipeline_steps_to_table(pipeline_id: str) -> list[dict]:
    """
    Convert all pipeline steps to a table format.
    """
    pipeline: Pipeline = Pipeline.from_db(pipeline_id)
    
    return [
        {
            "id": step.id,
            "name": step.name,
            "process_execs": [process_exec.id for process_exec in step.process_execs],
            "status": step.status
        }
        for step in pipeline.steps
    ]
    
def convert_all_pipelines_to_table() -> list[dict]:
    """
    Convert all pipelines to a table format.
    """
    pipeline_ids: list[str] = [pipeline_dict["id"] for pipeline_dict in find_many_from_db(COLLECTION_PIPELINES, {})]
    
    pipelines: list[Pipeline] = []
    
    for pipeline_id in pipeline_ids:
        try:
            pipeline: Pipeline = Pipeline.from_db(pipeline_id=pipeline_id)
            pipelines.append(pipeline)
        except Exception as e:
            print(e)
            
    # pipelines: list[Pipeline] = [Pipeline.from_db(pipeline_id=pipeline_id) for pipeline_id in pipeline_ids]

    return [
        {
            "id": pipeline.id,
            "name": pipeline.name,
            "author": pipeline.author,
            "description": pipeline.description,
            "n_steps": len(pipeline.steps),
            "checkpoint_steps": pipeline.checkpoint_steps
        }
        for pipeline in pipelines
    ]
    
def convert_all_workdirs_to_table() -> list[dict]:
    """
    Convert all workdirs to a table format.
    """
    skip_subdirs = ["venv*"]
    # set_neuroanalyst_root_dirs()
    neuroanalyst_workdir_root = get_neuroanalyst_root_dirs("workdir")
    if isinstance(neuroanalyst_workdir_root, dict):
        raise ValueError("Expected a string but got a dictionary.")
    root_dir: PosixPath = PosixPath(neuroanalyst_workdir_root)
    if root_dir is None:
        return []
    subdirs: list[dict] = []
    for subdir in root_dir.iterdir():
        if subdir.is_dir() and not any(re.match(pattern, subdir.name) for pattern in skip_subdirs):
            subdirs.append(
                {
                    "name": subdir.name, 
                    "path": str(subdir)
                }
            )
    return subdirs

def convert_all_datasets_to_table(get_derivatives: bool = False) -> list[dict]:
    """
    Convert all datasets to a table format.
    """
    skip_subdirs = ["venv*"]
    # set_neuroanalyst_root_dirs()
    neuroanalyst_datasets_root: str | dict = get_neuroanalyst_root_dirs("datasets")
    if isinstance(neuroanalyst_datasets_root, dict):
        raise ValueError("Expected a string but got a dictionary.")
    neuroanalyst_datasets_root_path = PosixPath(neuroanalyst_datasets_root)
    if neuroanalyst_datasets_root is None:
        return []
    
    dataset_paths: list[PosixPath] = [subdir for subdir in neuroanalyst_datasets_root_path.iterdir() if subdir.is_dir() and not any(re.match(pattern, subdir.name) for pattern in skip_subdirs)]
    rows: list[dict] = []
    for dataset_path in dataset_paths:
        dataset_info: SelectBIDSDatasetInfo = SelectBIDSDatasetInfo.from_path(dataset_path, get_derivatives=get_derivatives)
        row: dict = {
            "id": dataset_path.name,
            "path": str(dataset_info.bids_root),
            "n_files": len(dataset_info.bids_files),
            "description": dataset_info.dataset_description.Name,
            "authors": ", ".join(dataset_info.dataset_description.Authors or []),
            "get_derivatives": get_derivatives,
        }
        rows.append(row)
    return rows