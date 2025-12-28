import os
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

def normalize_morphometry_measures(input_filepath: str):
    """
    Normalize FreeSurfer-derived morphometric measures to enable
    cross-ROI and cross-subject comparison.

    Normalization strategy:
    - Z-score normalization within each metric family
    - Optional volume normalization by total intracranial volume (TIV)

    Args:
        input_filepath (str): Path to morphometry TSV file.

    Returns:
        output_data (pd.DataFrame): Normalized morphometry table.
        metrics (dict): Summary statistics of normalization.
        output_entities (dict): BIDS-like entities for output file.
        forced_outputs (list): Non-BIDS outputs (none).
    """

    # --------------------------------------------------
    # Step 1: Load data
    # --------------------------------------------------
    output_data = pd.read_csv(input_filepath, sep="\t")

    required_cols = {"roi_name", "metric", "value"}
    if not required_cols.issubset(output_data.columns):
        raise ValueError(f"Missing required columns: {required_cols - set(output_data.columns)}")

    output_data = output_data.copy()

    # --------------------------------------------------
    # Step 2: Detect TIV if present
    # --------------------------------------------------
    tiv = None
    tiv_mask = (
        (output_data["metric"].str.lower().isin(["estimatedtotalintracranialvol", "tiv"])) |
        (output_data["roi_name"].str.lower() == "estimatedtotalintracranialvol")
    )

    if tiv_mask.any():
        tiv = output_data.loc[tiv_mask, "value"].iloc[0]

    # --------------------------------------------------
    # Step 3: Normalize metrics
    # --------------------------------------------------
    normalized_values = []
    normalization_methods = []

    for metric_name, metric_df in output_data.groupby("metric"):
        values = metric_df["value"].astype(float)

        # Volume normalization if applicable
        if metric_name.lower().startswith("volume") and tiv is not None:
            norm_vals = values / tiv
            method = "tiv_normalized"

        else:
            mean = values.mean()
            std = values.std(ddof=0)

            if std == 0:
                norm_vals = np.zeros(len(values))
                method = "zscore_zero_variance"
            else:
                norm_vals = (values - mean) / std
                method = "zscore"

        normalized_values.extend(norm_vals)
        normalization_methods.extend([method] * len(norm_vals))

    output_data["normalized_value"] = normalized_values
    output_data["normalization_method"] = normalization_methods

    # --------------------------------------------------
    # Step 4: Metrics summary
    # --------------------------------------------------
    metrics = {
        "num_metrics": output_data["metric"].nunique(),
        "num_rois": output_data["roi_name"].nunique(),
        "normalization_methods": sorted(output_data["normalization_method"].unique().tolist()),
        "used_tiv": tiv is not None,
    }

    # --------------------------------------------------
    # Step 5: Output entities
    # --------------------------------------------------
    output_entities = {
        "desc": "morphometryNorm",
        "space": "fsaverage",
        "extension": ".tsv",
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs
