# NeuroAnalyst API

This directory contains the FastAPI-based web API for the NeuroAnalyst framework. The API provides endpoints to interact with the core components of NeuroAnalyst, such as NeuProcesses, NeuPipelines, and their executions.

## Overview

The API is organized into several routers, each handling a specific aspect of the NeuroAnalyst framework:

- **Logic Router**: Endpoints for encoding and decoding user-defined functions.
- **NeuProcessDir Router**: Endpoints for creating and managing NeuProcessDir instances.
- **NeuProcess Router**: Endpoints for creating and managing NeuProcess instances.
- **NeuProcessExec Router**: Endpoints for creating and managing NeuProcessExec instances.
- **NeuPipeline Router**: Endpoints for creating and managing NeuPipeline instances.
- **Dataset Router**: Endpoints for listing and filtering datasets.
- **BIDS Router**: Endpoints for extracting BIDS entities from file names.

## Running the API

### Starting the API Server

To start the API server, run:

```bash
cd /path/to/neuroanalyst
python -m neuroanalyst.scripts.run_api --host 0.0.0.0 --port 8000 --reload
```

This will start the API server on the specified host and port with auto-reload enabled (for development).

### API Documentation

Once the API server is running, you can access the auto-generated documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing the API

A test script is provided to demonstrate how to interact with the API endpoints:

```bash
cd /path/to/neuroanalyst
python -m neuroanalyst.scripts.test_api
```

You can also test specific endpoints:

```bash
# Test only the logic endpoints
python -m neuroanalyst.scripts.test_api --logic

# Test only the process endpoints
python -m neuroanalyst.scripts.test_api --process
```

## API Endpoints

### Logic Endpoints

- `POST /logic/encode`: Encode a user-defined function into a pydantic model.
- `POST /logic/decode`: Decode a pydantic model into a user-defined function.

### NeuProcessDir Endpoints

- `POST /dir/create/logic`: Create a new NeuProcessDir from NeuProcessLogic.

### NeuProcess Endpoints

- `GET /process/all`: Get a list of all NeuProcesses.
- `GET /process/{process_id}`: Get details of a specific NeuProcess.
- `POST /process/create`: Create a new NeuProcess from a NeuProcessDir.
- `POST /process/{process_id}/build_image`: Build the Singularity image for a specific NeuProcess.
- `POST /process/{process_id}/create_venv`: Create the virtual environment for a specific NeuProcess.
- `DELETE /process/{process_id}`: Delete a specific NeuProcess and its associated image and venv.

### NeuProcessExec Endpoints

- `POST /process/exec/create`: Create a new NeuProcessExec instance.
- `GET /process/exec/{exec_id}`: Get details of a specific NeuProcessExec.
- `POST /process/exec/{exec_id}/generate_command`: Generate the execution command for a specific NeuProcessExec.
- `DELETE /process/exec/{exec_id}`: Delete a specific NeuProcessExec.

### NeuPipeline Endpoints

- `POST /pipeline/create`: Create a new NeuPipeline from a list of NeuProcessExec instances.
- `GET /pipeline/{pipeline_id}`: Get details of a specific NeuPipeline.
- `GET /pipeline/all`: Get a list of all NeuPipelines.
- `POST /pipeline/{pipeline_id}/generate_script`: Generate the execution script for a specific NeuPipeline.
- `DELETE /pipeline/{pipeline_id}`: Delete a specific NeuPipeline and its associated directory.

### Dataset Endpoints

- `GET /dataset/all`: Get a list of all datasets.
- `GET /dataset/{dataset_id}`: Get details of a specific dataset.
- `POST /dataset/{dataset_id}/filter`: Get a list of files in a specific dataset that match the provided BIDS filters.

### BIDS Endpoints

- `GET /bids/entities/file_name`: Get the BIDS entities of a specific file given its name.

## Implementation Notes

The current implementation provides placeholders for the actual business logic. Integration with the NeuroAnalyst core functionality will be completed in subsequent development phases.
