# %% [markdown]
# # DTI modeling pipeline using DIPY
# 
# ## Processes
# 1. dti_tensor_fit
# 2. derive_dti_metrics

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
# os.environ["NEUROANALYST_HOME"] = "/Volumes/csi/cmokashi/neuroanalyst/"

USERNAME: str = "cmokashi"
AUTHOR: str = "Chinmay Mokashi"
PIPELINE_NAME: str = "dti_modeling"
PIPELINE_DESCRIPTION: str = "Performs DTI modeling and metric derivation using DIPY."
DWI_PIPELINE_NAME: str = "dwi_preprocessing"

# %% [markdown]
# ## Prepare Logics

# %%
logic_names: list[str] = [
    "dti_tensor_fit",
    "derive_dti_metrics",
]

logic_descriptions: list[str] = [
    "Fit a diffusion tensor model to DWI data using DIPY and generate scalar maps.",
    "Derive DTI metrics (FA, MD, AD, RD) from the fitted tensor model.",
]

# %%
sample_functions_root: Path = Path("src/neuroanalyst/models/process/logic/code/python/samples")

function_paths: list[str] = [sample_functions_root / f"{func_name}.py" for func_name in logic_names]

for logic_name, function_path in zip(logic_names, function_paths):
    logic_recipe: LogicRecipe = LogicRecipe(
        path=str(function_path),
        username=USERNAME,
        author=AUTHOR,
    )
    save_recipe_to_yaml(logic_recipe, logic_name, username=USERNAME)
    logic: NeuProcessLogic = create_logic_from_recipe(get_recipe_yaml_path(logic_name, "logic", username=USERNAME))
    logic.register(overwrite=True)

# %% [markdown]
# ## Prepare Processes

# %%
process_config: dict = {
    "bootstrap_method": "localimage",
    "base_image": "/rsrch5/home/csi/cmokashi/neuroanalyst/cmokashi/apptainer/images/base/python_312_slim_amd64_git.sif",
    "language_packages": {"python": ["dipy", "nibabel", "numpy"]},
    }

process_ids: list[str] = []
for logic_name in logic_names:
    process_dir_recipe: ProcessDirRecipe = ProcessDirRecipe(
        logic={"name": logic_name, "username": USERNAME},
        config=process_config,
    )
    save_recipe_to_yaml(process_dir_recipe, logic_name, username=USERNAME)
    process_dir: NeuProcessDir = create_process_dir_from_recipe(get_recipe_yaml_path(logic_name, "process", username=USERNAME))
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
    "username": USERNAME,
    "author": AUTHOR,
    "data": "/rsrch5/home/csi/cmokashi/neuroanalyst/cmokashi/datasets/ds004884-1.0.2/",
    "name": PIPELINE_NAME,
    "description": PIPELINE_DESCRIPTION,
    "auto_link": True,
    "cost": 8,
    "steps": [
        {
            "name": logic_names[i],
            "description": logic_descriptions[i],
            "processes": [
                {
                    "process_id": process_ids[i],
                    "input_bids_filters": {
                        "datatype": "dwi",
                        "suffix": "dwi",
                        "desc": "brainMasked", # Use brain-masked DWI from preprocessing
                        "extension": ".nii.gz",
                    } if i == 0 else {},
                }
            ]
        } for i in range(len(logic_names))
    ],
    "starting_bids_scope": DWI_PIPELINE_NAME # Use outputs from DWI preprocessing pipeline as inputs
}
pipeline_recipe: PipelineRecipe = PipelineRecipe(**pipeline_recipe_config)
pipeline: NeuPipeline = construct_pipeline_from_recipe(save_recipe_to_yaml(pipeline_recipe, PIPELINE_NAME, username=USERNAME))

# %%
def get_build_script_commands() -> str:
    commands: list[str] = []
    for process_id in process_ids:
        commands.append(f"python build_process.py {process_id} {USERNAME}")
    return " & ".join(commands)

print(get_build_script_commands())
print(f"Pipeline '{pipeline.pipeline_id}' created.")
print(pipeline)

