# %% [markdown]
# # FreeSurfer recon-all pipeline via recipe-building
# ## Steps
# 1. Create and register Logics
#   - autorecon1
#   - autorecon2
#   - autorecon3
# 2. Create ProcessDirs and build images
# 3. Construct Pipeline

# %%
from src.neuroanalyst.models.recipe.core import (
    create_logic_from_recipe,
    create_process_dir_from_recipe,
    construct_pipeline_from_recipe,
    save_recipe_to_yaml,
    get_recipe_yaml_path,
    LogicRecipe,
    ProcessDirRecipe,
    ProcessExecInStepRecipe,
    PipelineStepRecipe,
    PipelineRecipe,
    )
from src.neuroanalyst.models.process.logic.core import NeuProcessLogic
from src.neuroanalyst.models.process.dir.core import NeuProcessDir
from src.neuroanalyst.models.pipeline.core import NeuPipeline

import os
from pathlib import Path

# %%
# Set NEUROANALYST_HOME to the HPC installation
# os.environ["NEUROANALYST_HOME"] = "/Volumes/csi/cmokashi/neuroanalyst/"

# %%

AUTHOR: str = "Chinmay Mokashi"
PIPELINE_NAME: str = "recon_all"
PIPELINE_DESCRIPTION: str = "Executes the recon-all pipeline for preprocessing and cortical reconstruction in FreeSurfer."

EXTRA_BIND_PATHS: dict = {"/risapps/rhel8/freesurfer/7.4.1": "/risapps/rhel8/freesurfer/7.4.1"}
EXTRA_ENVIRONMENT_VARIABLES: dict = {"FREESURFER_HOME": "/risapps/rhel8/freesurfer/7.4.1"}

DATA_DIR: str = "/rsrch5/home/csi/cmokashi/neuroanalyst/users/cmokashi/datasets/ds004884-1.0.2/"

# %% [markdown]
# ## Prepare Logics

# %%
logic_names: list[str] = [
    "autorecon1",
    "autorecon2",
    "autorecon3",
]

logic_descriptions: list[str] = [
    "Executes the autorecon1 step of FreeSurfer's recon-all pipeline which includes motion correction, intensity normalization, and skull stripping.",
    "Executes the autorecon2 step of FreeSurfer's recon-all pipeline which includes white matter segmentation, surface extraction, and topology correction.",
    "Executes the autorecon3 step of FreeSurfer's recon-all pipeline which includes cortical parcellation and surface-based registration.",
]

sample_functions_root: Path = Path("src/neuroanalyst/models/process/logic/code/python/samples")

function_paths: list[str] = [sample_functions_root / f"{func_name}.py" for func_name in logic_names]

for logic_name, function_path in zip(logic_names, function_paths):
    logic_recipe: LogicRecipe = LogicRecipe(
        path=str(function_path),
        author=AUTHOR,
    )
    save_recipe_to_yaml(logic_recipe, logic_name)
    logic: NeuProcessLogic = create_logic_from_recipe(get_recipe_yaml_path(logic_name, "logic"))
    logic.register(overwrite=True)

# %% [markdown]
# ## Prepare Processes

# %%
process_config: dict = {
    "environment_variables": ["FREESURFER_HOME"],
    "bind_paths": ["/risapps/rhel8/freesurfer/7.4.1"],
    "command_flags": ["--fakeroot"],
    "bootstrap_method": "localimage",
    "base_image": "/rsrch5/home/csi/cmokashi/neuroanalyst/cmokashi/apptainer/images/base/for_freesurfer.sif",
    }
process_ids: list[str] = []
for logic_name in logic_names:
    process_dir_recipe: ProcessDirRecipe = ProcessDirRecipe(
        logic=logic_name,
        config=process_config,
    )
    save_recipe_to_yaml(process_dir_recipe, logic_name)
    process_dir: NeuProcessDir = create_process_dir_from_recipe(get_recipe_yaml_path(logic_name, "process"))
    try:
        process_dir.generate()
        print(f"Process directory for {logic_name} created at {process_dir.working_dir}")
        process_ids.append(process_dir.process_id)
    except Exception as e:
        print(f"Error creating process directory for {logic_name}: {e}")

# %% [markdown]
# ## Construct Pipeline

# %%
pipeline_recipe_config: dict = {
    "author": AUTHOR,
    "data": DATA_DIR,
    "name": PIPELINE_NAME,
    "description": PIPELINE_DESCRIPTION,
    "auto_link": True,
    "cost": 10,
    "steps": [
        {
            "name": logic_names[i],
            "description": logic_descriptions[i],
            "processes": [
                {
                    "process_id": process_ids[i],
                    "input_bids_filters": {
                        "suffix": "T1w",
                        "extension": ".nii.gz",
                        "datatype": "anat",
                        } if i == 0 else {},
                    "extra_bind_paths": EXTRA_BIND_PATHS,
                    "extra_environment_variables": EXTRA_ENVIRONMENT_VARIABLES
                }
            ]
        } for i in range(len(logic_names))
    ]
}
pipeline_recipe: PipelineRecipe = PipelineRecipe(**pipeline_recipe_config)
pipeline: NeuPipeline = construct_pipeline_from_recipe(save_recipe_to_yaml(pipeline_recipe, PIPELINE_NAME))

# %%
def get_build_script_commands() -> str:
    commands: list[str] = []
    for process_id in process_ids:
        commands.append(f"python build_process.py {process_id}")
    return " & ".join(commands)

print(get_build_script_commands())
print(f"Pipeline '{pipeline.pipeline_id}' created.")
print(pipeline)


