# NeuPipeline

The NeuPipeline class provides a comprehensive solution for creating and managing neuroimaging pipelines composed of multiple NeuProcessExec instances organized into execution steps.

## Overview

NeuPipeline is responsible for:
1. Managing a sequence of pipeline steps (each with one or more NeuProcessExec instances)
2. Generating execution scripts for the entire pipeline with proper dependencies
3. Storing pipeline metadata for reproducibility

## Core Components

### NeuPipelineStep

A pipeline step contains one or more NeuProcessExec instances that can be executed in parallel. Steps are executed in sequence, with each step waiting for all processes in the previous step to complete before beginning.

```python
step = NeuPipelineStep(
    name="Preprocessing",
    description="Data preprocessing step",
    process_execs=[process_exec1, process_exec2]  # These will run in parallel
)
```

### NeuPipeline

A pipeline is a sequence of steps, where each step contains one or more process executions that can run in parallel. Steps are executed in sequence, with dependencies between them.

```python
pipeline = NeuPipeline(
    name="Example Pipeline",
    description="An example pipeline for neuroimaging data processing",
    version="0.1.0",
    about=About(
        name="Example User",
        email="example@example.com",
        organization="Example Organization"
    ),
    steps=[step1, step2, step3],
    scheduler=HPCScheduler.LSF  # Choose from LSF, SLURM, PBS, or LOCAL
)
```

## Creating and Executing a Pipeline

1. **Create NeuProcessExec instances** for each process in your pipeline
2. **Organize them into NeuPipelineSteps** based on dependency relationships
3. **Create a NeuPipeline** with all steps and configuration
4. **Generate the pipeline execution script** with `pipeline.create_pipeline_dir()`
5. **Execute the pipeline** with `pipeline.execute()` or by running the generated script

## Example Usage

```python
from src.neuroanalyst.models.about import About
from src.neuroanalyst.models.process.exec.core import NeuProcessExec, HPCScheduler
from src.neuroanalyst.models.pipeline.core import NeuPipeline, NeuPipelineStep

# Create process execs
process_exec1 = NeuProcessExec.create(
    process=process1,
    pipeline_name="example_pipeline",
    bids_root="/path/to/bids/dataset"
)

process_exec2 = NeuProcessExec.create(
    process=process2,
    pipeline_name="example_pipeline",
    bids_root="/path/to/bids/dataset"
)

# Create pipeline steps
step1 = NeuPipelineStep(
    name="Preprocessing",
    description="Data preprocessing step",
    process_execs=[process_exec1]
)

step2 = NeuPipelineStep(
    name="Processing",
    description="Data processing step",
    process_execs=[process_exec2]
)

# Create pipeline
pipeline = NeuPipeline(
    name="Example Pipeline",
    description="An example pipeline for neuroimaging data processing",
    version="0.1.0",
    about=About(
        name="Example User",
        email="example@example.com",
        organization="Example Organization"
    ),
    steps=[step1, step2],
    scheduler=HPCScheduler.LSF
)

# Create pipeline directory and generate execution script
pipeline_dir = pipeline.create_pipeline_dir()
print(f"Pipeline directory created at: {pipeline_dir}")

# Execute the pipeline
result = pipeline.execute()
print(result)
```

## Supported HPC Schedulers

The NeuPipeline class supports multiple HPC schedulers:

- **LSF**: IBM Spectrum LSF
- **SLURM**: Simple Linux Utility for Resource Management
- **PBS**: Portable Batch System
- **LOCAL**: Local execution (no scheduler)

Each scheduler has specific templates and command generation logic to ensure proper execution in different HPC environments.

## Pipeline Organization

When a pipeline is created, it generates:

1. **Pipeline Directory**: Contains all files needed for execution
2. **Model File**: JSON representation of the pipeline for reproducibility
3. **Execution Script**: Shell script with all commands and dependencies
4. **README**: Documentation of the pipeline and usage instructions

These files are stored in the `NEUROANALYST_PIPELINES` directory defined in the environment.
