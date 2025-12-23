# %%
from src.neuroanalyst.models.process import NeuProcess, NeuProcessExec, NeuProcessLogic, NeuProcessDir, ExecutionMode
from src.neuroanalyst.models.about import About
from src.neuroanalyst.models.process.logic.code.python.decoder import PythonDecoder
from src.neuroanalyst.models.pipeline import NeuPipeline, NeuPipelineStep
from src.neuroanalyst.models.pipeline import ProcessConstructorConfig, PipelineStepConstructorConfig, PipelineConstructorConfig
from src.neuroanalyst.utils.constants import NeuroAnalystPaths

import os, time

from matplotlib import pyplot as plt
import networkx as nx
from bids.layout import BIDSLayout

# %%
USERNAME = "cmokashi"
BASE_IMAGE = "/rsrch5/home/csi/cmokashi/neuroanalyst/cmokashi/apptainer/images/base/for_freesurfer.sif"
EXECUTION_MODE: str = "container"
paths = NeuroAnalystPaths(username=USERNAME)
BIDS_ROOT: str = str([dataset for dataset in paths.datasets.iterdir() if dataset.is_dir()][0])
FREESURFER_HOME: str = os.getenv("FREESURFER_HOME", "/risapps/rhel8/freesurfer/7.4.1")
BIDS_ROOT, FREESURFER_HOME

# %% [markdown]
# ## Register Recon Logics

# %%
decoder: PythonDecoder = PythonDecoder()

functions: dict = {
    "autorecon1": {
        "about": About(
            name="Autorecon1",
            description="Autorecon1 Brain Extraction Tool (BET) from FSL",
            version="1.0.0",
            author="Chinmay Mokashi"
        ),
        "file_path": "./src/neuroanalyst/models/process/logic/code/python/samples/autorecon1.py",
    },
    "autorecon2": {
        "about": About(
            name="Autorecon2",
            description="Autorecon2 Segmentation",
            version="1.0.0",
            author="Chinmay Mokashi"
        ),
        "file_path": "./src/neuroanalyst/models/process/logic/code/python/samples/autorecon2.py",
    },
    "autorecon3": {
        "about": About(
            name="Autorecon3",
            description="Autorecon3 Segmentation",
            version="1.0.0",
            author="Chinmay Mokashi"
        ),
        "file_path": "./src/neuroanalyst/models/process/logic/code/python/samples/autorecon3.py",
    },
}

author, version, tag = "Chinmay Mokashi", "v1.0.0", "v1.0.0"

try:
    autorecon1_logic: NeuProcessLogic = decoder.decode_from_file(functions["autorecon1"]["file_path"])
    autorecon1_logic.about.author = author
    autorecon1_logic.about.version = version
    autorecon1_logic.about.tag = tag
    autorecon1_logic.username = USERNAME
    autorecon1_logic.register()
except Exception as e:
    print(f"Error decoding Autorecon1 logic: {e}. Loading from registry as fallback.")
    autorecon1_logic: NeuProcessLogic = NeuProcessLogic.from_func_name("autorecon1", username=USERNAME)
try:
    autorecon2_logic: NeuProcessLogic = decoder.decode_from_file(functions["autorecon2"]["file_path"])
    autorecon2_logic.about.author = author
    autorecon2_logic.about.version = version
    autorecon2_logic.about.tag = tag
    autorecon2_logic.username = USERNAME
    autorecon2_logic.register()
except Exception as e:
    print(f"Error decoding Autorecon2 logic: {e}. Loading from registry as fallback.")
    autorecon2_logic: NeuProcessLogic = NeuProcessLogic.from_func_name("autorecon2", username=USERNAME)
try:
    autorecon3_logic: NeuProcessLogic = decoder.decode_from_file(functions["autorecon3"]["file_path"])
    autorecon3_logic.about.author = author
    autorecon3_logic.about.version = version
    autorecon3_logic.about.tag = tag
    autorecon3_logic.username = USERNAME
    autorecon3_logic.register()
except Exception as e:
    print(f"Error decoding Autorecon3 logic: {e}. Loading from registry as fallback.")
    autorecon3_logic: NeuProcessLogic = NeuProcessLogic.from_func_name("autorecon3", username=USERNAME)

# %% [markdown]
# ## Create Recon Processes and Build Images

# %%
autorecon1_process_dir: NeuProcessDir = NeuProcessDir.from_logic(autorecon1_logic)
autorecon2_process_dir: NeuProcessDir = NeuProcessDir.from_logic(autorecon2_logic)
autorecon3_process_dir: NeuProcessDir = NeuProcessDir.from_logic(autorecon3_logic)

for dir in [autorecon1_process_dir, autorecon2_process_dir, autorecon3_process_dir]:
    dir.add_language_packages("python", ["nibabel", "numpy"])
    dir.config.bootstrap_method = "localimage"
    dir.config.base_image = BASE_IMAGE
    dir.add_bind_paths(FREESURFER_HOME)
    dir.add_environment_variables("FREESURFER_HOME")
    print(dir.process_id)
    dir.generate()

