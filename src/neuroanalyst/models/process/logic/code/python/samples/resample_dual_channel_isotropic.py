from neuroanalyst.models.process.logic.core import Metric

from pathlib import Path
import os
import json

import nibabel as nib
import numpy as np
import SimpleITK as sitk


def resample_dual_channel_isotropic(input_filepath: str):
    """
    Resample dual-channel image + labelmap to isotropic voxel spacing. The input is expected to have two channels:
        1st channel: preprocessed T1w image
        2nd channel: segmentation labelmap (FreeSurfer anatomical labels)
        
    The purpose is to ensure that both channels have isotropic voxel spacing for radiomics feature extraction.

    Args:
        input_filepath (str): Path to the input dual-channel image file.
        
    Returns:
        output_data (np.ndarray): Resampled dual-channel image data. Shape : (X', Y', Z', 2).
            1st channel: resampled preprocessed T1w image
            2nd channel: resampled segmentation labelmap
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """    
    TARGET_SPACING = (1.0, 1.0, 1.0)

    input_img: nib.Nifti1Image = nib.load(input_filepath)
    input_img_data: np.ndarray = input_img.get_fdata()
    affine = input_img.affine
    zooms = input_img.header.get_zooms()[:3]

    if input_img_data.shape[-1] != 2:
        raise ValueError("Input must be a dual-channel NIfTI (image + labelmap).")

    image = input_img_data[..., 0]
    labelmap = input_img_data[..., 1]

    def _to_sitk(array: np.ndarray, affine: np.ndarray) -> sitk.Image:
        sitk_img = sitk.GetImageFromArray(array)

        spacing = np.sqrt((affine[:3, :3] ** 2).sum(axis=0))
        direction = (affine[:3, :3] / spacing).flatten()
        origin = affine[:3, 3]

        sitk_img.SetSpacing(tuple(spacing[::-1]))
        sitk_img.SetDirection(tuple(direction))
        sitk_img.SetOrigin(tuple(origin[::-1]))

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

    sitk_image = _to_sitk(image, affine)
    
    if not np.all(np.mod(labelmap, 1) == 0):
        raise ValueError("Labelmap contains non-integer values.")
    sitk_labelmap = _to_sitk(labelmap.astype(np.uint16), affine)

    resampled_image = sitk.GetArrayFromImage(
        _resample(sitk_image, TARGET_SPACING, is_label=False)
    )
    resampled_labelmap = sitk.GetArrayFromImage(
        _resample(sitk_labelmap, TARGET_SPACING, is_label=True)
    )

    output_data = np.stack([resampled_image, resampled_labelmap], axis=-1)

    # Get mask file name from input
    input_sidecar_path = input_filepath.split(".")[0] + ".json"
    with open(input_sidecar_path, 'r') as f:
        sidecar_data = json.load(f)
        labelmap_filename = sidecar_data.get("metrics", {}).get("labelmap_filename", None)

    metrics = {
        "original_spacing": zooms,
        "target_spacing": TARGET_SPACING,
        "original_shape": input_img_data.shape,
        "resampled_shape": output_data.shape,
        "labelmap_filename": labelmap_filename,
        "resampling": "sitkLinear_image_sitkNearest_label"
    }

    output_entities = {
        "desc": "resampled",
        "modality": "T1w",
        "extension": ".nii.gz",
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs