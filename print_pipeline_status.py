from src.neuroanalyst.models.pipeline.core import NeuPipeline, NeuPipelineStatus

import sys, yaml

pipeline_name: str = sys.argv[1]  # Name of the pipeline to check status for
pipeline = NeuPipeline.from_pipeline_id(pipeline_name)

# Get percentage completion of each process exec in each step
status: NeuPipelineStatus = pipeline.get_pipeline_status()
stats: dict = status.get_stats()

# Print the stats as indented YAML
print(yaml.dump(stats, sort_keys=False))