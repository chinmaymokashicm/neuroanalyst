# NeuroAnalyst Documentation

## Overview
NeuroAnalyst is a platform designed to launch containerized data pipelines focused on neuroimaging data in the BIDS (Brain Imaging Data Structure) format. It provides insights to user queries by combining pipeline/process provenance with metrics generated from these pipelines and relevant scientific literature.

## Project Structure
The main code for the application resides under the `app/` directory. Below is an overview of the key components:

- **FastAPI**: Used to create endpoints for managing pipelines and processes.
- **MongoDB**: Stores entities such as `Process`, `ProcessExec`, and `Pipeline`, along with metrics extracted from pipeline results.
- **Celery + Redis**: Handles asynchronous execution of time-consuming tasks like building process images and executing pipelines.
- **Singularity Containers**: Built in an HCP (High-Performance Computing) environment to containerize pipelines.
- **BIDS Derivatives**: Results are stored under the input BIDS dataset in `derivatives/[pipeline-name]` following BIDS conventions. Metrics are also migrated to the MongoDB database for centralized use.

## Features

### 1. Containerized Pipelines
- Pipelines are containerized using Singularity in an HCP environment.
- FastAPI endpoints manage the creation of `Process`, `ProcessExec`, and `Pipeline` entities in the MongoDB database.

### 2. Asynchronous Task Execution
- Time-consuming tasks such as building process images and executing pipelines are offloaded to Celery workers.
- Redis is used as the message broker for Celery.

### 3. Results Storage
- Pipeline results are stored in the input BIDS dataset under `derivatives/[pipeline-name]`.
- Sidecar JSON files contain metrics that are migrated to the MongoDB database.

### 4. Insight API (Planned)
- The Insight API will allow users to query the database for relevant information.
- It will refine research questions and fetch the most relevant scientific literature via an external API.
- The refined question will be searched on selected papers, and the answer will be returned to the user.

## Getting Started

### Prerequisites
- Python 3.10+
- MongoDB
- Redis
- Singularity

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd neuroanalyst
   ```
2. Install dependencies:
   ```bash
   ./install_requirements.sh
   ```
3. Set up environment variables:
   ```bash
   source set_envs.sh
   ```

### Running the Application
1. Start MongoDB:
   ```bash
   ./run_mongodb.sh
   ```
2. Start Redis:
   ```bash
   ./run_redis.sh
   ```
3. Start Celery workers:
   ```bash
   ./run_celery_worker.sh
   ```
4. Start the FastAPI server:
   ```bash
   ./run_fastapi.sh
   ```

## Usage

### FastAPI Endpoints
- Use the FastAPI endpoints to create and manage pipelines and processes.
- Documentation for the API is available at `/docs` when the server is running.

### BIDS Derivatives
- Results are stored in the `derivatives/[pipeline-name]` directory of the input BIDS dataset.
- Metrics are automatically migrated to the MongoDB database.

### Insight API (Future Work)
- The Insight API will enable querying the database and integrating scientific literature into the results.

## Additional Context

### Processes and Working Directories
- The `processes/` directory contains subdirectories for each process, named with unique identifiers (e.g., `PR-000343/`).
- The `working_dirs/` directory contains subdirectories for specific tasks such as `brain_extraction/`, `regional_volumes/`, and more.

### Logs and Outputs
- Logs are stored in the `logs/` directory, including application logs (`app.log`) and other relevant logs.
- Outputs from Redis and other components are stored in the `outputs/` directory.

### Documentation and References
- Additional documentation is available in the `docs/` directory, including `introduction.md` and references.
- Templates for various configurations are stored in the `templates/` directory.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any bugs or feature requests.

## License
This project is licensed under the MIT License.