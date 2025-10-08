from neuroanalyst.models.pipeline import NeuPipeline

import logging, sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pipeline_id: str = str(sys.argv[1])

pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id)

result: str = pipeline.execute_via_python(logger=logger, resume=True)