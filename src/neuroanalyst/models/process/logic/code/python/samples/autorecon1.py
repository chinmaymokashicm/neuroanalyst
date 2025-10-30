import os, subprocess, traceback

import nibabel as nib
import numpy as np
from bids.layout import parse_file_entities


def autorecon1(input_filepath: str):
    """
    FreeSurfer Autorecon1.
    Runs FreeSurfer's autorecon1 on the input NIfTI file. (https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all).
    
    Notes for future implementations and error handling:
    - If a subject directory has been created previously, re-running with -i flag will error out. Remove the flag or delete the subject directory beforehand.
    - If a process is already running for the same subject, it will error out. Run this command to check and remove the lock:
        rm /data/tmp/freesurfer_subjects/{subject_id}/scripts/IsRunning.lh+rh
    - Add -qcache flag
    
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
    FREESURFER_HOME: str = os.getenv("FREESURFER_HOME", None)
    if not FREESURFER_HOME:
        raise EnvironmentError("FREESURFER_HOME environment variable is not set.")
    tmp_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")  #! Temporary directory for outputs; which would be usually be cleaned up by NeuroAnalyst wrapper, but here we keep it for FreeSurfer's intermediate files.
    os.makedirs(tmp_dir, exist_ok=True)
    
    # Step 2: Prepare FreeSurfer command
    entities: dict = parse_file_entities(input_filepath)
    subject_id: str = f"{entities.get('subject', 'unknown')}_{entities.get('session', 'ses-unknown')}"
    fs_subjects_dir: str = os.path.join(tmp_dir, "freesurfer_subjects")
    os.makedirs(fs_subjects_dir, exist_ok=True)
    
    cmd = [
        "bash", "-c",
        f"""
        source {FREESURFER_HOME}/SetUpFreeSurfer.sh && \\
        export OMP_NUM_THREADS=4 && \\
        export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4 && \\
        recon-all -i '{input_filepath}' -s '{subject_id}' -sd {fs_subjects_dir} -autorecon1
        """
    ]
    
    # Step 3: Run the FreeSurfer command
    print(f"Running command: {cmd}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"FreeSurfer Autorecon1 command finished with return code {result.returncode}")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running FreeSurfer Autorecon1 command: {e}")
        if getattr(e, "stdout", None):
            print("Stdout:", e.stdout)
        if getattr(e, "stderr", None):
            print("Stderr:", e.stderr)
        traceback.print_exc()
        raise e
    
    # Step 4: Prepare outputs
    t1_filepath: str = os.path.join(fs_subjects_dir, subject_id, "mri", "T1.mgz")
    brain_mask_filepath: str = os.path.join(fs_subjects_dir, subject_id, "mri", "brainmask.mgz")

    t1_img: nib.Nifti1Image = nib.load(t1_filepath)
    brain_mask_img: nib.Nifti1Image = nib.load(brain_mask_filepath)
    t1_data = np.stack([t1_img.get_fdata(), brain_mask_img.get_fdata()], axis=-1)
    
    # QC metrics
    mask_ratio = np.sum(brain_mask_img.get_fdata() > 0) / np.prod(t1_img.shape)
    mask_intensity_mean: float = np.mean(t1_img.get_fdata()[brain_mask_img.get_fdata() > 0])

    metrics = {
        "brain_volume": np.sum(brain_mask_img.get_fdata() > 0),
        "brain_dimensions": t1_data.shape[:-1],
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

    return t1_data, metrics, output_entities, forced_outputs