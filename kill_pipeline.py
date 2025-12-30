from src.neuroanalyst.models.pipeline import NeuPipeline

import sys

pipeline_id: str = str(sys.argv[1])
username: str = str(sys.argv[2])
pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id, username=username)

if __name__ == "__main__":
    result: str = pipeline.kill_all_jobs()