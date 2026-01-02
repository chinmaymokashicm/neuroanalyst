# %% [markdown]
# # DWI pre-processing pipeline
# 
# ## Processes
# 1. dipy_denoise_mppca
# 2. dipy_remove_gibbs_ringing
# 3. fsl_correct_distortions_and_motion
# # 4. n4_bias_field_correction
# 5. dipy_brain_mask

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

AUTHOR: str = "Chinmay Mokashi"
PIPELINE_NAME: str = "dwi_preprocessing"
PIPELINE_DESCRIPTION: str = "Performs basic preprocessing steps on DWI data using FSL."

# Applicable for FSL-based processing only
EXTRA_BIND_PATHS: dict = {"/opt/fsl_images/": "/risapps/apptainer/repo/fsl/3.16.8/"}
EXTRA_ENVIRONMENT_VARIABLES: dict = {"FSL_IMG_NAME": "fsl-3.16.8.sif"}
fsl_logics_idxs: list[int] = [2]  # Indices of logics that use FSL and need extra bind paths/env variables

# %% [markdown]
# ## Prepare Logics

# %%
logic_names: list[str] = [
    "dipy_denoise_mppca",
    "dipy_remove_gibbs_ringing",
    "fsl_correct_distortions_and_motion",
    # "n4_bias_field_correction",
    "dipy_brain_mask",
]

logic_descriptions: list[str] = [
    "Denoise DWI data using MP-PCA method from DIPY.",
    "Remove Gibbs ringing artifacts from DWI data using DIPY.",
    "Correct for eddy currents, susceptibility distortions, and motion in DWI data using FSL.",
    # "Apply N4 bias field correction to DWI data.",
    "Generate brain mask from DWI data using DIPY.",
]

# %%
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
    "command_flags": ["--fakeroot"],
    "bootstrap_method": "localimage",
    "base_image": "/rsrch5/home/csi/cmokashi/neuroanalyst/cmokashi/apptainer/images/base/python_312_slim_amd64_git_apptainer.sif",
    "language_packages": {"python": ["dipy", "nibabel", "numpy", "SimpleITK"]},
    }

process_ids: list[str] = []
for i, logic_name in enumerate(logic_names):
    config = process_config.copy()
    if i in fsl_logics_idxs:
        config["bind_paths"] = list(EXTRA_BIND_PATHS.keys())
        config["environment_variables"] = list(EXTRA_ENVIRONMENT_VARIABLES.keys())
        config["extra_directories"] = ["/opt/fsl_images/"] # Ensure FSL image dir exists in container
    process_dir_recipe: ProcessDirRecipe = ProcessDirRecipe(
        logic=logic_names[i],
        config=config,
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
                        "extension": ".nii.gz",
                    } if i == 0 else {},
                    "extra_bind_paths": EXTRA_BIND_PATHS if i in fsl_logics_idxs else {},
                    "extra_environment_variables": EXTRA_ENVIRONMENT_VARIABLES if i in fsl_logics_idxs else {}
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

