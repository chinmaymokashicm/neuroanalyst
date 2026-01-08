from neuroanalyst.models.process.logic.core import Metric

from pathlib import Path
import os

import nibabel as nib
import numpy as np
from bids.layout import parse_file_entities

def prepare_dual_channel_from_reconall(input_filepath: str):
    """
    Prepare dual-channel image from recon-all output for radiomics feature extraction.
    The first channel contains the preprocessed T1-weighted image, and the second channel contains the segmentation labelmap (FreeSurfer anatomical labels).
    
    Purpose of dual-channel image - to provide both intensity and anatomical context for radiomics analysis.
    
    Preprocessed T1w labelmap in priority of availability:
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
    
    image_path: Path = fs_subject_session_results_root_dir / "mri" / "norm.mgz"
    labelmap_filename_priority_list: list = [
        "aparc+aseg",
        "aseg",
        "aseg.auto",
        "wmparc",
        # "brainmask"
    ]
    labelmap_path: Path = None
    labelmap_type: str = ""
    for labelmap_filename in labelmap_filename_priority_list:
        candidate_labelmap_path: Path = fs_subject_session_results_root_dir / "mri" / (labelmap_filename + ".mgz")
        if candidate_labelmap_path.exists():
            labelmap_path = candidate_labelmap_path
            labelmap_type = labelmap_filename
            break
        
    if labelmap_path is None:
        raise FileNotFoundError("No suitable labelmap file found in recon-all outputs.")
    
    # Load image and labelmap data
    image_nifti: nib.Nifti1Image = nib.Nifti1Image(nib.load(str(image_path)).get_fdata(), np.eye(4))
    labelmap_nifti: nib.Nifti1Image = nib.Nifti1Image(nib.load(str(labelmap_path)).get_fdata(), image_nifti.affine, image_nifti.header)
    image_data: np.ndarray = image_nifti.get_fdata()
    labelmap_data: np.ndarray = labelmap_nifti.get_fdata()
    
    if image_data.shape != labelmap_data.shape:
        raise ValueError("Image and labelmap voxel dimensions do not match.")

    if not np.allclose(image_nifti.affine, labelmap_nifti.affine):
        raise ValueError("Image and labelmap affines do not match.")
    
    # Create dual-channel data
    output_data = np.stack([image_data, labelmap_data], axis=-1)
    
    CATEGORY: str = "anatomical"
    
    SEGMENTATION_COVERAGE = {
        "aparc+aseg": "cortical+subcortical",
        "aseg": "subcortical",
        "wmparc": "white_matter",
        "aseg.auto": "subcortical_auto"
    }
    coverage = SEGMENTATION_COVERAGE.get(labelmap_type, "unknown")

    metrics = {
        "image_shape": image_data.shape,
        "labelmap_shape": labelmap_data.shape,
        "labelmap_filename": labelmap_path.name,
        "labelmap_type": Metric(name="labelmap_type", value=labelmap_type, description="Type of the segmentation labelmap used", unit=None, category=CATEGORY, labels=["labelmap", "type"]),
        "segmentation_coverage": Metric(name="segmentation_coverage", value=coverage, description="Anatomical coverage of the segmentation labelmap", unit=None, category=CATEGORY, labels=["labelmap", "coverage"]),
    }
    output_entities = {
        "desc": "dual",
        "suffix": "T1w",
        "extension": ".nii.gz"
    }
    forced_outputs = [] # No forced outputs in this case
    
    return output_data, metrics, output_entities, forced_outputs