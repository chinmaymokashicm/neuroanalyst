import os
import subprocess
from pathlib import Path

import nibabel as nib

def fsl_bet(input_filepath: str):
    """
    Brain Extraction (BET).
    Runs FSL BET inside the provided FSL Singularity image.
    Assumptions-
    - The path of the FSL Singularity image is mounted to /opt/fsl in the container
    - The name of the image is passed via the FSL_IMG_NAME environment variable.
    - Apptainer/Singularity is available in the container.
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (np.ndarray): The brain-extracted image data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    DATA_DIR = "/data"  # shared data dir bind
    fsl_img_name = os.getenv("FSL_IMG_NAME")
    fsl_img_path = f"/opt/fsl/{fsl_img_name}"  # path to FSL Singularity image inside container
    pipeline_name = os.getenv("PIPELINE_NAME")  # get pipeline name from env
    output_dir = f"/data/derivatives/{pipeline_name}"  # output dir bind

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_filepath = str(Path(output_dir) / (input_filepath.replace(".nii.gz", "") + "_brain.nii.gz"))
    mask_filepath = str(Path(output_dir) / (input_filepath.replace(".nii.gz", "") + "_brain_mask.nii.gz"))
    
    # Check if singularity executable exists
    subprocess.run(["apptainer", "--version"], check=True)

    # Check if FSL image exists
    if not os.path.exists(fsl_img_path):
        print(f"FSL image not found at {fsl_img_path}")
        raise ValueError(f"FSL image not found at {fsl_img_path}")

    cmd = [
        "apptainer", "exec",
        fsl_img_path,
        "bet", input_filepath, output_filepath, "-m"
    ]
    result = subprocess.run(cmd, check=True)
    print(f"FSL BET command finished with return code {result.returncode}")
    
    print(f"=== Command Output ===\n{result.stdout}\n===================")
    print(result.stdout)
    
    print(f"=== Command Error (if any) ===\n{result.stderr}\n===================")
    print(result.stderr)

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