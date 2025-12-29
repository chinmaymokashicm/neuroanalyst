from neuroanalyst.models.process.logic.core import Metric

import os, subprocess, json, traceback
from pathlib import Path
from typing import Optional

import nibabel as nib
from nibabel import gifti
import numpy as np
from bids.layout import parse_file_entities, BIDSLayout
from bids.layout.writing import build_path


def autorecon2(input_filepath: str):
    """
    FreeSurfer Autorecon2. Performs tissue segmentation.
    Runs FreeSurfer's autorecon2 on the input NIfTI file. (https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all).
    Assumes that autorecon1 has been run previously and the subject directory exists.
    6.  EM Register (linear volumetric registration)
    7.  CA Intensity Normalization
    8.  CA Non-linear Volumetric Registration 
    9.  Remove neck
    10. EM Register, with skull
    11. CA Label (Aseg: Volumetric Labeling) and Statistics

    12. Intensity Normalization 2 (start here for control points)
    13. White matter segmentation
    14. Edit WM With ASeg
    15. Fill (start here for wm edits)
    16. Tessellation (begins per-hemisphere operations)
    17. Smooth1
    18. Inflate1
    19. QSphere
    20. Automatic Topology Fixer
    21. White Surfs (start here for brain edits for pial surf)
    22. Smooth2
    23. Inflate2
    
    Notes for future implementations and error handling:
    - If a subject directory has been created previously, re-running with -i flag will error out. Remove the flag or delete the subject directory beforehand.
    - If a process is already running for the same subject, it will error out. Run this command to check and remove the lock:
        rm /data/tmp/freesurfer_subjects/{subject_dirname}/scripts/IsRunning.lh+rh
    
    Args:
        input_filepath (str): Path to input NIfTI file. Loads the reference image from the previous autorecon1 step. Has 2 channels - intensity-normalized brain and skull-stripped brain.
    Returns:
        output_data (nib.Nifti1Image): NIfTI image of the aseg segmentation from FreeSurfer.
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
    
    # Check if mri/brainmask.mgz exists from autorecon1 step - if not, raise error
    brainmask_mgz_path: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "brainmask.mgz")
    if not os.path.exists(brainmask_mgz_path):
        raise FileNotFoundError(f"Expected brainmask.mgz from autorecon1 step not found: {brainmask_mgz_path}. Please run autorecon1 first.")
    
    cmd: list[str] = [
        "bash", "-c",
        f"""source {FREESURFER_HOME}/SetUpFreeSurfer.sh && \\
        export OMP_NUM_THREADS=8 && \\
        export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=8 && \\
        export SUBJECTS_DIR={fs_subjects_dir} && \\
        recon-all -s {subject_dirname} -autorecon2 -autorecon2-wm -autorecon2-cp -autorecon2-pial
        """
    ]

    # Step 3: Prepare outputs
    aseg_filepath: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "aseg.presurf.mgz")
    
    if not os.path.exists(aseg_filepath):
        # Step 4: Run the FreeSurfer command
        print(f"Running command: {cmd}")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"FreeSurfer Autorecon2 command finished with return code {result.returncode}")
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
    
    # Load the aseg file and convert to NIfTI
    output_data: nib.Nifti1Image = nib.Nifti1Image.from_image(nib.load(aseg_filepath))
    
    # Step 5: Prepare metrics and output entities
    metrics = {
        "brain_volume": int(np.sum(output_data.get_fdata() > 0)),
        "parameters": {
            "FreeSurfer_version": FREESURFER_HOME.split("/")[-1],
        },
        "original_output_path": fs_subjects_dir,
    }
    
    output_entities = {
        "desc": "autorecon2",
        "suffix": "seg",
        "extension": ".nii.gz"
    }
    
    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs