# NeuProcess
This module defines the Process component of NeuroAnalyst.

## Features
- Unitary code component that is designed to execute a singular task on a BIDS dataset.
- Designed to be part of a pipeline that consists of multiple such NeuProcesses.
- Can be executed either as a Singularity image/container, or barebones on the system.

## Running NeuProcess as barebones code
- Executes directly on the system, ideally within a virtual environment, if provided.
- Reduces requirement for Singularity - eliminating the complications of creating Singularity images.
- Currently executed as a bash script to accomodate any programming language.

### Steps
1. Create a NeuProcessLogic object
    - Provide programming language (current recommendation is only Python), logic (code in that logic), required input arguments, importing libraries statements, and other metadata (e.g. name and description).
    - Save to a DB or a repository for reusability.

2. Generation of NeuProcess
    - Provide path to virtual environment if exists, plus installation script if does not exist.
    - NeuProcess is generated and updated to a DB.

3. Execution as NeuProcessExec as part of a NeuPipeline
    - When part of a NeuPipeline, NeuProcessExec needs to be created for the NeuProcess.
    - NeuProcesExec defines the how the NeuProcess will be executed within this pipeline.
    - Includes generation of a bash script and the execution command of this script (including input arguments).

## Running NeuProcess as a Singularity image
    - Maintains reproducibility across environments, better for scientific replication.
    - Generates Singularity images with detailed documentation for operation.
    - Requires an execution script (script that executes the process logic) and an installation script (script that installs the requirements in the containerized environment).

### Steps
1. Submit information to create the image
    - About
    - Execution and installation scripts
    - Volumes that need to be mounted when executing
    - Environment variables that need to be set before execution

*[Optional]*
```markdown
- A NeuProcessLogic object can be created - this allows creation of the Singularity image in a standardized modular fashion.
- A standard wrapping framework will wrap the NeuProcessLogic object to create the execution and installation scripts, volumes and environment variables.
```

2. Generation of NeuProcess Singularity image
    - A Singularity image is generated and is made available when creating a pipeline.

3. Execution as NeuProcessExec as part of a NeuPipeline
    - As part of a NeuPipeline, NeuProcessExecs have to be created for every partaking NeuProcess.
    - NeuProcessExec defines how the NeuProcess will be executed. Includes container volumes, environment variables and the execution command.