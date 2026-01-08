from neuroanalyst.models.process.logic.core import Metric

from pathlib import Path
import os
import json

import nibabel as nib
import numpy as np
import pandas as pd

def derive_composite_phenotypes(input_filepath: str):
    """
    Generate composite phenotypes from bucketed radiomics features.
    Ensures every ROI has at least one phenotype assignment.
    
    Args:
        input_filepath (str): Path to TSV produced by categorize_radiomics_features
    Returns:
        output_data (pd.DataFrame): DataFrame containing composite phenotypes.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """
    PHENOTYPE_RULES = [
        {
            "name": "large_irregular_structure",
            "requires": {"large_volume", "irregular_shape"},
            "family": "shape",
        },
        {
            "name": "diffuse_structure",
            "requires": {"large_extent", "high_surface_area"},
            "family": "shape",
        },
        {
            "name": "heterogeneous_high_entropy_roi",
            "requires": {"high_entropy", "heterogeneous_texture"},
            "family": "texture",
        },
        {
            "name": "fine_grained_complex_texture",
            "requires": {"fine_texture", "complex_texture"},
            "family": "texture",
        },
        {
            "name": "asymmetric_intensity_distribution",
            "requires": {"right_skewed_intensity", "high_intensity_variance"},
            "family": "intensity",
        },
        {
            "name": "high_signal_dominant_roi",
            "requires": {"high_signal_energy", "high_mean_intensity"},
            "family": "intensity",
        },
    ]

    
    bucketed_df = pd.read_csv(input_filepath, sep="\t")
    
    records = []

    grouped = bucketed_df.groupby(
        ["label_id", "roi_type", "roi_hemisphere", "mask_filename"]
    )

    for roi_keys, df_roi in grouped:
        buckets = set(df_roi["bucket"].values)
        matched_any = False

        for rule in PHENOTYPE_RULES:
            if rule["requires"].issubset(buckets):
                records.append({
                    "label_id": roi_keys[0],
                    "roi_type": roi_keys[1],
                    "roi_hemisphere": roi_keys[2],
                    "mask_filename": roi_keys[3],
                    "composite_phenotype": rule["name"],
                    "phenotype_family": rule["family"],
                    "evidence_buckets": sorted(rule["requires"]),
                })
                matched_any = True

        # Fallback
        if not matched_any:
            records.append({
                "label_id": roi_keys[0],
                "roi_type": roi_keys[1],
                "roi_hemisphere": roi_keys[2],
                "mask_filename": roi_keys[3],
                "composite_phenotype": "no_composite_phenotype",
                "phenotype_family": "none",
                "evidence_buckets": [],
            })

    output_data = pd.DataFrame.from_records(records)
    output_data["composite_phenotype"] = output_data["composite_phenotype"].astype("category")

    metrics = {
        "num_rois": output_data["label_id"].nunique(),
        "num_composite_phenotypes": output_data["composite_phenotype"].nunique(),
        "phenotype_families": sorted(output_data["phenotype_family"].unique().tolist()),
    }

    output_entities = {
        "desc": "radiomicsPhenotypes",
        "modality": "T1w",
        "extension": ".tsv"
    }
    
    forced_outputs = [] # No forced outputs in this case

    return output_data, metrics, output_entities, forced_outputs