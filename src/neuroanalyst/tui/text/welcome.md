# NeuroAnalyst

NeuroAnalyst is a comprehensive framework for standardizing and automating neuroimaging data processing workflows. It transforms Python functions into complete, BIDS-compliant processing pipelines with containerized execution, rich metadata management, and high-performance computing integration.

<p align="center">
  <img src="docs/img/logos/logo_1.png" alt="NeuroAnalyst Logo" width="200"/>
</p>

## Key Features

- **Function-to-Pipeline Transformation**: Convert Python functions into complete processing workflows
- **Dataset- and computing- agnostic process building**: Build processes from functions that do not worry about the environment or the dataset
- **BIDS Compliance**: Automatic dataset validation and metadata generation
- **Containerization**: Generate Singularity containers or python virtual environments with all dependencies
- **Template-Based Generation**: Standardized script and container creation
- **HPC Integration**: Optimized for high-performance computing environments (SLURM, PBS, LSF)
- **Pipeline Orchestration**: Build complex workflows with dependency management

## How to Use NeuroAnalyst

- **Logic**: Write python functions, convert them into logical units
- **Process**: Convert logic to process directories and containerized environments (python virtual environments or Singularity images)
- **Pipeline**: Arrange processes into pipelines and set runtime parameters. Execute these pipelines in local or HPC environments