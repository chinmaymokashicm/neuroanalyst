# NeuroAnalyst Codebase Documentation

## Overview
NeuroAnalyst is a platform designed to launch containerized data pipelines focused on neuroimaging data in the BIDS (Brain Imaging Data Structure) format. The Core API (Aim 1) enables users to build, execute, and manage pipelines and processes efficiently. This documentation focuses on the implementation of Aim 1.

## Core API
The Core API provides functionality to:

1. **Build Process Images**: Process images are containerized environments built using Apptainer/Singularity. These images encapsulate the logic and dependencies required for specific neuroimaging tasks.
2. **Create Process Executions (Execs)**: Process execs are created by adding key metadata to execute process images. Metadata includes:
   - Container volumes: Volumes to mount onto the process container.
   - Environment variables: Variables to configure the container environment.
   - Other metadata: Name, description, and other relevant details.
3. **Construct Pipelines**: Pipelines are constructed by chaining together process execs. Each pipeline consists of multiple steps, where each step can have one or more execs.
4. **Execute Pipelines**: Pipelines are executed step-by-step, with each step running its associated execs in sequence.

## Key Features

### 1. BIDS-Compliant Output
- Output files are saved in the BIDS format under the `derivatives/[pipeline_name]` folder.
- Sidecar JSON files are generated for each input image file executed. These sidecars contain:
  - Name and description of the process.
  - Inputs and outputs.
  - Metrics generated during execution.

### 2. Centralized Metrics Storage
- After a pipeline step completes execution, the `metrics` field from the sidecar JSON files is migrated to a centralized MongoDB database.
- The database also stores identifiers such as `process_id`, `process_exec_id`, and `pipeline_id` for traceability.

### 3. Asynchronous Task Execution
- Compute/time-intensive tasks, such as building process images or executing pipelines, are offloaded to Celery workers.
- Redis is used as the message broker for Celery, enabling asynchronous execution.

## Code Structure

### Process Management
- **ProcessImageApptainer**: Represents a process image built using Apptainer/Singularity. Includes methods to:
  - Validate metadata.
  - Build the image.
  - Save the image configuration to the database.
- **ProcessExecApptainer**: Represents the execution plan for a process image. Includes metadata such as container volumes, environment variables, and execution commands.

### Pipeline Management
- **Pipeline**: Represents a sequence of steps, where each step consists of one or more process execs. Includes methods to:
  - Construct pipelines from user input.
  - Execute pipelines step-by-step.
  - Load and save metrics to the database.
- **PipelineStep**: Represents a single step in a pipeline. Includes methods to:
  - Execute all associated process execs in parallel.
  - Load and save metrics.

### Task Management
- **Celery Tasks**:
  - `build_process_image`: Builds Apptainer images for processes asynchronously.
  - `execute_process`: Executes a process asynchronously.
  - `run_pipeline`: Executes a pipeline asynchronously.

## Workflow

1. **Build Process Images**:
   - Define the process metadata (e.g., name, description, container volumes).
   - Use the `ProcessImageApptainer` class to build the image.
   - Save the image configuration to the MongoDB database.

2. **Create Process Execs**:
   - Define the execution metadata (e.g., environment variables, execution commands).
   - Use the `ProcessExecApptainer` class to create the execution plan.

3. **Construct Pipelines**:
   - Chain together process execs to form a pipeline.
   - Use the `Pipeline` class to define the pipeline structure and steps.

4. **Execute Pipelines**:
   - Trigger pipeline execution using the `run_pipeline` Celery task.
   - Monitor execution status and retrieve metrics from the MongoDB database.

## Example

### Building a Process Image
```python
from app.models.core.process import ProcessImageApptainer

process_image = ProcessImageApptainer.from_user(
    name="Example Process",
    tag="example-process",
    author="Researcher",
    description="An example process for neuroimaging data.",
    bootstrap="docker",
    base_image_from="python:3.10",
    working_directory={
        "root_dir": "/path/to/workdir",
        "main_file": "main.py",
        "requirements_file": "requirements.txt",
        "main_exec_prefix": "python",
        "requirements_exec_prefix": "pip install -r"
    }
)
process_image.build_image()
```

### Constructing and Executing a Pipeline
```python
from app.models.core.pipeline import Pipeline

pipeline = Pipeline.from_user(
    name="Example Pipeline",
    author="Researcher",
    description="A pipeline for processing neuroimaging data.",
    process_exec_ids=["exec1", "exec2"]
)
pipeline.execute()
```

## Future Work
- **Insight API (Aim 2)**: The next phase will focus on enabling users to query the database for insights and integrate scientific literature into the results.