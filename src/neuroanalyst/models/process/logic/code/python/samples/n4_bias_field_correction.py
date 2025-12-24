from src.neuroanalyst.models.process.logic.core import Metric

import os
from pathlib import Path
from typing import Optional

import numpy as np
import SimpleITK as sitk
import nibabel as nib


def n4_bias_field_correction(input_filepath: str):
    """Apply N4 Bias Field Correction to a 3D or 4D image using SimpleITK.

    Args:
        input_filepath (str): Path to the input nifti file.

    Returns:
        output_data (np.ndarray): Bias-field corrected image data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """

    # ============================
    # Step 1: Load Input Data
    # ============================
    DATA_DIR: str = "/data"
    img: nib.Nifti1Image = nib.load(input_filepath)
    img_data: np.ndarray = img.get_fdata()
    
    # ============================
    # Step 2: Apply N4 Bias Field Correction
    # ============================
    if img_data.ndim == 4:
        # Apply N4 correction on each volume separately
        output_data = np.zeros_like(img_data)
        for i in range(img_data.shape[3]):
            sitk_img = sitk.GetImageFromArray(img_data[..., i])
            n4_corrector = sitk.N4BiasFieldCorrectionImageFilter()
            corrected_sitk_img = n4_corrector.Execute(sitk_img)
            output_data[..., i] = sitk.GetArrayFromImage(corrected_sitk_img)
    else:
        sitk_img = sitk.GetImageFromArray(img_data)
        n4_corrector = sitk.N4BiasFieldCorrectionImageFilter()
        corrected_sitk_img = n4_corrector.Execute(sitk_img)
        output_data = sitk.GetArrayFromImage(corrected_sitk_img)

    # ============================
    # Step 3: Prepare Outputs
    # ============================
    metrics: dict = {
        "correction_method": "N4 Bias Field Correction",
        "input_shape": img_data.shape,
        "output_shape": output_data.shape,
    }

    output_entities: dict = {
        "suffix": "n4corrected",
        "desc": "dwi",
    }

    forced_outputs: list = [] # Placeholder for forced outputs

    return output_data, metrics, output_entities, forced_outputs