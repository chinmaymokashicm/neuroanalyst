# NeuroAnalyst
- Read docs/img/architecture/ for architecture diagrams.

## System Nodes Overview
This system runs across three main node types, each with distinct roles:

### 1. Compute Node (HPC)
- Executes computationally intensive tasks (pipelines, processes).
- Runs jobs in batch mode (no long-running daemons).
- Optimized for parallelized neuroimaging workloads.
- Communicates results/logs to the DB node after job completion.

### 2. Database (DB) Node
- Central data storage and management server.
- Hosts pipeline metadata, logs, and results.
- Provides structured access for querying and integration.
- Isolated from the App node per cybersecurity rules.

### 3. Application (App) Node
- Runs the web application and APIs.
- Provides user interface for submitting jobs, tracking progress, and retrieving results.
- Communicates with the DB node for data access.
- Submits jobs to the Compute node for execution.

---
**Security Model**:  
- DB and App must run on separate servers.  
- HPC nodes cannot host persistent services.  

## Log and Result Flow
### Workflow

1. **During Job Execution (Compute Node)**
   - Logs and intermediate results are written locally on the compute node.
   - Stored in temporary job-specific directories.

2. **After Job Completion**
   - Final logs and results are packaged for persistence.
   - Data is queued for transfer.

3. **Sync with Database (DB Node)**
   - Transfer occurs **ad-hoc (on-demand)** or **periodically** (e.g., scheduled sync).
   - DB node stores results in structured form for querying and retrieval.

#### Key Points
- Compute nodes never hold long-term data.  
- DB node is the authoritative store of logs and results.  
- Sync strategy (ad-hoc vs. periodic) can be tuned per workload.  

## Job Submission Workflow (HPC + NeuroAnalyst)

This document outlines how jobs are submitted and managed for NeuroAnalyst on the HPC system.

### 1. Create **NeuProcessDir**
- Purpose: Define and prepare a process directory on the HPC.
- Options:
  - **From logic**: Use `NeuProcessLogic` to generate preparation scripts and required files.
  - **From scripts**: Provide all necessary scripts directly, and wrap them into a `NeuProcessDir`.
- Storage:
  - **HPC**: `NeuProcessDir` directory created in project storage (persistent, not scratch).
  - **DB (MongoDB)**: `NeuProcessDir` component metadata stored for tracking and reuse.

### 2. Create **NeuProcess**
- Purpose: Build a runnable container image of the process.
- Execution:
  - Trigger build of a **Singularity image** from the `NeuProcessDir`.
- Storage:
  - **HPC**: Singularity image saved in project storage (persistent).
  - **DB (MongoDB)**: `NeuProcess` component metadata stored with link to the image.

### 3. Trigger **NeuPipeline**
- Purpose: Execute a pipeline composed of multiple processes.
- Execution:
  - Submit pipeline as a sequence of `NeuProcessExec` jobs to the HPC scheduler (with job dependencies).
  - Each process runs inside its respective Singularity container.
- Storage:
  - **HPC (datasets)**: 
    - Results written to:
      `[root]/derivatives/[pipeline_name]/`
    - Logs stored alongside results.
    - Temporary/intermediate files stored in **scratch**, then synced to project storage.
  - **DB (MongoDB)**:
    - `NeuPipeline` component updated with progress and completion states.
    - Logs may be synced periodically by stewards.

### About NeuProcessExec
- Represents a single execution instance of a NeuProcess.
- If attached to a NeuProcess, the expectation is to execute the process as a Singularity container.
- If attached to a NeuProcessDir, the expectation is to execute the process as a script (not containerized) within a virtual environment.
- NeuProcessExec instances should hold all the required information to execute a process. The NeuProcess or NeuProcessDir should not be executed on its own as it does not have all the required information to run (i.e. the root BIDS path, BIDS filters, mounted paths, environment variables).
- NeuProcess or NeuProcessDir instances tell the user what values are mandatory for it to run successfully, while the exec instances actually hold the values. This allows the process or dir instances to be independent of pipelines or datasets, but remain purely as code.

---

### Tracking & Stewards
- **Pipeline Stewards** created at pipeline launch:
  - Monitor job status via HPC scheduler (e.g., `bjobs`).
  - Update DB with progress states (`Waiting → Running → Complete/Failed`).
  - Collect and sync logs/results to DB or designated storage.
- **Logs**:
  - First written to HPC storage (scratch or project dir).
  - Synced periodically/ad-hoc with DB.

---

## Notes
- Additional job types (e.g., QC validation, cleanup, data sync) can be added in the future.
- Jobs always run under HPC scheduler constraints (no daemons).
- Scratch space is used for temporary execution; persistent results live in project storage.



