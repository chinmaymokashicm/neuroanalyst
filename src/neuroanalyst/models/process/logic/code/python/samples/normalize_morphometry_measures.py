from pathlib import Path
from typing import Tuple, Dict, List

import pandas as pd
import numpy as np


def normalize_morphometry_measures(input_filepath: str):
    """
    Normalize FreeSurfer-derived morphometric measures (wide format)
    to enable cross-ROI and cross-subject comparison.

    Input format:
        - One row per ROI
        - One column per metric (e.g., LH_ThickAvg_mm, Bilateral_GrayVolume_mm3)
        - Required column: StructName_base

    Normalization strategy:
        - Z-score normalization per metric column
        - Zero-variance metrics mapped to 0

    Args:
        input_filepath (str): Path to morphometry CSV file.

    Returns:
        output_data (pd.DataFrame): Normalized morphometry table (wide format).
        metrics (dict): Summary statistics of normalization.
        output_entities (dict): BIDS-like entities for output file.
        forced_outputs (list): Non-BIDS outputs (none).
    """

    # --------------------------------------------------
    # Step 1: Load data
    # --------------------------------------------------
    input_filepath = Path(input_filepath)
    output_data = pd.read_csv(input_filepath)

    if "StructName_base" not in output_data.columns:
        raise ValueError("Missing required column: 'StructName_base'")

    output_data = output_data.copy()

    # --------------------------------------------------
    # Step 2: Identify metric columns
    # --------------------------------------------------
    metric_cols = [
        c for c in output_data.columns
        if c != "StructName_base" and pd.api.types.is_numeric_dtype(output_data[c])
    ]

    if not metric_cols:
        raise ValueError("No numeric metric columns found for normalization")

    # --------------------------------------------------
    # Step 3: Normalize each metric column
    # --------------------------------------------------
    normalization_methods: Dict[str, str] = {}

    for col in metric_cols:
        values = output_data[col].astype(float)

        mean = values.mean()
        std = values.std(ddof=0)

        if std == 0 or np.isnan(std):
            output_data[col] = 0.0
            normalization_methods[col] = "zscore_zero_variance"
        else:
            output_data[col] = (values - mean) / std
            normalization_methods[col] = "zscore"

    # --------------------------------------------------
    # Step 4: Metrics summary
    # --------------------------------------------------
    metrics = {
        "num_rois": output_data["StructName_base"].nunique(),
        "num_metrics": len(metric_cols),
        "metric_columns": sorted(metric_cols),
        "normalization_methods": sorted(set(normalization_methods.values())),
        "per_metric_method": normalization_methods,
    }

    # --------------------------------------------------
    # Step 5: Output entities
    # --------------------------------------------------
    output_entities = {
        "desc": "morphometryNorm",
        "space": "fsaverage",
        "suffix": "morphometry",
        "extension": ".csv",
    }

    forced_outputs: List = []

    return output_data, metrics, output_entities, forced_outputs
