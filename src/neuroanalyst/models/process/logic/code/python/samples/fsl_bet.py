import os
import subprocess
from pathlib import Path

import nibabel as nib

def fsl_bet(input_filepath: str):
    """
    Brain Extraction (BET).
    Runs FSL BET inside the provided FSL Singularity image.
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (np.ndarray): The brain-extracted image data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    fsl_img = os.getenv("FSL_IMG")       # path to FSL Singularity image (passed at runtime)
    if fsl_img is None:
        raise ValueError("FSL_IMG environment variable is not set.")
    data_dir = "/data"  # shared data dir bind
    pipeline_name = os.getenv("PIPELINE_NAME")  # get pipeline name from env
    if pipeline_name is None:
        raise ValueError("PIPELINE_NAME environment variable is not set.")
    output_dir = f"/data/derivatives/{pipeline_name}"  # output dir bind

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_filepath = str(Path(output_dir) / (input_filepath.replace(".nii.gz", "") + "_brain.nii.gz"))
    mask_filepath = str(Path(output_dir) / (input_filepath.replace(".nii.gz", "") + "_brain_mask.nii.gz"))

    cmd = [
        "singularity", "exec",
        "--bind", f"{data_dir}:{data_dir}",
        "--bind", f"{output_dir}:{output_dir}",
        fsl_img,
        "bet", input_filepath, output_filepath, "-m"
    ]
    subprocess.run(cmd, check=True)

    if not os.path.exists(output_filepath):
        raise ValueError(f"Brain-extracted file not found at {output_filepath}")
    
    output_data = nib.load(output_filepath).get_fdata()
    if output_data is None:
        raise ValueError(f"Failed to load brain-extracted data from {output_filepath}")
    if output_data.size == 0:
        raise ValueError(f"Brain-extracted data from {output_filepath} is empty")
    if not (output_data > 0).any():
        raise ValueError(f"Brain-extracted data from {output_filepath} contains no non-zero values")
    print(f"Loaded brain-extracted data from {output_filepath} with shape {output_data.shape}")
    
    metrics: dict = {
        "brain_volume": int((output_data > 0).sum()),
        "tool": "FSL BET",
        "version": "6.0.5",
        "parameters": {
            "options": "-m"
        }
    }
    
    output_entities: dict = {
        "desc": "brain",
        "suffix": "T1w",
        "extension": ".nii.gz"
    }
    
    forced_outputs: list[str] = [output_filepath, mask_filepath]

    return output_data, metrics, output_entities, forced_outputs