# %%
autorecon1_process: NeuProcess = NeuProcess.from_process_dir(autorecon1_process_dir)
autorecon2_process: NeuProcess = NeuProcess.from_process_dir(autorecon2_process_dir)
autorecon3_process: NeuProcess = NeuProcess.from_process_dir(autorecon3_process_dir)
autorecon1_process.process_id, autorecon2_process.process_id, autorecon3_process.process_id

# autorecon1_process: NeuProcess = NeuProcess.from_process_id(process_id="PR-581497", username=USERNAME)
# autorecon2_process: NeuProcess = NeuProcess.from_process_id(process_id="PR-616178", username=USERNAME)
# autorecon3_process: NeuProcess = NeuProcess.from_process_id(process_id="PR-574089", username=USERNAME)

# # %%
# autorecon1_process.build_singularity_image()

# # %%
# autorecon2_process.build_singularity_image()

# # %%
# autorecon3_process.build_singularity_image()

# %% [markdown]
# ## Set up Pipeline Graph

# %%
process_config_autorecon1: ProcessConstructorConfig = ProcessConstructorConfig.initiate_from_process_id(username=USERNAME, process_id=autorecon1_process.process_id)
process_config_autorecon2: ProcessConstructorConfig = ProcessConstructorConfig.initiate_from_process_id(username=USERNAME, process_id=autorecon2_process.process_id)
process_config_autorecon3: ProcessConstructorConfig = ProcessConstructorConfig.initiate_from_process_id(username=USERNAME, process_id=autorecon3_process.process_id)

for process_config in [process_config_autorecon1, process_config_autorecon2, process_config_autorecon3]:
    process_config.extra_bind_paths = {FREESURFER_HOME: FREESURFER_HOME}
    process_config.extra_environment_variables = {"FREESURFER_HOME": FREESURFER_HOME}
    
process_config_autorecon1.validate_config(), process_config_autorecon2.validate_config(), process_config_autorecon3.validate_config()

# %%
pipeline_step_1_config: PipelineStepConstructorConfig = PipelineStepConstructorConfig(
    name="Autorecon1",
    description="Perform FreeSurfer autorecon1 on T1w images",
    process_configs=[process_config_autorecon1]
)
pipeline_step_2_config: PipelineStepConstructorConfig = PipelineStepConstructorConfig(
    name="Autorecon2",
    description="Perform FreeSurfer autorecon2 on T1w images",
    process_configs=[process_config_autorecon2]
)
pipeline_step_3_config: PipelineStepConstructorConfig = PipelineStepConstructorConfig(
    name="Autorecon3",
    description="Perform FreeSurfer autorecon3 on T1w images",
    process_configs=[process_config_autorecon3]
)

pipeline_config: PipelineConstructorConfig = PipelineConstructorConfig(
    about={"name": "T1w_Cortical_Reconstruction", "description": "T1w MR image cortical reconstruction using FreeSurfer recon-all tool.", "author": "Chinmay Mokashi"},
    steps=[pipeline_step_1_config, pipeline_step_2_config, pipeline_step_3_config],
    scheduler="lsf"
)
pipeline_config.construct_graph()

# %%
# pipeline_config.visualize()

# %% [markdown]
# ## Build the Pipeline

# %%
pipeline_config.add_edge(process_config_autorecon1, process_config_autorecon2, force=True)
pipeline_config.add_edge(process_config_autorecon2, process_config_autorecon3, force=True)
# pipeline_config.visualize()

# %%
# Notice how the descendant nodes are all set, but the starting BIDS filters for the root is not.
process_config_autorecon1.input_bids_filters, process_config_autorecon2.input_bids_filters, process_config_autorecon3.input_bids_filters

# %%
process_config_autorecon1.output_entities, process_config_autorecon2.output_entities, process_config_autorecon3.output_entities

# %%
process_config_autorecon1.input_bids_filters = {"suffix": "T1w", "extension": ".nii.gz"}

# %%
# Build the pipeline
print(BIDS_ROOT)
pipeline: NeuPipeline = pipeline_config.to_pipeline(bids_root=BIDS_ROOT)

# %%
# Waiting for all images/venvs to be built
# try:
#     processes: list[NeuProcess] = [autorecon1_process, autorecon2_process, autorecon3_process]
#     checking_method: callable = (lambda p: p.is_image_built) if any(proc_exec.execution_mode == ExecutionMode.CONTAINER for proc_exec in pipeline.process_execs) else (lambda p: p.is_venv_created)
#     while all(checking_method(p) for p in processes) is False:
#         print("\n\n")
#         print("Waiting for all images to be built.")
#         for process in processes:
#             print(f"Image: {process.process_name}: {process.process_id}, status: {checking_method(process)}")
#         time.sleep(5)
# except Exception as e:
#     print(f"Error in detecting compute environments for processes: {e}")

# pipeline_config.visualize()
print(pipeline)

# %%
# pipeline.reset_pipeline_status()
# pipeline.execute_via_python()
# pipeline.async_execute_via_python()
