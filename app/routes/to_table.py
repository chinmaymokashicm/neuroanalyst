from ...models.core.process import ProcessExec, ProcessImage
from ...models.core.pipeline import PipelineStep, Pipeline
from ...utils.db import find_many_from_db, find_one_from_db
from ...utils.constants import COLLECTION_PROCESS_IMAGES, COLLECTION_PROCESS_EXECS, COLLECTION_PIPELINES

def convert_all_process_images_to_table() -> list[dict]:
    """
    Convert all process images to a table format.
    """
    process_images_dict: list[dict] = find_many_from_db(COLLECTION_PROCESS_IMAGES, {})
    process_images: list[ProcessImage] = [ProcessImage(**process_image_dict) for process_image_dict in process_images_dict]
    
    return [
        {
            "name": process_image.name,
            "description": process_image.description,
            "created_at": process_image.created_at.isoformat(),
            "base_docker_image": process_image.base_docker_image,
            "expected_outputs": ", ".join(process_image.expected_outputs),
            "n_stages": len(process_image.stages)
        }
        for process_image in process_images
    ]
    
def convert_all_process_execs_to_table() -> list[dict]:
    """
    Convert all process executions to a table format.
    """
    process_execs_dict: list[dict] = find_many_from_db(COLLECTION_PROCESS_EXECS, {})
    process_execs: list[ProcessExec] = [ProcessExec(**process_exec_dict) for process_exec_dict in process_execs_dict]
    
    return [
        {
            "id": process_exec.id,
            "process_image": process_exec.process_image.name,
            "command": process_exec.command,
            "docker_container_id": process_exec.docker_container_id,
        }
        for process_exec in process_execs
    ]

def convert_all_pipeline_steps_to_table(pipeline_id: str) -> list[dict]:
    """
    Convert all pipeline steps to a table format.
    """
    # pipeline: Pipeline = find_one_from_db(COLLECTION_PIPELINES, {"id": pipeline_id})
    pipeline: Pipeline = Pipeline.from_db(COLLECTION_PIPELINES, pipeline_id)
    
    return [
        {
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
    pipelines_dict: list[dict] = find_many_from_db(COLLECTION_PIPELINES, {})
    pipelines: list[Pipeline] = [Pipeline(**pipeline_dict) for pipeline_dict in pipelines_dict]
    
    return [
        {
            "name": pipeline.name,
            "id": pipeline.id,
            "description": pipeline.description,
            "n_steps": len(pipeline.steps),
            "checkpoint_steps": pipeline.checkpoint_steps
        }
        for pipeline in pipelines
    ]