## Setup
- Run setup.sh - sets up the environment, installs dependencies, and sets environment variables.
- Note - these environment variables are crucial for the proper functioning of the NeuroAnalyst framework. NeuroAnalyst home, images, docs, workdir, reports, logs, datasets are defined from here. These envs will be used throughout the codebase.

## Core API
- There will be two classes of NeuProcess - Operators and Stewards.
- Operators are the ones that perform the actual processing, while Stewards are the ones that manage the system (e.g. state, logs, data hygiene, syncing, etc.).
- Below is the core API that will be used to create NeuProcesses and NeuPipelines. The NeuProcesses here will be of the Operator kind.

### Create NeuProcess
![Option 1](docs/img/architecture/Create%20NeuProcess.png)

#### Option 1 | Use NeuProcessLogic
1. Create NeuProcessLogic
    There are two kinds of NeuProcessLogic - one that would be executed on individual files, the other with a bulk functionality.
    - Level: File
        - Take a user-defined function [currently only python] that only performs computations without worrying about any NeuroAnalyst architecture.
        - Prepare an encoder that programmatically generates a python function and decodes a python function string into a pydantic model.
        - UDF only takes one mandatory arg - input_filepath (relative to BIDS root directory).
        - Use $BIDS_ROOT as root of the dataset to access related or associated data (e.g. if dwi nifti is given, use pybids to access the corresponding bvec and bval files).
        - Returns - {<output file data>, {metrics dict}, {output BIDS file entities as dict that would be used to construct the output file path later}, [optional - any output filepaths (relative to BIDS root) that were forcibly written in the function so that they can be removed]}
    - Level: Bulk
        - Here, the UDF operates on the entire dataset at once. The logic for choosing files, iterating through them, etc. is left to the user.
        - Saving data - use $BIDS_ROOT as root of the dataset and save data accordingly. Return metrics as dict. Sidecar JSON files should also be created that are saved in 'bulk' sub-dir in the root.
        - Pros: more flexibility for complex workflows, aggregation operations.
        - Cons: potentially higher memory usage, less control over individual file processing, no scope for multiprocessing.

2. Decorator wrapper (**only for the file level NeuProcessLogic**)
    - Wrap around the NeuProcessLogic such that - the output data is written to a BIDS-appropriate output path (it takes args from the user when creating the NeuProcess such as pipeline_name, as well as desired output file BIDS entities returned by the function) which is constructed using the input path. 
    - Write all metadata, such as metrics, and filepaths and process description/docstrings into sidecar JSON files with the same name as the output file.

3. Wrap NeuProcessLogic into NeuProcessDir
    - Construct 2 scripts - one is **main.py** that takes in input args from the user (such as pipeline_name, BIDS_FILTERS, and the BIDS root path), extracts the relevant files that need to be processed, and executes the processing function. The other script would be **install_requirements.sh** that is also provided by the user that simply installs everything that needs to be installed into the SIngularity image.
    - If the NeuProcessLogic is of level file, processing can be optionally done in parallel using python multiprocessing (number of cores can be specified by the user). If it is of level bulk, the function is simply executed once.
    - The user also needs to select an already present base image to build the Singularity image on, or provide the name of the base image that can be pulled from the web. There should be an option to choose from existing base images or downloading a base image from the web.
    - Large popular packages that could be available on the HPC environment include FreeSurfer, FSL, and others can be mounted onto the Singularity image when it is built from NeuProcessDir. 

4. Create NeuProcess Singularity/Apptainer image
    <!-- - The image is going to be executed in HPC environments that already have popular and large packages installed such as FreeSurfer and FSL. Allow the user to mount these packages onto the image so that we do not need to install them every build. -->
    - When creating image, user needs to provide all the required input args and environment variables that will be required to execute the spawned container. 
    - For security purposes, we will not be executing NeuProcess barebones but only as Singularity images, and we will be only mounting the BIDS dataset of interest as accessible (read-only) while only the [BIDS root]/derivatives/[pipeline_name] sub-dir will have write access since that is where all the output should go.

#### Option 2 | Provide installation and execution scripts
1. Create NeuProcessDir
    - Directly provide the installation and execution scripts. **install_requirements.sh** should install all required packages while **main.[extension]** script executes the logic of the process.

2. Create NeuProcess image
    - This will be similar to the previous option, except that the user will also need to provide the interpreter to run the main script (e.g. python main.py) or the command to execute it, in general. 

