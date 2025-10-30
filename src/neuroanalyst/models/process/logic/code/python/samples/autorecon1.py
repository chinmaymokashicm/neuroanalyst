import os, subprocess

import nibabel as nib
import numpy as np
from bids.layout import parse_file_entities


def autorecon1(input_filepath: str):
    """
    FreeSurfer Autorecon1.
    Runs FreeSurfer's autorecon1 on the input NIfTI file. (https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all)
    
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
    DATA_DIR: str = "/data"  # shared data dir bind
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME", "default_pipeline")
    tmp_dir: str = os.path.join(DATA_DIR, "tmp")  #! Temporary directory for outputs; which would be usually be cleaned up by NeuroAnalyst wrapper, but here we keep it for FreeSurfer's intermediate files.
    os.makedirs(tmp_dir, exist_ok=True)
    
    freesurfer_location: str = "/opt/freesurfer"  # Assuming FreeSurfer is installed here
    # Source FreeSurfer and check if 
    source_cmd: str = f"source {freesurfer_location}/SetUpFreeSurfer.sh && recon-all -version"
    os.environ["FREESURFER_HOME"] = freesurfer_location
    try:
        result = subprocess.run(source_cmd, shell=True, executable="/bin/bash", check=True, capture_output=True, text=True)
        print(f"FreeSurfer environment sourced successfully: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error sourcing FreeSurfer environment: {e}")
        raise e
    
    # Step 2: Prepare FreeSurfer command
    entities: dict = parse_file_entities(input_filepath)
    subject_id: str = f"{entities.get('subject', 'unknown')}_{entities.get('session', 'ses-unknown')}"
    fs_subjects_dir: str = os.path.join(tmp_dir, "freesurfer_subjects")
    os.makedirs(fs_subjects_dir, exist_ok=True)
    
    cmd: str = f"""
    source {freesurfer_location}/SetUpFreeSurfer.sh && \
    recon-all -i {input_filepath} -s {subject_id} -sd {fs_subjects_dir} -autorecon1
    """
    
    # Step 3: Run the FreeSurfer command
    print(f"Running command: {cmd}")
    result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    print(f"FreeSurfer Autorecon1 command finished with return code {result.returncode}")
    
    # Step 4: Prepare outputs
    brain_filepath: str = os.path.join(fs_subjects_dir, subject_id, "mri", "brain.mgz")
    brain_mask_filepath: str = os.path.join(fs_subjects_dir, subject_id, "mri", "brainmask.mgz")

    brain_img = nib.load(brain_filepath)
    brain_mask_img = nib.load(brain_mask_filepath)
    brain_data = np.stack([brain_img.get_fdata(), brain_mask_img.get_fdata()], axis=-1)
    
    # QC metrics
    mask_ratio: float = np.sum(brain_mask_img.get_fdata() > 0) / brain_data.size
    mask_intensity_mean: float = np.mean(brain_img.get_fdata()[brain_mask_img.get_fdata() > 0])

    metrics = {
        "brain_volume": np.sum(brain_mask_img.get_fdata() > 0),
        "brain_dimensions": brain_data.shape[:-1],
        "mask_ratio": mask_ratio,
        "mask_intensity_mean": mask_intensity_mean,
        "qc_pass": 0.25 <= mask_ratio <= 0.6 and 40 <= mask_intensity_mean <= 200,
        "qc_notes": (
            "Mask ratio or intensity mean out of expected range."
            if not (0.25 <= mask_ratio <= 0.6 and 40 <= mask_intensity_mean <= 200)
            else "QC passed."
        ),
        "qc_criteria": {
            "mask_ratio_range": [0.25, 0.6],
            "mask_intensity_mean_range": [40, 200]
        },
        "output_channels": [
            "brain",
            "brain_mask"
        ],
        "parameters": {
            "FreeSurfer_version": os.getenv("FREESURFER_VERSION", "unknown"),
        },
        "original_output_path": fs_subjects_dir,
    }
    
    output_entities = {
        "desc": "autorecon1",
        "suffix": "T1w",
        "extension": ".nii.gz"
    }
    
    
    # forced_outputs = [brain_filepath, brain_mask_filepath]
    forced_outputs = []
    
    # Save supplementary outputs by BIDS compliance
    # talairach_filepath: str = os.path.join(fs_subjects_dir, subject_id, "mri", "talairach.mgz")

    return brain_data, metrics, output_entities, forced_outputs