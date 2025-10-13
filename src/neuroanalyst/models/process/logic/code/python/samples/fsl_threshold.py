import os
import subprocess
from pathlib import Path

import nibabel as nib
import numpy as np

def fsl_threshold(input_filepath: str):
    """
    Performs thresholding on tissue segmentation outputs from FSL FAST using FSL fslmaths.
    Uses a Nifti file that has been segmented by FSL FAST. The input is expected to be a multi-channel Nifti file
    where each channel corresponds to a tissue type (CSF, GM, WM), seg, mixeltype, and restored image.
    Assumptions-
    - The path of the FSL Singularity image is mounted to /opt/fsl in the container
    - The name of the image is passed via the FSL_IMG_NAME environment variable.
    - Apptainer/Singularity is available in the container.
    - All the required parameters are passed via environment variables.
      If not provided, default values will be used.
    
    Args:
        input_filepath (str): Path to input NIfTI file. Takes the segmented output from FSL FAST as input.
    Returns:
        output_data (np.ndarray): Array of binary masks for each tissue type (CSF, GM, WM), seg, mixeltype, and restored image.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    # Step 1: Prepare environment and paths
    threshold: int = int(os.getenv("THRESHOLD", "0.5"))
    
    DATA_DIR = "/data"  # shared data dir bind
    fsl_img_name = os.getenv("FSL_IMG_NAME")
    fsl_img_path = f"/opt/fsl_images/{fsl_img_name}"  # path to FSL Singularity image inside container
    
    output_dir = os.path.join(DATA_DIR, "tmp")

    # Step 2: Define output file paths - this is necessary because fslmaths creates outputs automatically.
    # These outputs will then be deleted by the NeuroAnalyst wrapper.
    # We need to pass the actual output data to the NeuroAnalyst wrapper, so that it can be saved correctly with exhaustive metadata.
    # Load the tissues (CSF, GM, WM) from the input segmented file
    img = nib.load(input_filepath)
    img_data = img.get_fdata()
    if img_data.ndim != 4 or img_data.shape[3] < 3:
        raise ValueError("Input NIfTI file must be a 4D file with at least 3 channels (CSF, GM, WM).")
    csf_data = img_data[:, :, :, 0]
    gm_data = img_data[:, :, :, 1]
    wm_data = img_data[:, :, :, 2]
    
    # Save temporary files for each tissue type
    input_filename = input_filepath.split("/")[-1]
    csf_temp_path = os.path.join(output_dir, input_filename.replace(".nii.gz", "_csf_temp.nii.gz"))
    gm_temp_path = os.path.join(output_dir, input_filename.replace(".nii.gz", "_gm_temp.nii.gz"))
    wm_temp_path = os.path.join(output_dir, input_filename.replace(".nii.gz", "_wm_temp.nii.gz"))

    for data, path in zip([csf_data, gm_data, wm_data], [csf_temp_path, gm_temp_path, wm_temp_path]):
        nib.save(nib.Nifti1Image(data, img.affine, img.header), path)

    # Temporary output paths
    csf_output_path = csf_temp_path.replace("_temp", "_thresh")
    gm_output_path = gm_temp_path.replace("_temp", "_thresh")
    wm_output_path = wm_temp_path.replace("_temp", "_thresh")
    
    # Step 3: Build and run the Apptainer/Singularity command. This runs FSL FAST inside an Apptainer container.
    internal_bash_command: str = f"""
. ${{FSLDIR}}/etc/fslconf/fsl.sh
fslmaths {csf_temp_path} -thr {threshold} -bin {csf_output_path}
fslmaths {gm_temp_path} -thr {threshold} -bin {gm_output_path}
fslmaths {wm_temp_path} -thr {threshold} -bin {wm_output_path}
    """
    cmd = [
        "apptainer", "exec",
        fsl_img_path,
        "bash", "-c", internal_bash_command
    ]
    print(f"Running command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, check=True)
    print(f"FSL fslmaths command finished with return code {result.returncode}")
    
    print(f"=== Command Output ===\n{result.stdout}\n===================")
    print(result.stdout)
    
    print(f"=== Command Error (if any) ===\n{result.stderr}\n===================")
    print(result.stderr)


    if result.returncode != 0:
        raise RuntimeError(f"FSL fslmaths command failed with return code {result.returncode}")

    # Step 4: Load output data and prepare return values
    # This is necessary because the NeuroAnalyst wrapper expects the output data to be returned from this function.
    # The wrapper will then save the data to the appropriate NeuroAnalyst-compliant location with metadata.
    
    # Compute volume metrics for each tissue type
    tissue_data_list = []
    for tissue_path in [csf_output_path, gm_output_path, wm_output_path]:
        tissue_img = nib.load(tissue_path)
        tissue_data = tissue_img.get_fdata()
        tissue_data_list.append(tissue_data)

    # Forced outputs - files that are saved are by the application but not NeuroAnalyst-compliant
    forced_outputs = {
        "CSF": csf_output_path,
        "GM": gm_output_path,
        "WM": wm_output_path
    }
    output_data = np.stack(tissue_data_list, axis=-1)  # shape will be (X, Y, Z, 3)
    print(f"Stacked output data shape: {output_data.shape}")
    
    # Compute relevant metrics
    metrics: dict = {
        "shape": output_data.shape,
        "csf_volume": int((output_data[..., 0] > 0).sum()),
        "gm_volume": int((output_data[..., 1] > 0).sum()),
        "wm_volume": int((output_data[..., 2] > 0).sum()),
        "tool": "FSL fslmaths",
        "threshold": threshold
    }
    
    output_entities: dict = {
        "desc": "fslmaths",
        "suffix": "mask",
        "extension": ".nii.gz"
    }

    return output_data, metrics, output_entities, forced_outputs