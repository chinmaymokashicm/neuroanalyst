import os
import subprocess
from pathlib import Path

import nibabel as nib
import numpy as np

def fsl_threshold(input_filepath: str):
    """
    Apply FSL's thresholding to a NIfTI image to generate a binary mask for each tissue type.
    Uses a Nifti file that has been brain-extracted and segmented into tissue types - CSF, GM, WM. These images are stacked along the last dimension.
    """
    fsl_img = os.getenv("FSL_IMG")       # path to FSL Singularity image (passed at runtime)
    if fsl_img is None:
        raise ValueError("FSL_IMG environment variable is not set.")
    data_dir = "/data"  # shared data dir bind
    pipeline_name = os.getenv("PIPELINE_NAME")  # get pipeline name from env
    if pipeline_name is None:
        raise ValueError("PIPELINE_NAME environment variable is not set.")
    output_dir = f"/data/derivatives/{pipeline_name}"  # output dir bind
    threshold: float = float(os.getenv("THRESHOLD", 0.5))  # threshold value from env or default

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Extract each tissue type from the stacked input
    csf_data = nib.load(input_filepath).get_fdata()[..., 0]
    gm_data = nib.load(input_filepath).get_fdata()[..., 1]
    wm_data = nib.load(input_filepath).get_fdata()[..., 2]

    # Save individual tissue files to disk
    base_stem = input_filepath.replace(".nii.gz", "")
    csf_filepath = str(Path(output_dir) / f"{base_stem}_csf.nii.gz")
    gm_filepath = str(Path(output_dir) / f"{base_stem}_gm.nii.gz")
    wm_filepath = str(Path(output_dir) / f"{base_stem}_wm.nii.gz")

    nib.save(nib.Nifti1Image(csf_data, affine=np.eye(4)), csf_filepath)
    nib.save(nib.Nifti1Image(gm_data, affine=np.eye(4)), gm_filepath)
    nib.save(nib.Nifti1Image(wm_data, affine=np.eye(4)), wm_filepath)
    
    # Apply thresholding using FSL's fslmaths
    csf_thresh_filepath = str(Path(output_dir) / f"{base_stem}_csf_mask.nii.gz")
    gm_thresh_filepath = str(Path(output_dir) / f"{base_stem}_gm_mask.nii.gz")
    wm_thresh_filepath = str(Path(output_dir) / f"{base_stem}_wm_mask.nii.gz")

    tissue_types = [
        ("csf", csf_filepath, csf_thresh_filepath),
        ("gm", gm_filepath, gm_thresh_filepath),
        ("wm", wm_filepath, wm_thresh_filepath)
    ]

    for tissue, input_file, output_file in tissue_types:
        subprocess.run([
            "singularity", "exec",
            "--bind", f"{data_dir}:{data_dir}",
            "--bind", f"{output_dir}:{output_dir}",
            fsl_img,
            "fslmaths", input_file, "-thr", str(threshold), "-bin", output_file
        ], check=True)

    # Stack the binary masks into a single output array
    csf_mask = nib.load(csf_thresh_filepath).get_fdata()
    gm_mask = nib.load(gm_thresh_filepath).get_fdata()
    wm_mask = nib.load(wm_thresh_filepath).get_fdata()
    output_data = np.stack([csf_mask, gm_mask, wm_mask], axis=-1)
    
    metrics: dict = {
        "csf_voxels": int((csf_mask > 0).sum()),
        "gm_voxels": int((gm_mask > 0).sum()),
        "wm_voxels": int((wm_mask > 0).sum()),
        "tool": "FSL fslmaths",
        "version": "6.0.5",
        "parameters": {
            "threshold": threshold
        }
    }
    
    output_entities: dict = {
        "desc": "mask",
        "suffix": "T1w",
        "extension": ".nii.gz"
    }
    
    forced_outputs: list[str] = [csf_filepath, gm_filepath, wm_filepath, csf_thresh_filepath, gm_thresh_filepath, wm_thresh_filepath]
    
    return output_data, metrics, output_entities, forced_outputs