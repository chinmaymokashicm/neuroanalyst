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
    fsl_img = os.environ["FSL_IMG"]       # path to FSL Singularity image (passed at runtime)
    data_dir = "/data"  # shared data dir bind
    pipeline_name = os.environ["PIPELINE_NAME"]  # get pipeline name from env
    output_dir = f"/data/derivatives/{pipeline_name}"  # output dir bind

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_filepath = str(Path(output_dir) / (Path(input_filepath).stem + "_brain.nii.gz"))
    mask_filepath = str(Path(output_dir) / (Path(input_filepath).stem + "_brain_mask.nii.gz"))

    cmd = [
        "singularity", "exec",
        "--bind", f"{data_dir}:{data_dir}",
        "--bind", f"{output_dir}:{output_dir}",
        fsl_img,
        "bet", input_filepath, output_filepath, "-m"
    ]
    subprocess.run(cmd, check=True)

    output_data = nib.load(output_filepath).get_fdata()
    
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