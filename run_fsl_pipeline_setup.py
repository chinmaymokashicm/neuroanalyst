# %% [markdown]
# # Testing Pipelining Functionality

# %%
from src.neuroanalyst.models.about import About
from src.neuroanalyst.models.process.logic.code.python import (
    PythonEncoder, 
    PythonDecoder, 
    PythonEncoderConfig, 
    PythonDecoderConfig,
    encode_logic,
    decode_from_string
)
from src.neuroanalyst.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument, ProgrammingLanguage
from src.neuroanalyst.models.process.logic.code.base import CodeGenerationResult
from src.neuroanalyst.models.process.logic.code.python.decoder import PythonDecoder
from src.neuroanalyst.models.process.dir.core import NeuProcessDir, NeuProcessDirConfig
from src.neuroanalyst.models.process.process.core import NeuProcess
from src.neuroanalyst.models.process.exec.core import NeuProcessExec, HPCScheduler
from src.neuroanalyst.models.pipeline.core import NeuPipeline, NeuPipelineStep

import json, time

# %% [markdown]
# ## T1w pre-processing pipeline using FSL
# ### Plan
# 1. Create processes for individual steps-
#     - BET
#     - FAST Segmentation
#     - Thresholding
# 2. Create pipeline with runtime parameters

# %%
BIDS_ROOT: str = "/rsrch5/home/csi/cmokashi/neuroanalyst/datasets/ds004884-1.0.2"
BASE_IMAGE: str = "/rsrch5/home/csi/cmokashi/neuroanalyst/apptainer/images/python_3.12_slim_amd64_git.sif"
FSL_IMG: str = "/risapps/apptainer/repo/fsl/3.16.8/fsl_3.16.8.sif"
EXECUTION_MODE: str = "container"

# %% [markdown]
# ### Load NeuProcessLogic instances

# %%
decoder = PythonDecoder()

functions: dict = {
    "fsl_bet": {
        "about": About(
            name="FSL BET",
            description="Brain Extraction Tool (BET) from FSL",
            version="1.0.0",
            author="Chinmay Mokashi"
        ),
        "file_path": "./src/neuroanalyst/models/process/logic/code/python/samples/fsl_bet.py",
        # "file_path": "./src/neuroanalyst/models/process/logic/code/python/samples/fake_fsl_bet.py",
    },
    "fsl_fast": {
        "about": About(
            name="FSL FAST",
            description="FSL FAST Segmentation",
            version="1.0.0",
            author="Chinmay Mokashi"
        ),
        "file_path": "./src/neuroanalyst/models/process/logic/code/python/samples/fsl_fast.py",
        # "file_path": "./src/neuroanalyst/models/process/logic/code/python/samples/fake_fsl_fast.py",
    },
    "fsl_threshold": {
        "about": About(
            name="FSL Threshold",
            description="FSL Thresholding",
            version="1.0.0",
            author="Chinmay Mokashi"
        ),
        "file_path": "./src/neuroanalyst/models/process/logic/code/python/samples/fsl_threshold.py",
        # "file_path": "./src/neuroanalyst/models/process/logic/code/python/samples/fake_fsl_threshold.py",
    },
}

bet_logic: NeuProcessLogic = decoder.decode_from_file(functions["fsl_bet"]["file_path"])
fast_logic: NeuProcessLogic = decoder.decode_from_file(functions["fsl_fast"]["file_path"])
threshold_logic: NeuProcessLogic = decoder.decode_from_file(functions["fsl_threshold"]["file_path"])

# bet_logic.about = functions["fsl_bet"]["about"]
# fast_logic.about = functions["fsl_fast"]["about"]
# threshold_logic.about = functions["fsl_threshold"]["about"]

# %% [markdown]
# ### Create NeuProcessDir and respective directories

# %%
bet_dir: NeuProcessDir = NeuProcessDir.from_logic(bet_logic)
fast_dir: NeuProcessDir = NeuProcessDir.from_logic(fast_logic)
threshold_dir: NeuProcessDir = NeuProcessDir.from_logic(threshold_logic)

for dir in [bet_dir, fast_dir, threshold_dir]:
    dir.add_environment_variables("FSL_IMG")
    dir.add_language_packages("python", ["nibabel", "numpy"])
    dir.config.bootstrap_method = "localimage"
    dir.config.base_image = BASE_IMAGE

