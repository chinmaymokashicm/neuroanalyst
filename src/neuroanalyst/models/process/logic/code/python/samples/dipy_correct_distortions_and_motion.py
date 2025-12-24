from pathlib import Path

import numpy as np
import nibabel as nib
from dipy.align.imaffine import AffineMap
from dipy.align.transforms import RigidTransform3D
from dipy.align.imaffine import MutualInformationMetric, AffineRegistration

def dipy_correct_distortions_and_motion(input_filepath: str):
    """
    Correct motion and eddy current distortions in a DWI image using DIPY.

    Args:
        input_filepath (str): Path to the input DWI NIfTI file.

    Returns:
        output_data (np.ndarray): Corrected DWI image data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
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

    n_volumes = img_data.shape[3]

    # ============================
    # Step 2: Simple Motion Correction
    # ============================
    # Align each volume to the first b0 volume (assumes first volume is b0)
    # Using a simple rigid-body affine registration
    reference_volume = img_data[..., 0]
    corrected_data = np.zeros_like(img_data)

    corrected_data[..., 0] = reference_volume  # reference stays the same

    # Affine registration metric
    metric = MutualInformationMetric(nbins=32, sampling_proportion=None)
    affreg = AffineRegistration(metric=metric, level_iters=[1000, 100, 10], sigmas=[3.0, 1.0, 0.0], factors=[4, 2, 1])

    for i in range(1, n_volumes):
        moving = img_data[..., i]
        transform = affreg.optimize(
            static=reference_volume,
            moving=moving,
            transform=RigidTransform3D(),
            params0=None,
            static_grid2world=None,
            moving_grid2world=None
        )
        corrected_data[..., i] = transform.transform(moving)

    # ============================
    # Step 3: Placeholder for Eddy & Susceptibility
    # ============================
    # For full correction, FSL 'eddy' or 'topup' would be used.
    # Here we only do rigid-body motion correction.

    # ============================
    # Step 4: Prepare Outputs
    # ============================
    corrected_img = nib.Nifti1Image(corrected_data, affine, header)
    output_data = corrected_img.get_fdata()

    metrics: dict = {
        "correction_method": "motion_rigid_affine",
        "num_volumes": n_volumes,
        "note": "Eddy current and susceptibility corrections are placeholders; full correction requires FSL eddy/topup.",
        "bvecs_updated": False, # In a full implementation, bvecs would be updated based on motion parameters
    }

    output_entities: dict = {
        "suffix": "motion",
        "desc": "corrected",
    }

    forced_outputs: list = []  # No extra files generated in this simple implementation

    return output_data, metrics, output_entities, forced_outputs
