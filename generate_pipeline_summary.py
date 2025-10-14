from src.neuroanalyst.models.pipeline.core import NeuPipeline

import sys

pipeline_id: str = str(sys.argv[1])

pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id)

pipeline.generate_summary()