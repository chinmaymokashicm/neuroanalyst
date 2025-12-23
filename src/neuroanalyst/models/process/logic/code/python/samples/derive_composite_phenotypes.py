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
    bucketed_df = pd.read_csv(input_filepath, sep="\t")
    
    records = []

    grouped = bucketed_df.groupby(
        ["label_id", "roi_type", "roi_hemisphere", "mask_filename"]
    )

    for roi_keys, df_roi in grouped:
        buckets = set(df_roi["bucket"].values)
        matched = False

        def has(*args):
            return all(a in buckets for a in args)

        # Shape composites
        if has("large_volume", "irregular_shape"):
            records.append((*roi_keys, "large_irregular_structure"))
            matched = True

        if has("large_extent", "high_surface_area"):
            records.append((*roi_keys, "diffuse_structure"))
            matched = True

        # Texture composites
        if has("high_entropy", "heterogeneous_texture"):
            records.append((*roi_keys, "heterogeneous_high_entropy_roi"))
            matched = True

        if has("fine_texture", "complex_texture"):
            records.append((*roi_keys, "fine_grained_complex_texture"))
            matched = True

        # Intensity composites
        if has("right_skewed_intensity", "high_intensity_variance"):
            records.append((*roi_keys, "asymmetric_intensity_distribution"))
            matched = True

        if has("high_signal_energy", "high_mean_intensity"):
            records.append((*roi_keys, "high_signal_dominant_roi"))
            matched = True

        # Fallback phenotype
        if not matched:
            records.append((*roi_keys, "no_composite_phenotype"))

    output_data = pd.DataFrame(
        records,
        columns=[
            "label_id",
            "roi_type",
            "roi_hemisphere",
            "mask_filename",
            "composite_phenotype",
        ],
    )
    output_data["composite_phenotype"] = output_data["composite_phenotype"].astype("category")
    
    df_label_phenotypes: pd.DataFrame = output_data[["label_id", "composite_phenotype"]]
    prop_metrics: list[Metric] = []
    props: list[dict] = df_label_phenotypes.to_dict(orient="records")
    for prop in props:
        metric: Metric = Metric(
            name=prop["label_id"],
            value=prop["composite_phenotype"],
            description=f"composite_phenotype for label {prop['label_id']}",
            unit=None
        )
        prop_metrics.append(metric)
    prop_metrics = list(set(prop_metrics))  # Deduplicate
    prop_metrics.sort(key=lambda x: x.name)
    
    metrics = {
        "num_rois": output_data["label_id"].nunique(),
        "num_composite_phenotypes": output_data["composite_phenotype"].nunique(),
        **{f"{metric.name}+{metric.description}": metric for metric in prop_metrics}
    }
    
    output_entities = {
        "desc": "radiomicsPhenotypes",
        "modality": "T1w",
        "extension": ".tsv"
    }
    
    forced_outputs = [] # No forced outputs in this case

    return output_data, metrics, output_entities, forced_outputs