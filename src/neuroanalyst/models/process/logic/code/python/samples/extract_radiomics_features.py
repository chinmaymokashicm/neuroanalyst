from neuroanalyst.models.process.logic.core import Metric
from neuroanalyst.analysis.freesurfer import load_freesurfer_color_lut

from pathlib import Path
import os
import json

import nibabel as nib
import numpy as np
import pandas as pd
import SimpleITK as sitk
from radiomics import featureextractor

def extract_radiomics_features(input_filepath: str):
    """
    Extract radiomics features from preprocessed dual-channel image data.
    The mask, if multi-label, will be itertively processed for each label by binarizing the mask.
    
    Args:
        input_filepath (str): Path to the input dual-channel image file.
        
    Returns:
        output_data (pd.DataFrame): DataFrame containing extracted radiomics features.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """
    dual_channel_image: nib.Nifti1Image = nib.load(input_filepath)
    data: np.ndarray = dual_channel_image.get_fdata()
    if data.shape[-1] != 2:
        raise ValueError("Input data must have exactly two channels.")
    
    image_data = data[..., 0]
    mask_data = data[..., 1]
    
    parameters = {
        "binWidth": 25,
        "resampledPixelSpacing": None,
        "interpolator": "sitkBSpline",
        "enableCExtensions": True
    }
    extractor = featureextractor.RadiomicsFeatureExtractor(**parameters)
    extractor.enableFeaturesByName(
        shape=[
            "VoxelVolume", "SurfaceArea", "Sphericity",
            "Elongation", "MajorAxisLength",
        ],
        firstorder=[
            "Mean", "Median", "StandardDeviation",
            "Skewness", "Kurtosis", "Entropy", "Energy",
        ],
        glcm=[
            # "Contrast", "Correlation", "Homogeneity", "Energy",
            "Contrast", "Correlation", "Homogeneity",
        ],
        glrlm=[
            "ShortRunEmphasis", "LongRunEmphasis", "RunEntropy",
        ],
        glszm=[
            "SmallAreaEmphasis", "LargeAreaEmphasis", "ZoneEntropy",
        ],
    )
    image_sitk = sitk.GetImageFromArray(image_data.astype(np.float32))
    spacing = [float(x) for x in dual_channel_image.header.get_zooms()[:3]]
    image_sitk.SetSpacing(spacing)
    
    def _extract_features_for_label(label):
        binary_mask = (mask_data == label).astype(np.uint8)
        mask_sitk = sitk.GetImageFromArray(binary_mask)
        mask_sitk.SetSpacing(spacing)
        features = extractor.execute(image_sitk, mask_sitk)
        return features
    
    unique_labels = np.unique(mask_data)
    # Get mask file name from input
    try:
        input_sidecar_path = input_filepath.split(".")[0] + ".json"
        with open(input_sidecar_path, 'r') as f:
            sidecar_data = json.load(f)
            mask_filename = sidecar_data.get("metrics", {}).get("mask_filename", None)["value"]
    except:
        mask_filename = "aseg"
    
    df_lut: pd.DataFrame = load_freesurfer_color_lut()
    
    def _infer_roi_metadata(label: int):
        """
        Infer ROI namespace, type, and hemisphere from FreeSurfer label ID.
        """
        struct_name: str = df_lut.loc[df_lut['Index'] == label, 'StructName'].values[0]
        if len(struct_name) == 0:
            label_name: str = "unknown"
        else:
            label_name: str = struct_name
        
        hemisphere: str = "none"
        if "left" in label_name.lower():
            hemisphere = "L"
        elif "right" in label_name.lower():
            hemisphere = "R"
        
        roi_type: str = "unknown"
        if label in [2, 3, 4, 5, 7, 8, 10, 11, 12, 13, 17, 18, 26, 28, 60]:  # Cortical GM labels
            roi_type = "cortical_gm"
        elif label in [14, 15, 16, 24, 25, 41, 42, 43, 44, 46, 47, 49, 50, 51, 52, 53, 54]:  # Subcortical GM labels
            roi_type = "subcortical_gm"
        elif label in [4, 5, 14, 15, 24, 43, 44]:  # WM labels
            roi_type = "wm"
        elif label in [77, 78]:  # CSF labels
            roi_type = "csf"
        return {
            "roi_namespace": "freesurfer",
            "roi_type": roi_type,
            "roi_hemisphere": hemisphere
        }
    
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
    
    df_props: pd.DataFrame = output_data[["label_id", "mask_filename", "roi_namespace", "roi_type", "roi_hemisphere"]]
    prop_metrics: list[Metric] = []
    props: list[dict] = df_props.to_dict(orient="records")
    for prop in props:
        for non_label_key in ["mask_filename", "roi_namespace", "roi_type", "roi_hemisphere"]:
            metric: Metric = Metric(
                name=prop["label_id"],
                value=prop[non_label_key],
                description=f"{non_label_key} for label {prop['label_id']}",
                unit=None
            )
            prop_metrics.append(metric)
    prop_metrics = list(set(prop_metrics))  # Deduplicate
    prop_metrics.sort(key=lambda x: x.name)
    
    metrics = {
        "num_labels": len(unique_labels) - 1,  # Exclude background
        **{f"{metric.name}+{metric.description}": metric for metric in prop_metrics}
    }
    
    output_entities = {
        "desc": "radiomics",
        "modality": "T1w",
        "extension": ".tsv"
    }
    
    forced_outputs = [] # No forced outputs in this case
    
    return output_data, metrics, output_entities, forced_outputs
    