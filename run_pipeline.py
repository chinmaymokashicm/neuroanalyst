from src.neuroanalyst.models.pipeline import NeuPipeline
from src.neuroanalyst.utils import NeuroAnalystPaths

import logging, sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pipeline_id: str = str(sys.argv[1])

# Set up file handler for logging
paths = NeuroAnalystPaths()
logs_dir = paths.logs

log_file_path = f"{logs_dir}/pipelines/{pipeline_id}/{pipeline_id}.log"
file_handler = logging.FileHandler(log_file_path, mode='a')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id)

result: str = pipeline.execute_via_python(logger=logger, resume=True)