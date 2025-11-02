from neuroanalyst.analysis.freesurfer import extract_all_freesurfer_metrics, export_metrics

import os, subprocess, json
from pathlib import Path
import traceback
from typing import Optional

import nibabel as nib
import numpy as np
import pandas as pd
from bids.layout import parse_file_entities
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
        rm /data/tmp/freesurfer_subjects/{subject_id}/scripts/IsRunning.lh+rh
    
    !NOT IMPLEMENTED FOR DEBUGGING - Cleans out temporary files after processing to save space.
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (np.ndarray): Array of cortical surface data. 
            Shape will be (X, Y, Z, 1) where the last dimension corresponds to [cortical_surface].
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
    
    # Load sidecar of input file to check for QC results
    input_sidecar_path: str = input_filepath.replace(".nii.gz", ".nii").replace(".nii", ".json") # Works for both .nii and .nii.gz
    qc_pass_autorecon2: Optional[bool] = None
    if os.path.exists(input_sidecar_path):
        try:
            with open(input_sidecar_path, 'r') as f:
                input_sidecar = json.load(f)
            qc_pass_autorecon2 = input_sidecar.get("metrics", {}).get("qc_pass", {}).get("autorecon2", None)
        except Exception as e:
            print(f"Error reading sidecar JSON file: {e}")

    # Step 2: Prepare FreeSurfer command
    input_entities: dict = parse_file_entities(input_filepath)
    subject_id: str = f"{input_entities.get('subject', 'unknown')}_{input_entities.get('session', 'ses-unknown')}"
    fs_subjects_dir: str = os.path.join(tmp_dir, "freesurfer_subjects")
    os.makedirs(fs_subjects_dir, exist_ok=True)
    
    cmd: list[str] = [
        "bash", "-c",
        f"""
        source {FREESURFER_HOME}/SetUpFreeSurfer.sh && \\
        export OMP_NUM_THREADS=4 && \\
        export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4 && \\
        recon-all -s {subject_id} -sd {fs_subjects_dir} -autorecon3
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
    all_metrics: dict = extract_all_freesurfer_metrics(os.path.join(fs_subjects_dir, subject_id))
    # Separate values that are dicts and those that are pd.DataFrames
    # The dictionary metrics will go into sidecar, while DataFrames will be saved as CSV outputs.
    dict_metrics: dict = {}
    for key, value in all_metrics.items():
        if isinstance(value, dict):
            dict_metrics[key] = value
        else:
            pass

    try:
        # Save all metrics to directory
        export_metrics(all_metrics, output_dir=os.path.dirname(input_filepath))
    except Exception as e:
        print(f"Error exporting FreeSurfer metrics: {e}")
    
    # Return surface stats as output data and save cortical metrics DataFrames as CSV
    try:
        output_data: pd.DataFrame = pd.read_csv(os.path.join(os.path.dirname(input_filepath), "surface_statistics.csv"))
    except Exception as e:
        print(f"Error loading surface_statistics.csv: {e}")
        output_data = pd.DataFrame()
    try:
        df_cortical_bilateral: pd.DataFrame = pd.read_csv(os.path.join(os.path.dirname(input_filepath), "cortical_regional_metrics_bilateral.csv"))
    except Exception as e:
        print(f"Error loading cortical_regional_metrics_bilateral.csv: {e}")
        df_cortical_bilateral = pd.DataFrame()
    
        cortical_file_entities: dict = {**input_entities}
        cortical_file_entities.update({
            "desc": "cortical",
            "suffix": "stats",
            "extension": ".csv",
            })
        
        custom_path_patterns = [
            "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][acq-{acquisition}_][run-{run}_][desc-{desc}_]{suffix}{extension}",
            "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][task-{task}_][acq-{acquisition}_][ce-{ce}_][dir-{dir}_][rec-{rec}_][run-{run}_][echo-{echo}_][desc-{desc}_]{suffix}{extension}",
            "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][task-{task}_][acq-{acquisition}_][run-{run}_][desc-{desc}_]{suffix}{extension}",
            "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][space-{space}_][hemi-{hemi}_][model-{model}_][desc-{desc}_]{suffix}{extension}",
            "[sub-{subject}/][ses-{session}/][sample-{sample}/]{datatype}/sub-{subject}_[ses-{session}_][sample-{sample}_][desc-{desc}_]{suffix}{extension}",
            "[sub-{subject}/][ses-{session}/][sample-{sample}/][modality-{modality}_]{datatype}/sub-{subject}_[ses-{session}_][sample-{sample}_][modality-{modality}_][desc-{desc}_]{suffix}{extension}"
            ]
        
        cortical_output_filename: str = build_path(cortical_file_entities, path_patterns=custom_path_patterns)
        cortical_output_filepath: str = os.path.join(os.path.dirname(input_filepath), cortical_output_filename)
        os.makedirs(os.path.dirname(cortical_output_filepath), exist_ok=True)
        df_cortical_bilateral.to_csv(cortical_output_filepath, index=False)

    # Step 5: Prepare metrics and output entities
    try:
        # QC metrics
        qc_results = qc_autorecon3(os.path.join(fs_subjects_dir, subject_id, "stats"))
        if qc_pass_autorecon2 is None:
            qc_pass_autorecon2 = qc_results["qc_pass"]
    except Exception as e:
        print(f"Error computing QC metrics for Autorecon3: {e}")
        qc_results = {"mean_thickness": None, "surface_area": None, "qc_pass": None}
        
    metrics = {
        "parameters": {
            "FreeSurfer_version": os.getenv("FREESURFER_VERSION", "unknown"),
        },
        "mean_thickness": qc_results["mean_thickness"],
        "surface_area": qc_results["surface_area"],
        "qc_pass": {
            "autorecon2": qc_pass_autorecon2,
            "autorecon3": qc_results["qc_pass"]
        },
        **dict_metrics
    }
    
    output_entities = {
        "desc": "surface",
        "suffix": "stats",
        "extension": ".csv",
    }
    
    return output_data, metrics, output_entities, []