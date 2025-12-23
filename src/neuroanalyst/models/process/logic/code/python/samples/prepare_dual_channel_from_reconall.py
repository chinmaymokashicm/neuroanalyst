from neuroanalyst.models.process.logic.core import Metric

from pathlib import Path
import os

import nibabel as nib
import numpy as np
from bids.layout import parse_file_entities

def prepare_dual_channel_from_reconall(input_filepath: str):
    """
    Prepare dual-channel image from recon-all output for radiomics feature extraction.
    The first channel contains the preprocessed T1-weighted image, and the second channel contains the segmentation mask (FreeSurfer anatomical labels).
    
    Preprocessed T1w mask in priority of availability:
        1. aparc+aseg
        2. aseg
        3. aseg.auto
        4. wmparc
        # 5. brainmask
    
    If none of the above are available, raises an error.

    Args:
        input_filepath (str): Path to the input image file. Used as reference to locate recon-all outputs.
        
    Returns:
        output_data (np.ndarray): Dual-channel image data. Shape : (X, Y, Z, 2)
            1st channel: preprocessed T1w image
            2nd channel: segmentation mask (FreeSurfer anatomical labels)
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
        """
    DATA_DIR: str = "/data"
    RECON_ALL_PIPELINE_NAME: str = os.getenv("FS_PIPELINE_NAME")
    if RECON_ALL_PIPELINE_NAME is None:
        raise EnvironmentError("FS_PIPELINE_NAME environment variable is not set.")
    bids_entities: dict = parse_file_entities(input_filepath)
    subject_id, session_id = bids_entities.get("subject"), bids_entities.get("session")
    subject_session_id: str = subject_id + (f"_{session_id}" if session_id else "")
    fs_subject_session_results_root_dir: Path = Path(DATA_DIR) / "derivatives" / RECON_ALL_PIPELINE_NAME / "tmp" / "freesurfer_subjects" / subject_session_id
    
    image_path: Path = fs_subject_session_results_root_dir / "mri" / "norm.nii.gz"
    mask_filename_priority_list: list = [
        "aparc+aseg",
        "aseg",
        "aseg.auto",
        "wmparc",
        # "brainmask"
    ]
    mask_path: Path = None
    for mask_filename in mask_filename_priority_list:
        candidate_mask_path: Path = fs_subject_session_results_root_dir / "mri" / (mask_filename + ".mgz")
        if candidate_mask_path.exists():
            mask_path = candidate_mask_path
            break
        
    if mask_path is None:
        raise FileNotFoundError("No suitable mask file found in recon-all outputs.")
    
    # Load image and mask data
    image_nifti = nib.load(str(image_path))
    mask_nifti = nib.load(str(mask_path))
    image_data = image_nifti.get_fdata()
    mask_data = mask_nifti.get_fdata()
    
    if image_data.shape != mask_data.shape:
        raise ValueError("Image and mask dimensions do not match.")
    
    # Create dual-channel data
    output_data = np.stack([image_data, mask_data], axis=-1)
    
    metrics = {
        "image_shape": Metric(name="image_shape", value=image_data.shape, description="Shape of the input image", unit="voxels"),
        "mask_shape": Metric(name="mask_shape", value=mask_data.shape, description="Shape of the segmentation mask", unit="voxels"),
        "mask_filename": Metric(name="mask_filename", value=mask_filename, description="Filename of the segmentation mask", unit=None)
    }
    output_entities = {
        "desc": "dual",
        "modality": "T1w",
        "extension": ".nii.gz"
    }
    forced_outputs = [] # No forced outputs in this case
    
    return output_data, metrics, output_entities, forced_outputs