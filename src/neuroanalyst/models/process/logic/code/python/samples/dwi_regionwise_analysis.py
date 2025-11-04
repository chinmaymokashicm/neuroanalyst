from neuroanalyst.analysis.dwi import summarize_regionwise_metrics

from pathlib import Path
import os, json, shutil
from warnings import warn

import numpy as np
import pandas as pd
import nibabel as nib
from nilearn.image import resample_to_img
from dipy.io.image import load_nifti
from bids.layout import parse_file_entities
from bids.layout.writing import build_path
from nilearn.image import resample_to_img

def dwi_regionwise_analysis(input_filepath: str):
    """
    Perform region-wise analysis of DWI-derived metrics using anatomical labels.
    
    Args:
        input_filepath (str): Path to input registered DWI NIfTI file.
            Shape will be (X, Y, Z, 6) where the last dimension corresponds to 
            [FA, MD, AD, RD, ColorFA, Trace].
    Returns:
        output_data (pd.DataFrame): DataFrame summarizing region-wise metrics.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    input_dir: str = Path(input_filepath).parent
    input_file_stem: str = Path(input_filepath).stem.split(".")[0]
    bval_file, bvec_file, json_file = [os.path.join(input_dir, f"{input_file_stem}{extension}") for extension in [".bval", ".bvec", ".json"]]
    pipeline_name: str = os.getenv("PIPELINE_NAME", None)
    pipeline_dir: str = os.path.join("/data", "derivatives", pipeline_name)
    if not pipeline_name:
        raise EnvironmentError("PIPELINE_NAME environment variable is not set.")
    dwi_pipeline_name: str = os.getenv("DWI_PIPELINE_NAME", None)
    if not dwi_pipeline_name:
        raise EnvironmentError("DWI_PIPELINE_NAME environment variable is not set.")
    t1w_pipeline_name: str = os.getenv("T1W_PIPELINE_NAME", None)
    if not t1w_pipeline_name:
        raise EnvironmentError("T1W_PIPELINE_NAME environment variable is not set.")
    
    input_entities: dict = parse_file_entities(input_filepath)
    subject_id, session_id = None, None
    if "subject" in input_entities:
        subject_id = input_entities["subject"]
    if "session" in input_entities:
        session_id = input_entities["session"]

    # Get FA, MD, AD, RD maps filepath
    custom_path_patterns = [
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][acq-{acquisition}_][run-{run}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][task-{task}_][acq-{acquisition}_][ce-{ce}_][dir-{dir}_][rec-{rec}_][run-{run}_][echo-{echo}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][task-{task}_][acq-{acquisition}_][run-{run}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][space-{space}_][hemi-{hemi}_][model-{model}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/][sample-{sample}/]{datatype}/sub-{subject}_[ses-{session}_][sample-{sample}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/][sample-{sample}/][modality-{modality}_]{datatype}/sub-{subject}_[ses-{session}_][sample-{sample}_][modality-{modality}_][desc-{desc}_]{suffix}{extension}"
        ]
    
    dwi_pipeline_dir: str = os.path.join("/data", "derivatives", dwi_pipeline_name)
    map_file_entities = input_entities.copy()
    map_file_entities.update({"suffix": "dwi", "desc": "tensor", "extension": ".nii.gz"})
    dwi_tensor_filepath: str = os.path.join(dwi_pipeline_dir, build_path(map_file_entities, custom_path_patterns))
    if not os.path.exists(dwi_tensor_filepath):
        warn(f"DWI tensor file not found at expected location: {dwi_tensor_filepath}. Attempting to find any other tensor file of the subject and session...")
        same_subject_session_files = [f for f in os.listdir(dwi_pipeline_dir) if input_entities["subject"] in f and (("session" not in input_entities) or (input_entities["session"] in f)) and "desc-tensor" in f and f.endswith(".nii.gz")]
        if len(same_subject_session_files) == 0:
            raise FileNotFoundError(f"No DWI tensor files found for subject {subject_id} in {dwi_pipeline_dir}")
        dwi_tensor_filepath = os.path.join(dwi_pipeline_dir, same_subject_session_files[0])
        print(f"Found DWI tensor file at alternative path: {dwi_tensor_filepath}")
    print(f"Loading DWI tensor data from {dwi_tensor_filepath}...")
    dwi_tensor_img = nib.load(dwi_tensor_filepath)
    dwi_tensor_data = dwi_tensor_img.get_fdata()
    print(f"DWI tensor data shape: {dwi_tensor_data.shape}")
    try:
        fa_data = dwi_tensor_data[..., 0]
        md_data = dwi_tensor_data[..., 1]
        ad_data = dwi_tensor_data[..., 2]
        rd_data = dwi_tensor_data[..., 3]
    except Exception as e:
        raise ValueError(f"Error extracting DWI metrics from tensor data: {e}")
    print("Extracted FA, MD, AD, RD maps from DWI tensor data.")

    # Get aparc+aseg file from FreeSurfer outputs
    t1w_pipeline_dir: str = os.path.join("/data", "derivatives", t1w_pipeline_name)
    # Get freesurfer subject dir name
    subject_dirname: str = f"{subject_id}"
    if session_id:
        subject_dirname += f"_{session_id}"
    if subject_dirname == "":
        subject_dirname = "unknown_subject"
    freesurfer_subjects_dir: str = os.path.join(t1w_pipeline_dir, "tmp", "freesurfer_subjects", subject_dirname)
    aparc_aseg_filepath: str = os.path.join(freesurfer_subjects_dir, "mri", "aparc+aseg.mgz")
    if not os.path.exists(aparc_aseg_filepath):
        # raise FileNotFoundError(f"aparc+aseg file not found at expected location: {aparc_aseg_filepath}")
        warn(f"Aparc+Aseg T1w image not found at expected path: {aparc_aseg_filepath}. Attempting to find any other T1w image of the subject...")
        same_subject_id_dirnames = [dir_name for dir_name in os.listdir(os.path.join(t1w_pipeline_dir, "tmp", "freesurfer_subjects")) if dir_name.startswith(f"{subject_id}")]
        if len(same_subject_id_dirnames) == 0:
            raise FileNotFoundError(f"No FreeSurfer subject directories found for subject {subject_id} in {os.path.join(t1w_pipeline_dir, 'tmp', 'freesurfer_subjects')}")
        subject_dirname = same_subject_id_dirnames[0]
        freesurfer_subjects_dir = os.path.join(t1w_pipeline_dir, "tmp", "freesurfer_subjects", subject_dirname)
        aparc_aseg_filepath = os.path.join(freesurfer_subjects_dir, "mri", "aparc+aseg.mgz")
        if not os.path.exists(aparc_aseg_filepath):
            raise FileNotFoundError(f"Aparc+Aseg T1w image still not found at path: {aparc_aseg_filepath}")
        else:
            print(f"Found Aparc+Aseg T1w image at alternative path: {aparc_aseg_filepath}")
    aparc_aseg_img = nib.load(aparc_aseg_filepath)
    print(f"Loaded aparc+aseg image from {aparc_aseg_filepath}. Shape: {aparc_aseg_img.shape}")
    
    # Resample aparc+aseg to DWI space
    resampled_aparc_aseg_img = resample_to_img(aparc_aseg_img, dwi_tensor_img, interpolation='nearest')
    resampled_aparc_aseg_data = resampled_aparc_aseg_img.get_fdata()
    print(f"Resampled aparc+aseg image to DWI space. Shape: {resampled_aparc_aseg_data.shape}")
    
    # Perform region-wise analysis
    output_data: pd.DataFrame = summarize_regionwise_metrics(
        label_data=resampled_aparc_aseg_data,
        metric_data_dict={
            "FA": fa_data,
            "MD": md_data,
            "AD": ad_data,
            "RD": rd_data
        }
    )
    print("Computed region-wise DWI metrics.")
    
    # Prepare metrics
    metrics: dict = {
        "num_regions": int(output_data.shape[0]),
        "metrics_computed": ["FA", "MD", "AD", "RD"],
        "dwi_tensor_filepath": dwi_tensor_filepath,
        "aparc_aseg_filepath": aparc_aseg_filepath,
        "t1w_pipeline_name": t1w_pipeline_name,
        "dwi_pipeline_name": dwi_pipeline_name
    }
    
    output_entities: dict = {
        "desc": "dwiRegionwise",
        "suffix": "stats",
        "extension": ".csv"
    }
    
    forced_outputs: list = []

    return output_data, metrics, output_entities, forced_outputs