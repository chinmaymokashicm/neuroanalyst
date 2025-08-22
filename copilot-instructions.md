# NeuroAnalyst
- Read docs/img/architecture/ for architecture diagrams.

## Setup
- Run setup.sh - sets up the environment, installs dependencies, and sets environment variables.
- Note - these environment variables are crucial for the proper functioning of the NeuroAnalyst framework. NeuroAnalyst home, images, docs, workdir, reports, logs, datasets are defined from here. These envs will be used throughout the codebase.

## Core API
### Create NeuProcess
![Option 1](docs/img/architecture/Create%20NeuProcess.png)
#### Option 1 | Use NeuProcessLogic

1. Create NeuProcessLogic
    - Take a user-defined function [currently only python] that only performs computations without worrying about any NeuroAnalyst architecture.
    - Prepare an encoder that programmatically generates a python function and decodes a python function string into a pydantic model.
    - UDF only takes one mandatory arg - input_filepath (relative to BIDS root directory).
    - Returns - {<output file data>, {metrics dict}, {output BIDS file entities as dict that would be used to construct the output file path later}, [optional - any output filepaths (relative to BIDS root) that were forcibly written in the function so that they can be removed]}

2. Decorator wrapper
    - Wrap around a decorator such that - the output data is written to a BIDS-appropriate output path (it takes args from the user when creating the NeuProcess such as pipeline_name, as well as desired output file BIDS entities returned by the function) which is constructed using the input path. 
    - Write all metadata, such as metrics, and filepaths and process description/docstrings into sidecar JSON files with the same name as the output file.

3. Wrap NeuProcessLogic into NeuProcessDir
    - Construct 2 scripts - one is **main.py** that takes in input args from the user (such as pipeline_name, BIDS_FILTERS, and the BIDS root path), extracts the relevant files that need to be processed, and executes the processing function in parallel. The other script would be **install_requirements.sh** that is also provided by the user that simply installs everything that needs to be installed into the SIngularity image. 
    - The user also needs to select an already present base image to build the Singularity image on, or provide the name of the base image that can be pulled from the web. There should be an option to choose from existing base images or downloading a base image from the web.

4. Create NeuProcess Singularity/Apptainer image
    - The image is going to be executed in HPC environments that already have popular and large packages installed such as FreeSurfer and FSL. Allow the user to mount these packages onto the image so that we do not need to install them every build.
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

### Create NeuPipeline
1. Choose NeuProcesses in a sequence
   - Identify the individual NeuProcesses that will be part of the pipeline and their order of execution.
   - Create NeuProcessExec instances for each NeuProcess. This will involve providing the necessary configuration and dependencies for each process in this particular pipeline.

2. Create NeuPipeline
   - Create a NeuPipeline instance that encapsulates the sequence of NeuProcesses (+NeuProcessExecs).
   - Define the overall configuration for the pipeline, including metadata, author information, and versioning.

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