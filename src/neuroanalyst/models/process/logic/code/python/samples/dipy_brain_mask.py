import nibabel as nib
import numpy as np
from dipy.segment.mask import median_otsu

def dipy_brain_mask(input_filepath: str):
    """
    Apply brain masking to a DWI image using DIPY median_otsu.

    Args:
        input_filepath (str): Path to the input DWI NIfTI file.

    Returns:
        output_data (np.ndarray): Brain-masked DWI image data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of extra outputs (e.g., mask file).
    """
    # ----------------------------
    # Load data
    # ----------------------------
    img = nib.load(input_filepath)
    data = img.get_fdata()
    affine = img.affine
    header = img.header

    if data.ndim < 4:
        raise ValueError("Input image must be 4D DWI data.")

    # ----------------------------
    # Compute mean b0 (assume first volume)
    # ----------------------------
    b0 = data[..., 0]

    # ----------------------------
    # Median Otsu masking
    # ----------------------------
    masked_b0, mask = median_otsu(
        b0,
        vol_idx=None,
        median_radius=4,
        numpass=4,
        autocrop=False
    )

    # Apply mask to all volumes
    output_data = data * mask[..., np.newaxis]

    # ----------------------------
    # Outputs
    # ----------------------------
    metrics = {
        "masking_method": "median_otsu",
        "mask_shape": mask.shape,
        "num_volumes": data.shape[3],
    }

    output_entities = {
        "suffix": "masked",
        "desc": "brain",
    }

    forced_outputs = []  # mask could be saved later if desired

    return output_data, metrics, output_entities, forced_outputs