bet_dir.generate()
fast_dir.generate()
threshold_dir.generate()

# %% [markdown]
# ### Create NeuProcess instances (with virtual environments)

# %%
# bet_process: NeuProcess = NeuProcess.from_process_id(bet_dir.process_id)
# fast_process: NeuProcess = NeuProcess.from_process_id(fast_dir.process_id)
# threshold_process: NeuProcess = NeuProcess.from_process_id(threshold_dir.process_id)

# bet_process.create_virtual_env()
# fast_process.create_virtual_env()
# threshold_process.create_virtual_env()

# %% [markdown]
# ### Create NeuProcess instances (with Singularity images)
# 

# %%
bet_process: NeuProcess = NeuProcess.from_process_id(bet_dir.process_id)
fast_process: NeuProcess = NeuProcess.from_process_id(fast_dir.process_id)
threshold_process: NeuProcess = NeuProcess.from_process_id(threshold_dir.process_id)

bet_process.build_image()
fast_process.build_image()
threshold_process.build_image()

# %% [markdown]
# ### Create NeuProcessExec instances

# %%
dataset_path: str = BIDS_ROOT
fsl_img_path: str = FSL_IMG

bet_exec: NeuProcessExec = NeuProcessExec(
    process=bet_process,
    execution_mode=EXECUTION_MODE,
    env_var_values={"FSL_IMG": fsl_img_path, "BIDS_FILTERS": json.dumps({
        "suffix": "T1w",
        "extension": ".nii.gz"
    })},
    bind_path_values={"/data": dataset_path, "/opt/fsl": fsl_img_path}
)

fast_exec: NeuProcessExec = NeuProcessExec(
    process=fast_process,
    # process=bet_process,
    execution_mode=EXECUTION_MODE,
    env_var_values={"FSL_IMG": fsl_img_path, "BIDS_FILTERS": json.dumps({
        "desc": "brain",
        "suffix": "T1w",
        "extension": ".nii.gz"
    })},
    bind_path_values={"/data": dataset_path}
)

threshold_exec: NeuProcessExec = NeuProcessExec(
    process=threshold_process,
    # process=bet_process,
    execution_mode=EXECUTION_MODE,
    env_var_values={"FSL_IMG": fsl_img_path, "BIDS_FILTERS": json.dumps({
        "desc": "seg",
        "suffix": "T1w",
        "extension": ".nii.gz"
    })},
    bind_path_values={"/data": dataset_path}
)

# bet_exec.get_configuration_status()
# fast_exec.get_configuration_status()
# threshold_exec.get_configuration_status()

threshold_exec.print_configuration_status()


# %% [markdown]
# ### Prepare NeuPipeline

# %%
scheduler: HPCScheduler = HPCScheduler.LSF
# scheduler: HPCScheduler = HPCScheduler.LOCAL

bet_step: NeuPipelineStep = NeuPipelineStep(
    name="Brain Extraction",
    description="Perform brain extraction using FSL BET",
    process_execs=[bet_exec]
)
fast_step: NeuPipelineStep = NeuPipelineStep(
    name="Tissue Segmentation",
    description="Perform tissue segmentation using FSL FAST",
    process_execs=[fast_exec]
)
threshold_step: NeuPipelineStep = NeuPipelineStep(
    name="Thresholding",
    description="Apply thresholding using FSL Threshold",
    process_execs=[threshold_exec]
)

timestamp: str = time.strftime("%Y%m%d-%H%M%S")

about_fsl_pipeline: About = About(
    name=f"FSL_Real_T1w_Preprocessing_{timestamp}",
    description="A pipeline for preprocessing T1-weighted MRI images using FSL tools.",
    version="1.0.0",
    author="Chinmay Mokashi"
)
fsl_pipeline: NeuPipeline = NeuPipeline(
    about=about_fsl_pipeline,
    steps=[bet_step, fast_step, threshold_step],
    scheduler=scheduler,
    bids_root=BIDS_ROOT
)
fsl_pipeline.apply_standard_exec_params()
print(fsl_pipeline.steps[0].process_execs[0].print_configuration_status())

# %%
# fsl_pipeline.steps[0].process_execs[0].generate_command()
fsl_pipeline.create_pipeline_dir()

print(f"Pipeline ID: {fsl_pipeline.pipeline_id}")