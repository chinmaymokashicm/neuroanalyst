import os, subprocess, json, traceback
from pathlib import Path
from typing import Optional

import nibabel as nib
from nibabel import gifti
import numpy as np
from bids.layout import parse_file_entities
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
        output_data (np.ndarray): Array of segmentation data ("aseg.presurf.mgz") and white matter separated ("wm.mgz").
            Shape will be (X, Y, Z, 2) where the last dimension corresponds to [segmentation, white_matter].
            *Note - this output is only as a reference for downstream processing; the actual outputs are saved in FreeSurfer's subject directory structure.
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
    
    def to_gifti(vertices: np.ndarray, faces: np.ndarray):
        gii = gifti.GiftiImage()
        gii.add_gifti_data_array(gifti.GiftiDataArray(data=vertices, intent='NIFTI_INTENT_POINTSET'))
        gii.add_gifti_data_array(gifti.GiftiDataArray(data=faces, intent='NIFTI_INTENT_TRIANGLE'))
        return gii

    # Step 1: Prepare environment and paths
    DATA_DIR: str = "/data"  # shared data dir bind
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME", "default_pipeline")
    FREESURFER_HOME: str = os.getenv("FREESURFER_HOME", None)
    if not FREESURFER_HOME:
        raise EnvironmentError("FREESURFER_HOME environment variable is not set.")
    freesurfer_outputs_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")  #! Temporary directory for outputs; which would be usually be cleaned up by NeuroAnalyst wrapper, but here we keep it for FreeSurfer's intermediate files.
    os.makedirs(freesurfer_outputs_dir, exist_ok=True)
    
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
    
    cmd: list[str] = [
        "bash", "-c",
        f"""source {FREESURFER_HOME}/SetUpFreeSurfer.sh && \\
        export OMP_NUM_THREADS=4 && \\
        export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4 && \\
        recon-all -s {subject_dirname} -sd {fs_subjects_dir} -autorecon2
        """
    ]

    # Step 3: Prepare outputs
    aseg_filepath: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "aseg.presurf.mgz")
    wm_filepath: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "wm.seg.mgz")
    
    if not os.path.exists(aseg_filepath) or not os.path.exists(wm_filepath):
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
    
    aseg_data = nib.load(aseg_filepath).get_fdata()
    wm_data = nib.load(wm_filepath).get_fdata()
    
    output_data = np.stack([aseg_data, wm_data], axis=-1)
    
    # # Step 5: Prepare metrics and output entities
    # aseg_stats_path: str = os.path.join(fs_subjects_dir, subject_dirname, "stats", "aseg.stats")
    # try:
    #     qc_results = qc_autorecon2(aseg_stats_path)
    #     if qc_pass is None:
    #         qc_pass = qc_results["qc_pass"]
    # except Exception as e:
    #     print(f"Warning: Could not parse aseg stats for QC metrics: {e}")
    #     qc_results = {}
    
    metrics = {
        "total_brain_volume": int(np.sum(aseg_data > 0)),
        "white_matter_volume": int(np.sum(wm_data > 0)),
        "num_labels": int(len(np.unique(aseg_data))),
        "segmentation_dimensions": aseg_data.shape,
        "segmentation_classes": int(np.max(aseg_data)),
        "output_channels": [
            {"name": "segmentation", "description": "Automated segmentation (aseg.presurf.mgz)"},
            {"name": "white_matter", "description": "White matter segmentation (wm.mgz)"}
        ],
        "qc_pass": {
            "autorecon1": qc_pass_autorecon1,
            # "autorecon2": qc_results.get("qc_pass", None)
        },
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
    
    # forced_outputs = [aseg_filepath, wm_filepath]
    forced_outputs = []
    
    try:
        # Save supplementary outputs by BIDS compliance
        lh_surface_filepath: str = os.path.join(fs_subjects_dir, subject_dirname, "surf", "lh.smoothwm")
        rh_surface_filepath: str = os.path.join(fs_subjects_dir, subject_dirname, "surf", "rh.smoothwm")
        lh_surface_bids_entities: dict = {**entities, **{
            "hemi": "L",
            "desc": "surf",
            "suffix": "smoothwm",
            "extension": ".surf.gii",
        }}
        rh_surface_bids_entities: dict = {**entities, **{
            "hemi": "R",
            "desc": "surf",
            "suffix": "smoothwm",
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
        input_dir: str = os.path.dirname(input_filepath)
        lh_surface_bids_filepath: str = os.path.join(input_dir, lh_surface_bids_filename)
        rh_surface_bids_filepath: str = os.path.join(input_dir, rh_surface_bids_filename)
        os.makedirs(os.path.dirname(lh_surface_bids_filepath), exist_ok=True)
        os.makedirs(os.path.dirname(rh_surface_bids_filepath), exist_ok=True)
        
        try:
            for hemi_surface_filepath, bids_filepath in [
                (lh_surface_filepath, lh_surface_bids_filepath),
                (rh_surface_filepath, rh_surface_bids_filepath)
            ]:
                vertices, faces = nib.freesurfer.read_geometry(hemi_surface_filepath)
                gii_data = to_gifti(vertices, faces)
                nib.save(gii_data, bids_filepath)
                forced_outputs.append(bids_filepath)
        except Exception as e:
            print(f"Warning: Could not save supplementary surface outputs: {e}")
    except Exception as e:
        print(f"Warning: Could not save supplementary surface outputs: {e}")
    

    return output_data, metrics, output_entities, forced_outputs