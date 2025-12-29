from neuroanalyst.models.process.logic.core import Metric

import os, json, subprocess
from pathlib import Path
from typing import Optional

import numpy as np
import nibabel as nib
from dipy.io.gradients import read_bvals_bvecs
from dipy.core.gradients import gradient_table


def fsl_register_dti_maps_to_mni(input_filepath: str):
    """Register DTI scalar maps to MNI space.

    Args:
        input_filepath (str): Path to the input NifTi image with multi-channel DTI scalar maps (FA, MD, RD, AD).

    Returns:
        output_data (nib.Nifti1Image): Stacked Nifti image registered to MNI (FA, MD, RD, AD).
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """
    # ============================
    # Step 1: Load Input Data
    # ============================
    DATA_DIR: str = "/data"
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME", None)
    if PIPELINE_NAME is None:
        raise EnvironmentError("PIPELINE_NAME environment variable is not set.")
    fsl_img_name = os.getenv("FSL_IMG_NAME")
    fsl_img_path = f"/opt/fsl_images/{fsl_img_name}"  # path to FSL Singularity image inside container
    output_dir: str = os.path.join(DATA_DIR, "tmp")  # Temporary directory for outputs; will be cleaned up by the framework's wrapper
    os.makedirs(output_dir, exist_ok=True)
    
    img: nib.Nifti1Image = nib.load(input_filepath)
    img_data: np.ndarray = img.get_fdata()
    affine: np.ndarray = img.affine
    header: nib.Nifti1Header = img.header
    
    if img_data.ndim != 4 or img_data.shape[-1] != 4:
        raise ValueError("Input image must be a 4D DWI image.")
    
    # ============================
    # Step 2: Register DTI Maps to MNI - register a reference map (FA) and apply the same transform to other maps
    # ============================
    # Register the FA map to MNI space using FSL FLIRT and save the transformation matrix
    # Apply the same transformation to MD, RD, and AD maps
    
    temp_fa_input_filepath: str = os.path.join(output_dir, "fa_map.nii.gz")
    temp_fa_output_filepath: str = os.path.join(output_dir, "temp_fa_map.nii.gz")
    temp_fa2mni_mat_filepath: str = os.path.join(output_dir, "fa2mni.mat")
    temp_output_filepath: str = os.path.join(output_dir, "dti_scalars_mni.nii.gz")
    
    fa_data: np.ndarray = img_data[..., 0]
    fa_img: nib.Nifti1Image = nib.Nifti1Image(fa_data, affine)
    nib.save(fa_img, temp_fa_input_filepath)
    
    internal_bash_command: str = f"""
set -e

. ${{FSLDIR}}/etc/fslconf/fsl.sh

# Reference MNI template
MNI_REF=${{FSLDIR}}/data/standard/MNI152_T1_1mm.nii.gz

# 1) Register FA to MNI (estimate transform)
flirt \\
  -in {temp_fa_input_filepath} \\
  -ref $MNI_REF \\
  -omat {temp_fa2mni_mat_filepath} \\
  -out {temp_fa_output_filepath} \\
  -dof 12 \\
  -interp trilinear

# 2) Apply the same transform to the stacked DTI maps
fslsplit {input_filepath} vol_
for vol in vol_*.nii.gz; do
  flirt \\
    -in $vol \\
    -ref $MNI_REF \\
    -applyxfm \\
    -init {temp_fa2mni_mat_filepath} \\
    -out mni_$vol \\
    -interp trilinear
done
fslmerge -t {temp_output_filepath} mni_vol_*.nii.gz
"""
    try:
        cmd = [
            "apptainer", "exec",
            fsl_img_path,
            "bash", "-c", internal_bash_command
        ]
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        print(f"FSL FLIRT command finished with return code {result.returncode}")
        
        if result.returncode != 0:
            raise RuntimeError(f"FSL FLIRT command failed with return code {result.returncode}")
    except Exception as e:
        raise RuntimeError(f"FSL FLIRT command failed: {e}")
    
    output_data: nib.Nifti1Image = nib.load(temp_output_filepath)

    metrics: dict = {
        "registration_tool": "FSL FLIRT",
        "input_shape": img_data.shape,
        "output_shape": output_data.shape
    }

    output_entities: dict = {
        "suffix": "map",
        "desc": "registeredToMNI",
        "extension": ".nii.gz"
    }

    forced_outputs: list = [output_dir]

    return output_data, metrics, output_entities, forced_outputs