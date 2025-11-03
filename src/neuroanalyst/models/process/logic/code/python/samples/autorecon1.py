import os, subprocess, traceback

import nibabel as nib
import numpy as np
from bids.layout import parse_file_entities


def autorecon1(input_filepath: str):
    """
    FreeSurfer Autorecon1.
    Runs FreeSurfer's autorecon1 on the input NIfTI file. (https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all).
        1.  Motion Correction and Conform
        2.  NU (Non-Uniform intensity normalization)
        3.  Talairach transform computation
        4.  Intensity Normalization 1
        5.  Skull Strip
    
    Notes for future implementations and error handling:
    - If a subject directory has been created previously, re-running with -i flag will error out. Remove the flag or delete the subject directory beforehand.
    - If a process is already running for the same subject, it will error out. Run this command to check and remove the lock:
        rm /data/tmp/freesurfer_subjects/{subject_dirname}/scripts/IsRunning.lh+rh
    - Add -qcache flag
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (np.ndarray): Array of intensity-normalized brain ("T1") and skull-stripped brain ("brainmask.mgz").
            Shape will be (X, Y, Z, 2) where the last dimension corresponds to [T1, brainmask].
            *Note - this output is only as a reference for downstream processing; the actual outputs are saved in FreeSurfer's subject directory structure.
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
    freesurfer_outputs_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")  #! Temporary directory for outputs; which would be usually be cleaned up by NeuroAnalyst wrapper, but here we keep it for FreeSurfer's intermediate files.
    os.makedirs(freesurfer_outputs_dir, exist_ok=True)
    
    # Step 2: Prepare FreeSurfer command
    entities: dict = parse_file_entities(input_filepath)
    subject_dirname: str = ""
    subject_id, session_id = None, None
    if "subject" in entities:
        subject_id = entities["subject"]
    if "session" in entities:
        session_id = entities["session"]
    subject_dirname = f"{subject_id}"
    if session_id:
        subject_dirname += f"_{session_id}"
    if subject_dirname == "":
        subject_dirname = "unknown_subject"
    fs_subjects_dir: str = os.path.join(freesurfer_outputs_dir, "freesurfer_subjects")
    os.makedirs(fs_subjects_dir, exist_ok=True)
    
    cmd = [
        "bash", "-c",
        f"""
        source {FREESURFER_HOME}/SetUpFreeSurfer.sh && \\
        export OMP_NUM_THREADS=4 && \\
        export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4 && \\
        recon-all -i '{input_filepath}' -s '{subject_dirname}' -sd {fs_subjects_dir} -autorecon1
        """
    ]
    
    # Step 3: Prepare outputs
    skull_stripped_filepath: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "brainmask.mgz")
    t1_filepath: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "T1.mgz")

    if not os.path.exists(skull_stripped_filepath) or not os.path.exists(t1_filepath):
        # Step 4: Run the FreeSurfer command if the outputs do not already exist
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
    else:
        print("Outputs already exist. Skipping FreeSurfer command execution.")

    skull_stripped_img: nib.Nifti1Image = nib.load(skull_stripped_filepath)
    t1_img: nib.Nifti1Image = nib.load(t1_filepath)
    t1_data: np.ndarray = t1_img.get_fdata()[..., np.newaxis]
    skull_stripped_data: np.ndarray = skull_stripped_img.get_fdata()[..., np.newaxis]
    t1_data = np.concatenate([t1_data, skull_stripped_data], axis=-1)  # Shape: (X, Y, Z, 2)
    
    # Calculate metrics using skull-stripped image and whole T1 image
    brain_volume: float = np.sum(skull_stripped_img.get_fdata() > 0) * np.prod(skull_stripped_img.header.get_zooms()[:3])  # in mm³
    
    # QC metrics
    mask_ratio: float = np.sum(skull_stripped_img.get_fdata() > 0) / np.sum(t1_img.get_fdata() > 0)
    mask_intensity_mean: float = np.mean(t1_img.get_fdata()[skull_stripped_img.get_fdata() > 0])

    metrics = {
        "brain_volume": brain_volume,
        "brain_dimensions": t1_data.shape[:-1],
        "qc_pass": 0.25 <= mask_ratio <= 0.6 and 40 <= mask_intensity_mean <= 200,
        "qc_metrics": {
            "mask_ratio": mask_ratio,
            "mask_intensity_mean": mask_intensity_mean
        },
        "qc_notes": (
            "Mask ratio or intensity mean out of expected range."
            if not (0.25 <= mask_ratio <= 0.6 and 40 <= mask_intensity_mean <= 200)
            else "QC passed."
        ),
        "qc_criteria": {
            "mask_ratio_range": [0.25, 0.6],
            "mask_intensity_mean_range": [40, 200]
        },
        "channels": [
            {"name": "T1", "description": "Intensity-normalized T1-weighted image"},
            {"name": "brainmask", "description": "Skull-stripped brain mask"}
        ],
        "parameters": {
            "FreeSurfer_version": FREESURFER_HOME.split("/")[-1],
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
    # talairach_filepath: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "talairach.mgz")

    return t1_data, metrics, output_entities, forced_outputs