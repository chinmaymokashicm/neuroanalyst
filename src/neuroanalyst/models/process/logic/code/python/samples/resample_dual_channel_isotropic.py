from neuroanalyst.models.process.logic.core import Metric

from pathlib import Path
import os
import json

import nibabel as nib
import numpy as np
import SimpleITK as sitk


def resample_dual_channel_isotropic(input_filepath: str):
    """
    Resample dual-channel image + mask data to isotropic voxel spacing. The input is expected to have two channels:
        1st channel: preprocessed T1w image
        2nd channel: segmentation mask (FreeSurfer anatomical labels)
        
    The purpose is to ensure that both channels have isotropic voxel spacing for radiomics feature extraction.

    Args:
        input_filepath (str): Path to the input dual-channel image file.
        
    Returns:
        output_data (np.ndarray): Resampled dual-channel image data. Shape : (X', Y', Z', 2).
            1st channel: resampled preprocessed T1w image
            2nd channel: resampled segmentation mask
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """
    
    TARGET_SPACING = (1.0, 1.0, 1.0)

    nifti = nib.load(input_filepath)
    data = nifti.get_fdata()
    affine = nifti.affine
    zooms = nifti.header.get_zooms()[:3]

    if data.shape[-1] != 2:
        raise ValueError("Input must be a dual-channel NIfTI (image + mask).")

    image = data[..., 0]
    mask = data[..., 1]

    def _to_sitk(array: np.ndarray, spacing: tuple[float, float, float]) -> sitk.Image:
        sitk_img: sitk.Image = sitk.GetImageFromArray(array)
        sitk_img.SetSpacing(spacing[::-1])  # SITK uses z, y, x
        return sitk_img

    def _resample(sitk_img: sitk.Image, spacing: tuple[float, float, float], is_label: bool = False) -> sitk.Image:
        original_spacing = sitk_img.GetSpacing()
        original_size = sitk_img.GetSize()

        new_size = [
            int(round(osz * ospc / tspc))
            for osz, ospc, tspc in zip(original_size, original_spacing, spacing[::-1])
        ]

        resampler = sitk.ResampleImageFilter()
        resampler.SetOutputSpacing(spacing[::-1])
        resampler.SetSize(new_size)
        resampler.SetInterpolator(
            sitk.sitkNearestNeighbor if is_label else sitk.sitkLinear
        )
        resampler.SetOutputDirection(sitk_img.GetDirection())
        resampler.SetOutputOrigin(sitk_img.GetOrigin())

        return resampler.Execute(sitk_img)

    sitk_image = _to_sitk(image, zooms)
    sitk_mask = _to_sitk(mask, zooms)

    resampled_image = sitk.GetArrayFromImage(
        _resample(sitk_image, TARGET_SPACING, is_label=False)
    )
    resampled_mask = sitk.GetArrayFromImage(
        _resample(sitk_mask, TARGET_SPACING, is_label=True)
    )

    output_data = np.stack([resampled_image, resampled_mask], axis=-1)

    # Get mask file name from input
    input_sidecar_path = input_filepath.split(".")[0] + ".json"
    with open(input_sidecar_path, 'r') as f:
        sidecar_data = json.load(f)
        mask_filename = sidecar_data.get("metrics", {}).get("mask_filename", None)["value"]

    metrics = {
        "original_spacing": zooms,
        "target_spacing": Metric(name="target_spacing", value=TARGET_SPACING, description="Target voxel spacing", unit="mm"),
        "original_shape": Metric(name="original_shape", value=data.shape, description="Original shape of the dual-channel image", unit="voxels"),
        "resampled_shape": Metric(name="resampled_shape", value=output_data.shape, description="Shape of the resampled dual-channel image", unit="voxels"),
        "mask_filename": Metric(name="mask_filename", value=mask_filename, description="Filename of the segmentation mask", unit=None)
    }

    output_entities = {
        "desc": "resampled",
        "modality": "T1w",
        "extension": ".nii.gz",
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs