from neuroanalyst.models.process.logic.core import Metric

import os
from pathlib import Path
from typing import Optional

import numpy as np
import nibabel as nib
from dipy.denoise.localpca import mppca


def dipy_denoise_mppca(input_filepath: str):
    """Apply MP-PCA denoising to a raw DWI image using DIPY.

    Args:
        input_filepath (str): Path to the input DWI nifti file.

    Returns:
        output_data (np.ndarray): Denoising image data.
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
    affine: np.ndarray = img.affine
    header: nib.Nifti1Header = img.header
    
    if img_data.ndim < 4:
        raise ValueError("Input image must be a 4D DWI image.")
    
    # ============================
    # Step 2: Apply MP-PCA Denoising
    # ============================
    denoised_data: np.ndarray = mppca(img_data, patch_radius=2, return_sigma=False)
    denoised_img: nib.Nifti1Image = nib.Nifti1Image(denoised_data, affine, header)
    output_data: np.ndarray = denoised_img.get_fdata()
    
    # ============================
    # Step 3: Prepare Outputs
    # ============================
    metrics: dict = {
        "denoising_method": "MP-PCA",
        "input_shape": img_data.shape,
        "output_shape": output_data.shape,
    }

    output_entities: dict = {
        "suffix": "mppcaDenoised",
        "desc": "dwi",
    }

    forced_outputs: list = [] # No forced outputs in this case

    return output_data, metrics, output_entities, forced_outputs