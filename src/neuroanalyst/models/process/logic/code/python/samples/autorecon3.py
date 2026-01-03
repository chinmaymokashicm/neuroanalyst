from neuroanalyst.models.process.logic.core import Metric
from neuroanalyst.analysis.freesurfer import load_aparc_stats, extract_cortical_regional_metrics

import os, subprocess, json
from pathlib import Path
import traceback
from typing import Optional

import nibabel as nib
import numpy as np
import pandas as pd
from bids.layout import parse_file_entities, BIDSLayout
from bids.layout.writing import build_path

def autorecon3(input_filepath: str):
    """
    FreeSurfer Autorecon3. Performs cortical surface reconstruction.
    Runs FreeSurfer's autorecon3 on the input NIfTI file. (https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all).
    Assumes that autorecon2 has been run previously and the subject directory exists.
    24. Spherical Mapping
    25. Spherical Registration 
    26. Spherical Registration, Contralater hemisphere
    27. Map average curvature to subject
    28. Cortical Parcellation (Labeling)
    29. Cortical Parcellation Statistics
    30. Pial Surfs
    31. WM/GM Contrast
    32. Cortical Ribbon Mask
    33. Cortical Parcellation mapped to ASeg
    34  Brodmann and exvio EC labels
    
    Notes for future implementations and error handling:
    - If a subject directory has been created previously, re-running with -i flag will error out. Remove the flag or delete the subject directory beforehand.
    - If a process is already running for the same subject, it will error out. Run this command to check and remove the lock:
        rm /data/tmp/freesurfer_subjects/{subject_dirname}/scripts/IsRunning.lh+rh
    
    !NOT IMPLEMENTED FOR DEBUGGING - Cleans out temporary files after processing to save space.
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (pd.DataFrame): DataFrame of cortical surface statistics from "surface_statistics.csv".
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    def qc_autorecon3(stats_dir):
        lh_stats = Path(stats_dir) / "lh.aparc.stats"
        rh_stats = Path(stats_dir) / "rh.aparc.stats"

        def parse_stats(path):
            vals = {}
            with open(path) as f:
                for line in f:
                    if line.startswith("# Measure"):
                        parts = line.split()
                        vals[parts[2]] = float(parts[3])
            return vals

        lh_vals = parse_stats(lh_stats)
        rh_vals = parse_stats(rh_stats)

        mean_thickness = (lh_vals.get("MeanThickness", 0) + rh_vals.get("MeanThickness", 0)) / 2
        surface_area = (lh_vals.get("SurfArea", 0) + rh_vals.get("SurfArea", 0)) / 2

        qc_pass = 2.0 < mean_thickness < 3.5 and 80000 < surface_area < 130000
        return {"mean_thickness": mean_thickness, "surface_area": surface_area, "qc_pass": qc_pass}
    
    # Step 1: Prepare environment and paths
    DATA_DIR: str = "/data"  # shared data dir bind
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME", "default_pipeline")
    FREESURFER_HOME: str = os.getenv("FREESURFER_HOME", None)
    if not FREESURFER_HOME:
        raise EnvironmentError("FREESURFER_HOME environment variable is not set.")
    pipeline_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME)
    tmp_dir: str = os.path.join(pipeline_dir, "tmp")  #! Temporary directory for outputs; which would be usually be cleaned up by NeuroAnalyst wrapper, but here we keep it for FreeSurfer's intermediate files.
    os.makedirs(tmp_dir, exist_ok=True)

    # Step 2: Prepare FreeSurfer command
    input_entities: dict = parse_file_entities(input_filepath)
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
    fs_subjects_dir: str = os.path.join(tmp_dir, "freesurfer_subjects")
    os.makedirs(fs_subjects_dir, exist_ok=True)
    
    # Check if surf/lh or surf/rh exists from autorecon2 step - if not, raise error
    # lh_surf_path: str = os.path.join(fs_subjects_dir, subject_dirname, "surf", "lh.white")
    # rh_surf_path: str = os.path.join(fs_subjects_dir, subject_dirname, "surf", "rh.white")
    # if not os.path.exists(lh_surf_path) or not os.path.exists(rh_surf_path):
    #     raise FileNotFoundError(f"Expected surface files from autorecon2 step not found: {lh_surf_path}, {rh_surf_path}. Please run autorecon2 first.")
    
    # Check if mri/aseg.presurf.mgz, mri/wm.mgz, and mri/filled.mgz exist from autorecon2 step - if not, raise error
    aseg_presurf_path: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "aseg.presurf.mgz")
    wm_mgz_path: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "wm.mgz")
    filled_mgz_path: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "filled.mgz")
    if not os.path.exists(aseg_presurf_path) or not os.path.exists(wm_mgz_path) or not os.path.exists(filled_mgz_path):
        raise FileNotFoundError(f"Expected MRI files from autorecon2 step not found: {aseg_presurf_path}, {wm_mgz_path}, {filled_mgz_path}. Please run autorecon2 first.")
    
    cmd: list[str] = [
        "bash", "-c",
        f"""
        source {FREESURFER_HOME}/SetUpFreeSurfer.sh && \\
        export OMP_NUM_THREADS=8 && \\
        export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=8 && \\
        export SUBJECTS_DIR={fs_subjects_dir} && \\
        recon-all -s {subject_dirname} -autorecon3
        """
    ]
    
    # Step 3: Run the FreeSurfer command
    lh_aparc_path: str = os.path.join(fs_subjects_dir, subject_dirname, "stats", "lh.aparc.stats")
    rh_aparc_path: str = os.path.join(fs_subjects_dir, subject_dirname, "stats", "rh.aparc.stats")
    if not os.path.exists(lh_aparc_path) or not os.path.exists(rh_aparc_path):
        print(f"Running command: {cmd}")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"FreeSurfer Autorecon3 command finished with return code {result.returncode}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error running FreeSurfer Autorecon3 command: {e}")
            if getattr(e, "stdout", None):
                print("Stdout:", e.stdout)
            if getattr(e, "stderr", None):
                print("Stderr:", e.stderr)
            traceback.print_exc()
            raise e
    else:
        print("Outputs already exist. Skipping FreeSurfer command execution.")
    
    # Step 4: Prepare outputs
    if not os.path.exists(lh_aparc_path) or not os.path.exists(rh_aparc_path):
        raise FileNotFoundError(f"Expected aparc.stats files not found: {lh_aparc_path}, {rh_aparc_path}.")
    lh_aparc_annot_path: str = os.path.join(fs_subjects_dir, subject_dirname, "label", "lh.aparc.annot")
    rh_aparc_annot_path: str = os.path.join(fs_subjects_dir, subject_dirname, "label", "rh.aparc.annot")
    if not os.path.exists(lh_aparc_annot_path) or not os.path.exists(rh_aparc_annot_path):
        raise FileNotFoundError(f"Expected aparc.annot files not found: {lh_aparc_annot_path}, {rh_aparc_annot_path}.")
    lh_aparc = load_aparc_stats(lh_aparc_path)
    rh_aparc = load_aparc_stats(rh_aparc_path)
    output_data: pd.DataFrame = extract_cortical_regional_metrics(lh_aparc, rh_aparc)

    # Step 5: Prepare metrics and output entities
    try:
        # QC metrics
        qc_results = qc_autorecon3(os.path.join(fs_subjects_dir, subject_dirname, "stats"))
    except Exception as e:
        print(f"Error computing QC metrics for Autorecon3: {e}")
        qc_results = {"mean_thickness": None, "surface_area": None, "qc_pass": None}
        
    CATEGORY: str = "anatomical"
    metrics = {
        "freesurfer_version": os.getenv("FREESURFER_VERSION", "unknown"),
        "mean_thickness": Metric(
            name="mean_thickness",
            value=qc_results["mean_thickness"],
            description="Mean cortical thickness across hemispheres",
            unit="mm",
            category=CATEGORY,
            labels=["cortical_thickness"],
        ),
        "surface_area": Metric(
            name="surface_area",
            value=qc_results["surface_area"],
            description="Total cortical surface area",
            unit="mm2",
            category=CATEGORY,
            labels=["surface_area"],
        ),
        # **{k: Metric(value=v, description=f"FreeSurfer metric: {k}") for k, v in dict_metrics.items()}
    }
    
    output_entities = {
        "desc": "surface",
        "suffix": "stats",
        "extension": ".csv",
    }
    
    return output_data, metrics, output_entities, []