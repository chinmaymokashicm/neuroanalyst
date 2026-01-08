from neuroanalyst.models.process.logic.core import Metric

from pathlib import Path
import os
import json

import nibabel as nib
import numpy as np
import pandas as pd

def categorize_radiomics_features(input_filepath: str):
    """
    Categorize radiomics features into semantically meaningful buckets
    aligned with radiomics literature (shape, intensity, texture). Lambin et al. 2017.

    Args:
        input_filepath (str): Path to TSV produced by extract_radiomics_features

    Returns:
        output_data (pd.DataFrame): DataFrame containing bucketed 
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """
    FEATURE_FAMILY_MAP = {
        # Shape
        "original_shape_VoxelVolume": "shape",
        "original_shape_SurfaceArea": "shape",
        "original_shape_Sphericity": "shape",
        "original_shape_Elongation": "shape",
        "original_shape_MajorAxisLength": "shape",

        # Intensity
        "original_firstorder_Mean": "intensity",
        "original_firstorder_Median": "intensity",
        "original_firstorder_StandardDeviation": "intensity",
        "original_firstorder_Skewness": "intensity",
        "original_firstorder_Kurtosis": "intensity",
        "original_firstorder_Entropy": "intensity",
        "original_firstorder_Energy": "intensity",

        # Texture
        "original_glcm_Contrast": "texture",
        "original_glcm_Correlation": "texture",
        "original_glcm_Homogeneity1": "texture",
        "original_glrlm_ShortRunEmphasis": "texture",
        "original_glrlm_LongRunEmphasis": "texture",
        "original_glrlm_RunEntropy": "texture",
        "original_glszm_SmallAreaEmphasis": "texture",
        "original_glszm_LargeAreaEmphasis": "texture",
        "original_glszm_ZoneEntropy": "texture",
    }

    def _bucket_feature(feature_name: str, value: float):
        """
        Bucket a single feature value based on predefined thresholds.
        
        Args:
            feature_name (str): Name of the radiomics feature.
            value (float): Value of the radiomics feature.
        Returns:
            bucket (str): Bucket category for the feature value.
        """
        if pd.isna(value):
            return "undefined"

        # ------------------
        # Shape features
        # ------------------
        if "VoxelVolume" in feature_name:
            if value < 1e3:
                return "small_volume"
            elif value < 1e4:
                return "medium_volume"
            else:
                return "large_volume"

        if "SurfaceArea" in feature_name:
            if value < 1e3:
                return "low_surface_area"
            elif value < 5e3:
                return "moderate_surface_area"
            else:
                return "high_surface_area"

        if "MajorAxisLength" in feature_name:
            if value < 20:
                return "short_extent"
            elif value < 60:
                return "moderate_extent"
            else:
                return "large_extent"

        if "Sphericity" in feature_name:
            return "compact_shape" if value > 0.6 else "irregular_shape"

        if "Elongation" in feature_name:
            return "elongated_shape" if value > 0.7 else "non_elongated_shape"

        # ------------------
        # First-order intensity
        # ------------------
        if "Mean" in feature_name:
            return "low_mean_intensity" if value < 500 else "high_mean_intensity"

        if "Median" in feature_name:
            return "low_median_intensity" if value < 500 else "high_median_intensity"

        if "StandardDeviation" in feature_name:
            return "low_intensity_variance" if value < 20 else "high_intensity_variance"

        if "Skewness" in feature_name:
            if value < -0.5:
                return "left_skewed_intensity"
            elif value > 0.5:
                return "right_skewed_intensity"
            else:
                return "symmetric_intensity"

        if "Kurtosis" in feature_name:
            return "peaked_intensity" if value > 3 else "flat_intensity"

        if "Entropy" in feature_name:
            if value < 3:
                return "low_entropy"
            elif value < 6:
                return "medium_entropy"
            else:
                return "high_entropy"

        if "Energy" in feature_name:
            return "low_signal_energy" if value < 1e6 else "high_signal_energy"

        # ------------------
        # Texture (GLCM)
        # ------------------
        if "Contrast" in feature_name:
            return "high_contrast_texture" if value > 10 else "low_contrast_texture"

        if "Correlation" in feature_name:
            return "high_texture_correlation" if value > 0.8 else "low_texture_correlation"

        if "Homogeneity" in feature_name:
            return "homogeneous_texture" if value > 0.5 else "heterogeneous_texture"

        # ------------------
        # Texture (GLRLM)
        # ------------------
        if "ShortRunEmphasis" in feature_name:
            return "fine_texture" if value > 0.5 else "coarse_texture"

        if "LongRunEmphasis" in feature_name:
            return "coarse_texture" if value > 0.5 else "fine_texture"

        if "RunEntropy" in feature_name:
            return "complex_texture" if value > 4 else "simple_texture"

        # ------------------
        # Texture (GLSZM)
        # ------------------
        if "SmallAreaEmphasis" in feature_name:
            return "fragmented_texture" if value > 0.5 else "non_fragmented_texture"

        if "LargeAreaEmphasis" in feature_name:
            return "large_zone_texture" if value > 0.5 else "small_zone_texture"

        if "ZoneEntropy" in feature_name:
            return "complex_zone_structure" if value > 4 else "simple_zone_structure"

        return "uncategorized"


    df_features = pd.read_csv(input_filepath, sep="\t")
    records = []
    
    required_columns = ["label_id", "roi_type", "roi_hemisphere", "mask_filename"]
    missing_columns = required_columns - set(df_features.columns)
    if missing_columns:
        raise ValueError(f"Input data is missing required columns: {missing_columns}")
    
    for _, row in df_features.iterrows():
        for feature_name, family in FEATURE_FAMILY_MAP.items():
            if feature_name not in row or pd.isna(row[feature_name]):
                continue

            records.append({
                "label_id": row["label_id"],
                "roi_type": row["roi_type"],
                "roi_hemisphere": row["roi_hemisphere"],
                "mask_filename": row["mask_filename"],
                "feature_family": family,
                "feature_name": feature_name,
                "bucket": _bucket_feature(feature_name, row[feature_name]),
                "value": row[feature_name],
            })

    output_data = pd.DataFrame.from_records(records)

    metrics = {
        "num_rois": output_data["label_id"].nunique(),
        "num_features": output_data["feature_name"].nunique(),
        "num_feature_families": output_data["feature_family"].nunique(),
        "num_buckets": output_data["bucket"].nunique(),
    }
    
    output_entities = {
        "desc": "radiomicsBucketed",
        "suffix": "T1w",
        "extension": ".tsv"
    }

    return output_data, metrics, output_entities, []
