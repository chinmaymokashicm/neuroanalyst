import sys

from src.neuroanalyst.models.pipeline import NeuPipeline

pipeline_id: str = str(sys.argv[1])

pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id)
pipeline.reset_pipeline_status()