from neuroanalyst.models.process.logic.core import Metric

from pathlib import Path
import os
import json

import nibabel as nib
import numpy as np

def normalize_intensity_within_segmentation(input_filepath: str):
    """
    Normalize intensity of the first channel (preprocessed T1w image) within the regions defined by the second channel (segmentation mask).
    The input is expected to have two channels:
        1st channel: preprocessed T1w image
        2nd channel: segmentation mask (FreeSurfer anatomical labels)
        
    The purpose is to normalize the intensity values of the T1w image within the segmented regions for consistent radiomics feature extraction.
    Normalization is performed independently for each anatomical label.

    Args:
        input_filepath (str): Path to the input dual-channel image file.
        
    Returns:
        output_data (np.ndarray): Intensity-normalized dual-channel image data. Shape : (X, Y, Z, 2).
            1st channel: intensity-normalized preprocessed T1w image
            2nd channel: segmentation mask
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """
    
    dual_channel_image: nib.Nifti1Image = nib.load(input_filepath)
    input_data: np.ndarray = dual_channel_image.get_fdata()
    if input_data.shape[-1] != 2:
        raise ValueError("Input data must have exactly two channels.")
    
    image = input_data[..., 0]
    mask = input_data[..., 1]
    
    normalized_image = np.copy(image)
    unique_labels = np.unique(mask)
    for label in unique_labels:
        if label == 0:
            continue  # Skip background
        region_voxels = image[mask == label]
        mean_intensity = np.mean(region_voxels)
        std_intensity = np.std(region_voxels)
        if std_intensity > 0:
            normalized_image[mask == label] = (region_voxels - mean_intensity) / std_intensity
        else:
            normalized_image[mask == label] = 0.0  # If std is zero, set to zero
    
    output_data = np.stack([normalized_image, mask], axis=-1)
    
    # Get mask file name from input
    input_sidecar_path = input_filepath.split(".")[0] + ".json"
    with open(input_sidecar_path, 'r') as f:
        sidecar_data = json.load(f)
        mask_filename = sidecar_data.get("metrics", {}).get("mask_filename", None)["value"]
    
    metrics = {
        "unique_labels": unique_labels.tolist(),
        "mask_filename": Metric(name="mask_filename", value=mask_filename, description="Filename of the segmentation mask", unit=None)
    }
    
    output_entities = {
        "desc": "normalized",
        "modality": "T1w",
        "extension": ".nii.gz"
    }
    
    forced_outputs = [] # No forced outputs in this case
    
    return output_data, metrics, output_entities, forced_outputs