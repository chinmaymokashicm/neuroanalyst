# NeuroAnalyst API

This directory contains the FastAPI implementation for the NeuroAnalyst framework's web API.

> **Note**: This documentation reflects the currently implemented endpoints. Some features mentioned in the project roadmap (such as execution endpoints) are not yet implemented.

## Overview

The API provides endpoints to interact with the NeuroAnalyst framework, allowing users to:

- Create and manage NeuProcesses
- Build and execute neuroimaging pipelines
- Monitor execution status and retrieve results

## API Structure

The API is organized into the following routers:

- **Logic Router** (`/api/v1/logic/*`): Endpoints for NeuProcessLogic operations including encoding, decoding, and validation
- **Process Router** (`/api/v1/process/*`): Endpoints for NeuProcessDir and NeuProcess operations
- **Pipeline Router** (`/api/v1/pipeline/*`): Endpoints for creating and managing NeuPipeline objects
- **Logs Router** (`/api/v1/logs/*`): Endpoints for retrieving and streaming log files from various components

## Running the API

The API server can be started using the provided `run_api.sh` script:

```bash
./run_api.sh
```

This will start the server on port 8000, and you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Documentation

### Logic Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/logic/` | POST | Create a new NeuProcessLogic |
| `/api/v1/logic/encode` | POST | Encode a Python function as a NeuProcessLogic |
| `/api/v1/logic/decode` | POST | Decode an encoded NeuProcessLogic function |
| `/api/v1/logic/{logic_name}` | GET | Get information about a specific NeuProcessLogic |
| `/api/v1/logic/` | GET | List all available NeuProcessLogic functions |

### Process Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/process/dir` | POST | Create a new NeuProcessDir |
| `/api/v1/process/` | POST | Create a new NeuProcess |
| `/api/v1/process/{process_id}` | GET | Get information about a specific NeuProcess |
| `/api/v1/process/` | GET | List all available NeuProcesses |

### Pipeline Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/pipeline/` | POST | Create a new NeuPipeline |
| `/api/v1/pipeline/{pipeline_id}` | GET | Get information about a specific pipeline |
| `/api/v1/pipeline/` | GET | List all available pipelines |

### Logs Endpoints

| Endpoint | Method | Description | Query Parameters |
|----------|--------|-------------|-----------------|
| `/api/v1/logs/image/{process_id}` | GET | Get image build logs for a process | `date_str`: Optional date string in format YYYYMMDD_HHMMSS |
| `/api/v1/logs/venv/{process_id}` | GET | Get venv build logs for a process | `date_str`: Optional date string in format YYYYMMDD_HHMMSS |
| `/api/v1/logs/pipeline/{pipeline_id}` | GET | Get logs for a pipeline execution | None |
| `/api/v1/logs/process_exec/{exec_id}` | GET | Get logs for a process execution | `error`: Whether to retrieve error log instead of standard output (default: false) |
| `/api/v1/logs/list` | GET | List available logs by type and optional ID | `type`: Type of logs to list (image, venv, pipeline, process_exec)<br>`id`: Optional ID to filter logs by |

## Implementation Notes

- The API uses Pydantic models for request and response validation
- Authentication is not currently implemented but can be added in the future
- All data is currently stored in the file system, with database integration planned for future versions
- Execution endpoints for running processes and pipelines are planned but not yet implemented
- The logs router provides functionality to stream logs from various components