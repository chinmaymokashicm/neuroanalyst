from pathlib import Path

import numpy as np
import nibabel as nib
from dipy.denoise.gibbs import gibbs_removal


def dipy_remove_gibbs_ringing(input_filepath: str):
    """
    Remove Gibbs ringing artifacts from a DWI image using DIPY.

    Args:
        input_filepath (str): Path to the input DWI NIfTI file.

    Returns:
        output_data (np.ndarray): Gibbs-corrected image data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """

    # ============================
    # Step 1: Load Input Data
    # ============================
    img: nib.Nifti1Image = nib.load(input_filepath)
    img_data: np.ndarray = img.get_fdata()
    affine: np.ndarray = img.affine
    header: nib.Nifti1Header = img.header

    if img_data.ndim < 4:
        raise ValueError("Input image must be a 4D DWI image.")

    # ============================
    # Step 2: Apply Gibbs ringing removal
    # ============================
    # Apply along spatial axes only
    gibbs_corrected_data: np.ndarray = gibbs_removal(img_data, slice_axis=2)

    corrected_img: nib.Nifti1Image = nib.Nifti1Image(gibbs_corrected_data, affine, header)
    output_data: np.ndarray = corrected_img.get_fdata()

    # ============================
    # Step 3: Prepare Outputs
    # ============================
    metrics: dict = {
        "correction_method": "Gibbs ringing removal",
        "input_shape": img_data.shape,
        "output_shape": output_data.shape,
    }

    output_entities: dict = {
        "suffix": "gibbsCorrected",
        "desc": "dwi",
    }

    forced_outputs: list = []  # No forced outputs in this step

    return output_data, metrics, output_entities, forced_outputs
