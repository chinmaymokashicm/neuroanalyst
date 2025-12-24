import sys

from src.neuroanalyst.models.pipeline import NeuPipeline

pipeline_id: str = str(sys.argv[1])
username: str = str(sys.argv[2])

pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id, username=username)
pipeline.reset_pipeline_status()