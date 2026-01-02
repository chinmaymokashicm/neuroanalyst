from src.neuroanalyst.models.pipeline import NeuPipeline

import sys

pipeline_id: str = str(sys.argv[1])
pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id)

if __name__ == "__main__":
    result: str = pipeline.kill_all_jobs()