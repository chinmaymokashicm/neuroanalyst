import os
import subprocess
from pathlib import Path

import nibabel as nib
import numpy as np

def fsl_bet(input_filepath: str):
    """
    Brain Extraction (BET).
    Runs FSL BET inside the provided FSL Singularity image. (https://open.win.ox.ac.uk/pages/fslcourse/practicals/intro2/index.html)
    Assumptions-
    - The path of the FSL Singularity image is mounted to /opt/fsl in the container
    - The name of the image is passed via the FSL_IMG_NAME environment variable.
    - Apptainer/Singularity is available in the container.
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (np.ndarray): Array of brain-extracted image data stacked with the brain mask. 
            Shape will be (X, Y, Z, 2) where the last dimension corresponds to [brain, brain_mask].
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    # Step 1: Prepare environment and paths
    fsl_img_name = os.getenv("FSL_IMG_NAME")
    fsl_img_path = f"/opt/fsl/{fsl_img_name}"  # path to FSL Singularity image inside container
    output_dir: str = "/tmp/"  # Temporary directory for outputs; will be cleaned up by NeuroAnalyst wrapper

    # Step 2: Define output file paths - this is necessary because BET creates two outputs automatically.
    # We need to pass the output data to the NeuroAnalyst wrapper, so that it can be saved correctly with exhaustive metadata.
    output_filepath = str(Path(output_dir) / (input_filepath.replace(".nii.gz", "") + "_brain.nii.gz"))
    mask_filepath = str(Path(output_dir) / (input_filepath.replace(".nii.gz", "") + "_brain_mask.nii.gz"))

    # Step 3: Build and run the Apptainer/Singularity command. This runs FSL BET inside an Apptainer container.
    internal_bash_command: str = f"""
. ${{FSLDIR}}/etc/fslconf/fsl.sh
bet {input_filepath} {output_filepath} -m
    """
    cmd = [
        "apptainer", "exec",
        fsl_img_path,
        "bash", "-c", f"'{internal_bash_command}'"
    ]
    print(f"Running command: {' \\ '.join(cmd)}")
    
    result = subprocess.run(cmd, check=True)
    print(f"FSL BET command finished with return code {result.returncode}")
    
    print(f"=== Command Output ===\n{result.stdout}\n===================")
    print(result.stdout)
    
    print(f"=== Command Error (if any) ===\n{result.stderr}\n===================")
    print(result.stderr)

    # Step 4: Load output data (brain and brain mask) and prepare return values
    # This is necessary because the NeuroAnalyst wrapper expects the output data to be returned from this function.
    # The wrapper will then save the data to the appropriate NeuroAnalyst-compliant location with metadata.
    for brain_path in [output_filepath, mask_filepath]:
        if not os.path.exists(brain_path):
            raise FileNotFoundError(f"Expected output file not found: {brain_path}")
    brain_img = nib.load(output_filepath)
    brain_data = brain_img.get_fdata()
    mask_img = nib.load(mask_filepath)
    mask_data = mask_img.get_fdata()
    brain_data = np.stack([brain_data, mask_data], axis=-1)  # shape will be (X, Y, Z, 2)
    print(f"Loaded brain data shape: {brain_data.shape}")
    
    metrics: dict = {
        "brain_volume": int((brain_data > 0).sum()),
        "mask_volume": int((mask_data > 0).sum()),
        "mask_coverage": float((mask_data > 0).sum()) / mask_data.size,
        "tool": "FSL BET",
        "version": "6.0.5",
        "parameters": {
            "options": "-m"
        }
    }
    output_entities: dict = {
        "desc": "bet",
        "suffix": "T1w",
        "extension": ".nii.gz"
    }
    
    # Forced outputs - files that are saved are by the application but not NeuroAnalyst-compliant
    forced_outputs: list[str] = [output_filepath, mask_filepath]

    return brain_data, metrics, output_entities, forced_outputs