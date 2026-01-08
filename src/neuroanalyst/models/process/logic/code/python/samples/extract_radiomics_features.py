from neuroanalyst.models.process.logic.core import Metric
from neuroanalyst.analysis.freesurfer import load_freesurfer_color_lut

from pathlib import Path
from typing import Optional
import os
import json

import nibabel as nib
import numpy as np
import pandas as pd
import SimpleITK as sitk
from radiomics import featureextractor

def extract_radiomics_features(input_filepath: str):
    """
    Extract radiomics features by ROI from preprocessed dual-channel image data.
    The mask, if multi-label, will be itertively processed for each label by binarizing the mask.
    
    Args:
        input_filepath (str): Path to the input dual-channel image file.
        
    Returns:
        output_data (pd.DataFrame): DataFrame containing extracted radiomics features.
            Columns include:
                - label_id
                - mask_filename
                - roi_namespace
                - roi_label
                - roi_type
                - roi_hemisphere
                - roi_region
                - [radiomics features...]
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """
    def _to_sitk(array: np.ndarray, affine: np.ndarray) -> sitk.Image:
        sitk_img = sitk.GetImageFromArray(array)

        spacing = np.sqrt((affine[:3, :3] ** 2).sum(axis=0))
        direction = tuple(np.eye(3).flatten())
        origin = affine[:3, 3]

        sitk_img.SetSpacing(tuple(spacing[::-1]))
        sitk_img.SetDirection(tuple(direction))
        sitk_img.SetOrigin(tuple(origin[::-1]))

        return sitk_img
    
    def _extract_features_for_label(label):
        binary_mask = (mask_data == label).astype(np.uint8)
        mask_sitk = _to_sitk(binary_mask, dual_channel_image.affine)
        features = extractor.execute(image_sitk, mask_sitk)
        return features
    
    def _safe_enable_features(extractor: featureextractor.RadiomicsFeatureExtractor, feature_class: str, feature_names: list[str]) -> list[str]:
        """
        Enable PyRadiomics features safely.
        Returns list of successfully enabled features.
        """
        enabled = []
        for name in feature_names:
            try:
                extractor.enableFeaturesByName(**{feature_class: [name]})
                enabled.append(name)
            except LookupError:
                print(f"[radiomics] Skipping missing feature: {feature_class}.{name}")
        return enabled
    
    def str_to_bool(s: str) -> Optional[bool]:
        if s is None:
            return None
        elif s.lower() in ['true', '1', 'yes']:
            return True
        elif s.lower() in ['false', '0', 'no']:
            return False
        else:
            return None
    
    df_lut: pd.DataFrame = load_freesurfer_color_lut()
    def _infer_roi_metadata(label: int) -> dict:
        row = df_lut[df_lut["Index"] == label]

        if row.empty:
            return {
                "roi_namespace": "freesurfer",
                "roi_label": f"unknown_{label}",
                "roi_type": "unknown",
                "roi_hemisphere": "unknown",
                "roi_region": "unknown",
            }

        label_name = row.iloc[0]["StructName"].strip()
        lname = label_name.lower()

        # Hemisphere
        if lname.startswith("left"):
            hemisphere = "lh"
        elif lname.startswith("right"):
            hemisphere = "rh"
        else:
            hemisphere = "midline"

        # Broad anatomical region
        if "cerebellum" in lname:
            region = "cerebellum"
        elif "brainstem" in lname:
            region = "brainstem"
        else:
            region = "cerebrum"

        # Tissue / ROI type
        if "cortex" in lname:
            roi_type = "cortical_gm"
        elif "white-matter" in lname:
            roi_type = "wm"
        elif "ventricle" in lname or "vent" in lname:
            roi_type = "csf"
        elif any(k in lname for k in [
            "thalamus", "caudate", "putamen", "pallidum",
            "hippocampus", "amygdala", "accumbens"
        ]):
            roi_type = "subcortical_gm"
        else:
            roi_type = "other"

        return {
            "roi_namespace": "freesurfer",
            "roi_label": label_name,
            "roi_type": roi_type,
            "roi_hemisphere": hemisphere,
            "roi_region": region,
        }
        
    # Get mask file name from input
    # Check if normalization was applied
    # Check if resampling was applied
    try:
        input_sidecar_path = input_filepath.split(".")[0] + ".json"
        with open(input_sidecar_path, 'r') as f:
            sidecar_data = json.load(f)
            mask_filename = sidecar_data.get("metrics", {}).get("labelmap_filename", None)
            if mask_filename is None:
                mask_filename = sidecar_data.get("metrics", {}).get("mask_filename", None)
            if mask_filename is None:
                raise ValueError("Mask filename not found in sidecar JSON.")
            normalization_info = sidecar_data.get("metrics", {}).get("normalization", None)
            resampling_info = sidecar_data.get("metrics", {}).get("resampling", None)
    except Exception as e:
        raise ValueError(f"Error reading sidecar JSON for mask filename: {e}")
    
    dual_channel_image: nib.Nifti1Image = nib.load(input_filepath)
    data: np.ndarray = dual_channel_image.get_fdata()
    if data.shape[-1] != 2:
        raise ValueError("Input data must have exactly two channels.")
    
    image_data = data[..., 0]
    mask_data = data[..., 1].astype(np.int32)
    image_sitk = _to_sitk(image_data.astype(np.float32), dual_channel_image.affine)
    
    unique_labels = np.unique(mask_data)
    
    parameters = {
        "binWidth": 25,
        "resampledPixelSpacing": [1.0, 1.0, 1.0] if resampling_info is not None else None,
        "interpolator": "sitkBSpline",
        "enableCExtensions": True
    }
    extractor = featureextractor.RadiomicsFeatureExtractor(**parameters)
    enabled_features = {}

    enabled_features["shape"] = _safe_enable_features(
        extractor, "shape",
        ["VoxelVolume", "SurfaceArea", "Sphericity", "Elongation", "MajorAxisLength"]
    )

    enabled_features["firstorder"] = _safe_enable_features(
        extractor, "firstorder",
        ["Mean", "Median", "StandardDeviation", "Skewness", "Kurtosis", "Entropy", "Energy"]
    )

    enabled_features["glcm"] = _safe_enable_features(
        extractor, "glcm",
        [
            "Contrast",
            "Correlation",
            "Homogeneity1",
            "JointEntropy",
            "JointEnergy",
        ]
    )

    enabled_features["glrlm"] = _safe_enable_features(
        extractor, "glrlm",
        ["ShortRunEmphasis", "LongRunEmphasis", "RunEntropy"]
    )

    enabled_features["glszm"] = _safe_enable_features(
        extractor, "glszm",
        ["SmallAreaEmphasis", "LargeAreaEmphasis", "ZoneEntropy"]
    )

    
    all_features = []
    for label in unique_labels:
        if label == 0:
            continue  # Skip background
        features = _extract_features_for_label(label)
        # Remove diagnostic features
        features = {k: v for k, v in features.items() if not k.startswith("diagnostics_")}
        # Add label-specific metadata
        roi_metadata = _infer_roi_metadata(label)
        features.update({
            "label_id": int(label),
            "mask_filename": mask_filename,
            **roi_metadata
        })
        all_features.append(features)
        
    output_data = pd.DataFrame(all_features)
    
    roi_namespaces = []
    try:
        roi_namespaces = sorted(output_data["roi_namespace"].unique().tolist())
    except Exception as e:
        roi_namespaces = []
        print(f"Error extracting roi_namespaces: {e}")
    
    roi_types = []
    try:
        roi_types = sorted(output_data["roi_type"].unique().tolist())
    except Exception as e:
        roi_types = []
        print(f"Error extracting roi_types: {e}")
        
    roi_hemispheres = []
    try:
        roi_hemispheres = sorted(output_data["roi_hemisphere"].unique().tolist())
    except Exception as e:
        roi_hemispheres = []
        print(f"Error extracting roi_hemispheres: {e}")
    
    metrics = {
        "num_labels": len(unique_labels) - 1,  # Exclude background
        "labelmap_filename": mask_filename,
        "normalization": normalization_info,
        "roi_namespaces": roi_namespaces,
        "roi_types": roi_types,
        "roi_hemispheres": roi_hemispheres,
        "enabled_features": enabled_features,
    }
    
    output_entities = {
        "desc": "radiomics",
        "suffix": "T1w",
        "extension": ".tsv"
    }
    
    forced_outputs = [] # No forced outputs in this case
    
    return output_data, metrics, output_entities, forced_outputs
    