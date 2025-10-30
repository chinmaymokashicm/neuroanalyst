import os, subprocess, json
from pathlib import Path
from typing import Optional

import nibabel as nib
import numpy as np
from bids.layout import parse_file_entities
from bids.layout.writing import build_path

def autorecon3(input_filepath: str):
    """
    FreeSurfer Autorecon3. Performs cortical surface reconstruction.
    Runs FreeSurfer's autorecon3 on the input NIfTI file. (https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all).
    Assumes that autorecon2 has been run previously and the subject directory exists.
    
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
    tmp_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")  #! Temporary directory for outputs; which would be usually be cleaned up by NeuroAnalyst wrapper, but here we keep it for FreeSurfer's intermediate files.
    os.makedirs(tmp_dir, exist_ok=True)
    
    # Load sidecar of input file to check for QC results
    input_sidecar_path: str = input_filepath.replace(".nii.gz", ".nii").replace(".nii", ".json") # Works for both .nii and .nii.gz
    qc_pass_autorecon2: Optional[bool] = None
    if os.path.exists(input_sidecar_path):
        with open(input_sidecar_path, 'r') as f:
            input_sidecar = json.load(f)
        qc_pass_autorecon2 = input_sidecar.get("metrics", {}).get("qc_pass", {}).get("autorecon2", None)
    
    # Step 2: Prepare FreeSurfer command
    entities: dict = parse_file_entities(input_filepath)
    subject_id: str = f"{entities.get('subject', 'unknown')}_{entities.get('session', 'ses-unknown')}"
    fs_subjects_dir: str = os.path.join(tmp_dir, "freesurfer_subjects")
    os.makedirs(fs_subjects_dir, exist_ok=True)
    
    cmd: str = f"""
    source '{FREESURFER_HOME}'/SetUpFreeSurfer.sh && \\
    export OMP_NUM_THREADS=4 && \\
    export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4 && \\
    recon-all -s '{subject_id}' -sd '{fs_subjects_dir}' -autorecon3 -qcache -measure thickness
    """
    
    # Step 3: Run the FreeSurfer command
    print(f"Running command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, executable="/bin/bash")
        print(f"FreeSurfer Autorecon3 command finished with return code {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Error running FreeSurfer Autorecon3 command: {e.stderr}")
        raise e
    
    # Step 4: Prepare outputs
    cortical_surface_filepath: str = os.path.join(fs_subjects_dir, subject_id, "surf", "lh.pial")
    # Convert surface to nibabel Gifti format
    vertices, faces = nib.freesurfer.read_geometry(cortical_surface_filepath)
    
    output_data = nib.GiftiImage()
    coords = nib.GiftiDataArray(data=vertices, intent=nib.nifti1.intent_codes['NIFTI_INTENT_POINTSET'])
    faces_array = nib.GiftiDataArray(data=faces, intent=nib.nifti1.intent_codes['NIFTI_INTENT_TRIANGLE'])
    output_data.add_gifti_data_array(coords)
    output_data.add_gifti_data_array(faces_array)
    
    # Step 5: Prepare metrics and output entities
    qc_results = qc_autorecon3(os.path.join(fs_subjects_dir, subject_id, "stats"))
    metrics = {
        "parameters": {
            "FreeSurfer_version": os.getenv("FREESURFER_VERSION", "unknown"),
        },
        "mean_thickness": qc_results["mean_thickness"],
        "surface_area": qc_results["surface_area"],
        "qc_pass": {
            "autorecon2": qc_pass_autorecon2,
            "autorecon3": qc_results["qc_pass"]
        }
    }
    
    output_entities = {
        "desc": "cortical_surface",
        "suffix": "surf",
        "extension": ".surf.gii",
    }
    
    return output_data, metrics, output_entities, []