| Option | Pros | Cons |
|--------|------|------|
| **Option 1: Use NeuProcessLogic** | - Simplifies user logic by abstracting NeuroAnalyst architecture.<br>- Automatic handling of BIDS paths, metadata, and output organization.<br>- Decorator-based workflow for easier integration.<br>- Programmatic encoder/decoder for Python UDFs.<br>- Streamlined parallel execution and containerization. | - Currently limited to Python functions.<br>- Requires adherence to NeuroAnalyst's function signature and workflow.<br>- Less flexibility for custom installation or execution steps. |
| **Option 2: Provide installation and execution scripts** | - Greater flexibility in scripting and language choice.<br>- User controls installation and execution logic.<br>- Can support non-Python workflows. | - User must manually handle BIDS paths, metadata, and output organization.<br>- More responsibility on user for correct setup.<br>- Requires explicit interpreter/command specification. |

### NeuProcessDir
- The code for the NeuProcessDir class is located in the `app/models/process/dir` directory. The main file is `core.py`.
- The NeuProcessDir object is used to do the following-
    - Generate working directory for a process.
    - The process directory can then be executed as is (except passing runtime execution information such as environment variables, BIDS root path, etc.). All the information about the process and executing will be found in this directory.
    - Provide the necessary information to the downstream NeuProcess instance about actions such as building a Singularity image (if necessary), required container mounts that need values, environment variable values that need to be set, etc. This will eventually be used to generate execution commands for the NeuProcess for whatever condition the user needs it to be (e.g. running on a HPC-LSF but by creating an image and executing the image).
- There should be two ways to generate the NeuProcessDir:
    1. Using the NeuProcessLogic to automatically create the directory structure and files.
    2. Manually creating the directory structure and files as needed.
    - For now, let us only focus on the first option.
    - Create classmethods such as `from_logic` and `from_scripts` to create the NeuProcessDir instance.
- The NeuProcessDir generates the working directory code that will be used to execute the NeuProcess, either as a script or as a Singularity image.
- The working directories will be stored by default in the neuroanalyst working dirs env variable path. The name of the dir will be the process id of the NeuProcessDir instance, i.e. PR-XXXXXX.
- The user needs to provide the following-
    - Binds: list of paths that need to be mounted onto the container or symlinked within the process dir if executing as a script.
    - Environment variables: list of environment variables that need to be set when executing the process.
- Here is how the directory should look like. Use template files to generate these files. Keep the template scripts descriptive and production-grade-
    - There should always be these scripts-
        - install_requirements.sh - This script will install all the necessary dependencies for the process. The dependency installment could be within a virtual environment or within the Singularity image itself.
        - main.* - This script will execute the main logic of the process. Currently, when we are using NeuProcessLogic to build the process, this will be a python file. Support for other languages could be added in the future. When we are using NeuProcessLogic, there should be a udf.py as well as a decorator.py to house the relevant code. We keep this code separate for readability and to avoid import conflicts.
    - These config files should also be available for reproducibility of the process-
        - config.json - This file contains all the configuration information about the process, such as base packages, python packages, author, description, etc.
        - model.json - This file contains the complete pydantic model dump of the NeuProcessDir instance. It is useful for validation and reconstruction of the instance.
    - Singularity definition file - PR-XXXXXX.def - This file will be used to build the Singularity image. The name of the file should be the same as the process id of the NeuProcessDir instance.
    - The following build scripts should also be available within sub-dir `build`-
        - image.sh - This script will build the Singularity image from the Singularity definition file. The image will be stored in the neuroanalyst images/ sub-dir. The name of the image should be the same as the process id of the NeuProcessDir instance, i.e. PR-XXXXXX.sif.
        - venv.sh - This script will create a virtual environment in the neuroanalyst workdir/venvs/ sub-dir if it does not already exist. The name of the venv should be the same as the process id of the NeuProcessDir instance. It will install all the necessary dependencies within this venv.
    - The following execution scripts should also be available within sub-dir `execute`-
        - sub-dir `hpc` - contains scripts that are compatible with HPC environments, currently for SLURM, PBS, and LSF schedulers. For each scheduler, there should be two scripts - one to execute the process as a container, and one to create a virtual environment and execute the process as a script, i.e. `execute/hpc/lsf/run_container.sh`, `execute/hpc/lsf/run_venv.sh`, etc.
        - sub-dir `local` - contains scripts that are compatible with local environments. Same as above, there should be two scripts - one to execute the process as a container, and one to create a virtual environment and execute the process as a script.
        - When running a script that executes a process as a container, make sure that the image has been built in the images/ sub-dir in the neuroanalyst dir (look at set_envs.sh and constants.py). If not, build the image successfully and only then execute the container.
        - When running a script that executes a process as a script, create a virtual environment in the neuroanalyst workdir/venvs/ sub-dir if it does not already exist. The name of the venv should be the same as the process id of the NeuProcessDir instance. Install all the necessary dependencies within this venv and only then execute the script.
    - Framework to construct the execute scripts-
        - For HPC execution scripts, I see directives/options in the beginning, while for local execution there are none as per my knowledge.
        - We set variables that will be used later in these scripts. 
        - We check if the image/venv exists, depending on whether the script is container or venv execute.
        - We parse the args that are provided with the script during runtime. Keep in mind, we are setting bind paths (internal paths are already fixed at this stage while the external paths will be provided at runtime) and environment variables (values will be set at runtime)
        - For venv execute scripts, we first activate the venv and then set up symbolic links of bind paths in the venv.
        - The execution command is constructed and saved to a variable.
        - We execute the command.
    - README.md - This file contains the documentation for the process, such as description, author, usage, etc. Show examples of execution for all scenarios - schedulers/local, script/container.
