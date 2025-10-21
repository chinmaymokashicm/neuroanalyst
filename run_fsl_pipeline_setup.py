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
from pathlib import Path

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
BASE_IMAGE: str = "/rsrch5/home/csi/cmokashi/neuroanalyst/apptainer/images/python_3.12_slim_amd64_git_apptainer.sif"
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

# %% [markdown]
# ### Create NeuProcessDir and respective directories

# %%
bet_dir: NeuProcessDir = NeuProcessDir.from_logic(bet_logic)
fast_dir: NeuProcessDir = NeuProcessDir.from_logic(fast_logic)
threshold_dir: NeuProcessDir = NeuProcessDir.from_logic(threshold_logic)

for dir in [bet_dir, fast_dir, threshold_dir]:
    dir.add_environment_variables("FSL_IMG_NAME")
    dir.add_bind_paths("/opt/fsl_images")
    dir.add_language_packages("python", ["nibabel", "numpy"])
    dir.config.bootstrap_method = "localimage"
    dir.config.base_image = BASE_IMAGE
    dir.config.command_flags = ["--fakeroot"]
    dir.config.max_workers = 2

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
fsl_img_dir: str = str(Path(fsl_img_path).parent)
fsl_img_name: str = str(Path(fsl_img_path).name)

scheduler_args: dict = {"-n": 2, "-q": "medium", "-M": "20GB", "-W": "12:00"} # LSF-specific flags - memory 20GB, 2 cores, medium queue

subjects_part_1: list[str] = ["M2001", "M2002", "M2003", "M2004", "M2005"]
subjects_part_2: list[str] = ["M2006", "M2007", "M2009", "M2011", "M2012"]
subjects_part_3: list[str] = ["M2013", "M2014", "M2015", "M2016", "M2017"]

bids_filters: dict = {
    "bet": {
        "desc": None,
        "suffix": "T1w",
        "extension": ".nii.gz"
    },
    "fast": {
        "desc": "bet",
        "suffix": "T1w",
        "extension": ".nii.gz"
    },
    "threshold": {
        "desc": "fast",
        "suffix": "seg",
        "extension": ".nii.gz"
    }
}


# bet_exec: NeuProcessExec = NeuProcessExec(
#     process=bet_process,
#     execution_mode=EXECUTION_MODE,
#     env_var_values={"FSL_IMG_NAME": fsl_img_name, "BIDS_FILTERS": json.dumps({"subject": "M2001",
#         "desc": None,
#         "suffix": "T1w",
#         "extension": ".nii.gz"
#     })},
#     bind_path_values={"/opt/fsl_images": fsl_img_dir},
#     scheduler_flags=scheduler_flags
# )

# fast_exec: NeuProcessExec = NeuProcessExec(
#     process=fast_process,
#     # process=bet_process,
#     execution_mode=EXECUTION_MODE,
#     env_var_values={"FSL_IMG_NAME": fsl_img_name, "BIDS_FILTERS": json.dumps({
#         "desc": "bet",
#         "suffix": "T1w",
#         "extension": ".nii.gz"
#     })},
#     bind_path_values={"/opt/fsl_images": fsl_img_dir},
#     scheduler_flags=scheduler_flags
# )

# threshold_exec: NeuProcessExec = NeuProcessExec(
#     process=threshold_process,
#     # process=bet_process,
#     execution_mode=EXECUTION_MODE,
#     env_var_values={"FSL_IMG_NAME": fsl_img_name, "BIDS_FILTERS": json.dumps({
#         "desc": "fast",
#         "suffix": "seg",
#         "extension": ".nii.gz"
#     })},
#     bind_path_values={"/opt/fsl_images": fsl_img_dir},
#     scheduler_flags=scheduler_flags
# )

# bet_exec.get_configuration_status()
# fast_exec.get_configuration_status()
# threshold_exec.get_configuration_status()

# threshold_exec.print_configuration_status()

bet_execs: list[NeuProcessExec] = []
fast_execs: list[NeuProcessExec] = []
threshold_execs: list[NeuProcessExec] = []

for subjects, exec_list, process, bids_filter in [
    (subjects_part_1, bet_execs, bet_process, bids_filters["bet"]),
    (subjects_part_2, bet_execs, bet_process, bids_filters["bet"]),
    (subjects_part_3, bet_execs, bet_process, bids_filters["bet"]),
    (subjects_part_1, fast_execs, fast_process, bids_filters["fast"]),
    (subjects_part_2, fast_execs, fast_process, bids_filters["fast"]),
    (subjects_part_3, fast_execs, fast_process, bids_filters["fast"]),
    (subjects_part_1, threshold_execs, threshold_process, bids_filters["threshold"]),
    (subjects_part_2, threshold_execs, threshold_process, bids_filters["threshold"]),
    (subjects_part_3, threshold_execs, threshold_process, bids_filters["threshold"]),
]:
    exec_instance: NeuProcessExec = NeuProcessExec(
        process=process,
        execution_mode=EXECUTION_MODE,
        env_var_values={
            "FSL_IMG_NAME": fsl_img_name,
            "BIDS_FILTERS": json.dumps({"subject": subjects} | bids_filter)
        },
        bind_path_values={"/opt/fsl_images": fsl_img_dir},
        scheduler_args=scheduler_args
    )
    exec_list.append(exec_instance)
    print(f"Created exec for subjects {', '.join(subjects)} with process {process.process_id}")

print(f"Total BET execs: {len(bet_execs)}")
print(f"Total FAST execs: {len(fast_execs)}")
print(f"Total Threshold execs: {len(threshold_execs)}")

# %% [markdown]
# ### Prepare NeuPipeline

# %%
scheduler: HPCScheduler = HPCScheduler.LSF
# scheduler: HPCScheduler = HPCScheduler.LOCAL

bet_step: NeuPipelineStep = NeuPipelineStep(
    name="Brain Extraction",
    description="Perform brain extraction using FSL BET",
    process_execs=bet_execs
)
fast_step: NeuPipelineStep = NeuPipelineStep(
    name="Tissue Segmentation",
    description="Perform tissue segmentation using FSL FAST",
    process_execs=fast_execs
)
threshold_step: NeuPipelineStep = NeuPipelineStep(
    name="Thresholding",
    description="Apply thresholding using FSL Threshold",
    process_execs=threshold_execs
)

timestamp: str = time.strftime("%Y%m%d-%H%M%S")

about_fsl_pipeline: About = About(
    # name=f"FSL_Real_T1w_Preprocessing_{timestamp}",
    name="fsl_t1w_preprocessing",
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
print(repr(fsl_pipeline))