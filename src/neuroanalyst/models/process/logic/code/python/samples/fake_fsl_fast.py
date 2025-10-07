import os
import subprocess
from pathlib import Path

import nibabel as nib
import numpy as np

def fsl_fast(input_filepath: str):
    """
    Tissue Segmentation using FSL FAST.
    Runs FSL FAST inside the provided FSL Singularity image.
    Uses a Nifti file that has been brain-extracted.
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (list): List of segmented tissue image data arrays [CSF, GM, WM].
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    # fsl_img = os.environ["FSL_IMG"]       # path to FSL Singularity image (passed at runtime)
    fsl_img = os.getenv("FSL_IMG", "/path/to/fsl.sif")  # Placeholder path for testing
    data_dir = "/data"  # shared data dir bind
    pipeline_name = os.environ["PIPELINE_NAME"]  # get pipeline name from env
    output_dir = f"/data/derivatives/{pipeline_name}"  # output dir bind

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    base_stem = Path(input_filepath).stem
    output_filepath = str(Path(output_dir) / f"{base_stem}_seg.nii.gz")
    csf_filepath = str(Path(output_dir) / f"{base_stem}_csf.nii.gz")
    gm_filepath = str(Path(output_dir) / f"{base_stem}_gm.nii.gz")
    wm_filepath = str(Path(output_dir) / f"{base_stem}_wm.nii.gz")

    cmd = [
        "singularity", "exec",
        "--bind", f"{data_dir}:{data_dir}",
        "--bind", f"{output_dir}:{output_dir}",
        fsl_img,
        "fast", "-o", str(Path(output_filepath).with_suffix('')), input_filepath
    ]
    # subprocess.run(cmd, check=True)

    # csf_data = nib.load(csf_filepath).get_fdata()
    # gm_data = nib.load(gm_filepath).get_fdata()
    # wm_data = nib.load(wm_filepath).get_fdata()
    
    csf_data = nib.Nifti1Image(np.zeros((10, 10, 10)), affine=np.eye(4)).get_fdata()  # Placeholder data for testing
    gm_data = nib.Nifti1Image(np.zeros((10, 10, 10)), affine=np.eye(4)).get_fdata()  # Placeholder data for testing
    wm_data = nib.Nifti1Image(np.zeros((10, 10, 10)), affine=np.eye(4)).get_fdata()  # Placeholder data for testing

    output_data = np.stack([csf_data, gm_data, wm_data], axis=-1)
    
    metrics: dict = {
        "csf_volume": int((csf_data > 0).sum()),
        "gm_volume": int((gm_data > 0).sum()),
        "wm_volume": int((wm_data > 0).sum()),
        "tool": "FSL FAST",
        "version": "6.0.5",
        "parameters": {
            "options": "-o"
        }
    }
    
    output_entities: dict = {
        "desc": "seg",
        "suffix": "T1w",
        "extension": ".nii.gz"
    }

    forced_outputs: list[str] = [output_filepath, csf_filepath, gm_filepath, wm_filepath]

    return output_data, metrics, output_entities, forced_outputs