- When the main file is python and we are using NeuProcessLogic to create it, here is how it should look-
    - The UDF provided by the user should be embedded within the main.py script. This can be either bulk or file level.
    - We load the neuprocess decorator dynamically and put it into the main.py script and wrap the UDF with it.
    - We import all other dependent functions from the neuroanalyst package and put it directly into the script so that we do not need to install the package while maintaining transparency of the version of the code being used.

### Create NeuProcess
- The code for the NeuProcess class is located in `app/models/process/process` directory. The main file is `core.py`.
- NeuProcess takes a NeuProcessDir object, or path to a process directory, or simply the process ID (which can be used to construct the path). If directory path or process ID is provided, use the model.json file to construct the NeuProcessDir from it.
<!-- - The user also needs to mention if NeuProcess is going to be a Singularity image or as a script (within a virtual environment). -->
- NeuProcess loads the binds and environment variables from the NeuProcessDir instance.
- NeuProcess needs to have a method that will build the Singularity image from the Singularity definition file in the process directory. The image will be stored in the neuroanalyst images/ directory. The name of the image should be the same as the process id of the NeuProcess instance, i.e. PR-XXXXXX.sif.
- NeuProcess also needs a method that will generate the virtual environment in the NEUROANALYST_VENVS directory if it does not already exist. The name of the venv should be the same as the process id of the NeuProcess instance.

### Create NeuPipeline
1. Choose NeuProcesses in a sequence
   - Identify the individual NeuProcesses that will be part of the pipeline and their order of execution.
   - Create NeuProcessExec instances for each NeuProcess. This will involve providing the necessary configuration and dependencies for each process in this particular pipeline.

3. Create NeuPipeline
   - Create a NeuPipeline instance that encapsulates the sequence of NeuProcesses (+NeuProcessExecs).
   - Define the overall configuration for the pipeline, including metadata, author information, and versioning.

### NeuProcess - Stewards
- These NeuProcesses will also be Singularity images and will be executed as NeuProcessExec instances (containers).
- The idea behind the stewards is to manage the overall workflow, ensuring that the necessary resources are available and that the processing is carried out smoothly. They handle tasks such as monitoring, logging, and error handling, allowing the operators to focus on the actual data processing.
- Since the computation is performed on HPCs that are no-daemon environments, these images/containers can be executed ad-hoc or scheduled using a job scheduler without the need for a daemon process.
- Some steward processes that could be created include:
  - **NeuPipelineRunner**: Executes the entire pipeline, managing the execution order of NeuProcessExec instances.
  - **NeuProcessMonitor**: Monitors the execution of NeuProcesses, checking for errors and ensuring that outputs are generated correctly.
  - **NeuDataManager**: Handles data hygiene, syncing, and organization of input/output datasets across processes.
  - **NeuLogManager**: Manages logging and reporting of process execution, capturing metrics and performance data.
  - **NeuStateManager**: Maintains the state of the pipeline execution, including tracking progress and managing dependencies between processes.
  - **NeuSyncManager**: Synchronizes data between the HPCs and the other nodes, such as DB and App nodes.

```markdown
Additional Notes-
- Components to be created - NeuProcessLogic, NeuProcessDir, NeuProcess, NeuProcessExec, [wrapper on NeuProcessLogic].
- Use template files wherever applicable to keep the code clean and readable.
- Use pydantic wherever possible.
- Use pybids to iterate through BIDS dataset, and execute the UDF (which should be per-file for now) in parallel (maybe python multiprocessing?)
- Organize these modules neatly - for example, process/logic has all NeuProcessLogic related code, use process/dir for all NeuProcessDir related code.
- Prepare documentation for each module, and provide examples. Update main README.md at the root as we go along, and fix any issues/changes.
- Continue writing tests for each module as we go along.
- I have Singularity installed on my system (MacOS). It is installed within 'lima'. Use this for testing.