import os, subprocess, json, traceback
from pathlib import Path
from typing import Optional

import nibabel as nib
import numpy as np
from bids.layout import parse_file_entities
from bids.layout.writing import build_path


def autorecon2(input_filepath: str):
    """
    FreeSurfer Autorecon2. Performs tissue segmentation.
    Runs FreeSurfer's autorecon2 on the input NIfTI file. (https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all).
    Assumes that autorecon1 has been run previously and the subject directory exists.
    
    Notes for future implementations and error handling:
    - If a subject directory has been created previously, re-running with -i flag will error out. Remove the flag or delete the subject directory beforehand.
    - If a process is already running for the same subject, it will error out. Run this command to check and remove the lock:
        rm /data/tmp/freesurfer_subjects/{subject_id}/scripts/IsRunning.lh+rh
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (np.ndarray): Array of segmentation data. 
            Shape will be (X, Y, Z, 1) where the last dimension corresponds to [segmentation].
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    def parse_aseg_stats(aseg_stats_path):
        vols = {}
        with open(aseg_stats_path) as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.split()
                vols[parts[4]] = float(parts[3])
        return vols
    
    def qc_autorecon2(aseg_stats_path):
        vols = parse_aseg_stats(aseg_stats_path)
        wm_ok = 200000 < vols.get("Left-Cerebral-White-Matter", 0) < 400000
        bs_ok = 15000 < vols.get("Brain-Stem", 0) < 30000
        return {"qc_pass": wm_ok and bs_ok, "volumes": vols}

    # Step 1: Prepare environment and paths
    DATA_DIR: str = "/data"  # shared data dir bind
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME", "default_pipeline")
    FREESURFER_HOME: str = os.getenv("FREESURFER_HOME", None)
    if not FREESURFER_HOME:
        raise EnvironmentError("FREESURFER_HOME environment variable is not set.")
    tmp_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")  #! Temporary directory for outputs; which would be usually be cleaned up by NeuroAnalyst wrapper, but here we keep it for FreeSurfer's intermediate files.
    pipeline_dir: str = os.path.join(DATA_DIR, "pipelines", PIPELINE_NAME)
    os.makedirs(tmp_dir, exist_ok=True)
    
    # Load sidecar of input file to check for QC results
    input_sidecar_path: str = input_filepath.replace(".nii.gz", ".nii").replace(".nii", ".json") # Works for both .nii and .nii.gz
    qc_pass_autorecon1: Optional[bool] = None
    if os.path.exists(input_sidecar_path):
        with open(input_sidecar_path, 'r') as f:
            input_sidecar = json.load(f)
        qc_pass_autorecon1 = input_sidecar.get("metrics", {}).get("qc_pass", None)
        
    if qc_pass_autorecon1 is False:
        print("Input file failed QC. autorecon2 should be skipped.")
        # output_data = np.array([])  # Empty array to indicate no processing
        # metrics = {
        #     "qc_skipped": True
        # }
        # output_entities = {
        #     "desc": "autorecon2_skipped",
        #     "suffix": "seg",
        #     "extension": ".nii.gz"
        # }
        # forced_outputs = []
        # return output_data, metrics, output_entities, forced_outputs
        
    # Step 2: Prepare FreeSurfer command
    entities: dict = parse_file_entities(input_filepath)
    subject_id: str = f"{entities.get('subject', 'unknown')}_{entities.get('session', 'ses-unknown')}"
    fs_subjects_dir: str = os.path.join(tmp_dir, "freesurfer_subjects")
    os.makedirs(fs_subjects_dir, exist_ok=True)
    
    cmd: str = f"""
    source '{FREESURFER_HOME}'/SetUpFreeSurfer.sh && \\
    export OMP_NUM_THREADS=4 && \\
    export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4 && \\
    recon-all -s '{subject_id}' -sd '{fs_subjects_dir}' -autorecon2
    """
    
    # Step 3: Run the FreeSurfer command
    print(f"Running command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, executable="/bin/bash")
        print(f"FreeSurfer Autorecon2 command finished with return code {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Error running FreeSurfer Autorecon2 command: {e.stderr}")
        traceback.print_exc()
        raise e

    # Step 4: Prepare outputs
    aseg_filepath: str = os.path.join(fs_subjects_dir, subject_id, "mri", "aseg.mgz")
    wm_filepath: str = os.path.join(fs_subjects_dir, subject_id, "mri", "wm.mgz")
    
    aseg_data = nib.load(aseg_filepath).get_fdata()
    wm_data = nib.load(wm_filepath).get_fdata()
    
    output_data = np.stack([aseg_data, wm_data], axis=-1)
    
    # Step 5: Prepare metrics and output entities
    aseg_stats_path: str = os.path.join(fs_subjects_dir, subject_id, "stats", "aseg.stats")
    try:
        qc_results = qc_autorecon2(aseg_stats_path)
        if qc_pass is None:
            qc_pass = qc_results["qc_pass"]
    except Exception as e:
        print(f"Warning: Could not parse aseg stats for QC metrics: {e}")
        qc_results = {}
    
    metrics = {
        "total_brain_volume": np.sum(aseg_data > 0),
        "white_matter_volume": np.sum(wm_data > 0),
        "segmentation_dimensions": aseg_data.shape,
        "segmentation_classes": int(np.max(aseg_data)),
        "output_channels": [
            "segmentation",
            "white_matter"
        ],
        "qc_pass": {
            "autorecon1": qc_pass_autorecon1,
            "autorecon2": qc_results.get("qc_pass", None)
        },
        "parameters": {
            "FreeSurfer_version": os.getenv("FREESURFER_VERSION", "unknown"),
        },
        "original_output_path": fs_subjects_dir,
    }
    
    output_entities = {
        "desc": "autorecon2",
        "suffix": "seg",
        "extension": ".nii.gz"
    }
    
    # forced_outputs = [aseg_filepath, wm_filepath]
    forced_outputs = []
    
    # Save supplementary outputs by BIDS compliance
    lh_surface_filepath: str = os.path.join(fs_subjects_dir, subject_id, "surf", "lh.white")
    rh_surface_filepath: str = os.path.join(fs_subjects_dir, subject_id, "surf", "rh.white")
    lh_surface_bids_entities: dict = {**entities, **{
        "hemi": "L",
        "desc": "surf",
        "suffix": "pial",
        "extension": ".surf.gii",
    }}
    rh_surface_bids_entities: dict = {**entities, **{
        "hemi": "R",
        "desc": "surf",
        "suffix": "pial",
        "extension": ".surf.gii",
    }}
    custom_path_patterns = [
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][acq-{acquisition}_][run-{run}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][task-{task}_][acq-{acquisition}_][ce-{ce}_][dir-{dir}_][rec-{rec}_][run-{run}_][echo-{echo}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][task-{task}_][acq-{acquisition}_][run-{run}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][space-{space}_][hemi-{hemi}_][model-{model}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/][sample-{sample}/]{datatype}/sub-{subject}_[ses-{session}_][sample-{sample}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/][sample-{sample}/][modality-{modality}_]{datatype}/sub-{subject}_[ses-{session}_][sample-{sample}_][modality-{modality}_][desc-{desc}_]{suffix}{extension}"
        ]
    
    lh_surface_bids_filename: str = build_path(lh_surface_bids_entities, path_patterns=custom_path_patterns)
    rh_surface_bids_filename: str = build_path(rh_surface_bids_entities, path_patterns=custom_path_patterns)
    lh_surface_bids_filepath: str = os.path.join(pipeline_dir, lh_surface_bids_filename)
    rh_surface_bids_filepath: str = os.path.join(pipeline_dir, rh_surface_bids_filename)
    os.makedirs(os.path.dirname(lh_surface_bids_filepath), exist_ok=True)
    os.makedirs(os.path.dirname(rh_surface_bids_filepath), exist_ok=True)
    
    try:
        for hemi_surface_filepath, bids_filepath in [
            (lh_surface_filepath, lh_surface_bids_filepath),
            (rh_surface_filepath, rh_surface_bids_filepath)
        ]:
            mris_convert_cmd = [
                "mris_convert",
                hemi_surface_filepath,
                bids_filepath
            ]
            print(f"Running command: {' '.join(mris_convert_cmd)}")
            result = subprocess.run(mris_convert_cmd, check=True, capture_output=True, text=True)
            print(f"mris_convert command finished with return code {result.returncode}")
            # forced_outputs.append(bids_filepath)
    except Exception as e:
        print(f"Warning: Could not convert surface to GIFTI: {e}")

    return output_data, metrics, output_entities, forced_outputs