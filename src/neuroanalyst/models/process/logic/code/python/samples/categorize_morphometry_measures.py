import pandas as pd
import numpy as np
from typing import Tuple, Dict, List


def categorize_morphometry_measures(
    input_filepath: str
) -> Tuple[pd.DataFrame, Dict, Dict, List]:
    """
    Categorize normalized morphometric measures into biologically
    interpretable semantic buckets.

    Args:
        input_filepath (str): Path to normalized morphometry TSV.

    Returns:
        output_data (pd.DataFrame): Categorized morphometry table.
        metrics (dict): Summary statistics.
        output_entities (dict): BIDS-like entities.
        forced_outputs (list): Non-BIDS outputs (none).
    """

    # --------------------------------------------------
    # Step 1: Load + validate
    # --------------------------------------------------
    df = pd.read_csv(input_filepath, sep="\t")
    Z_LOW: float = -1.96
    Z_HIGH: float = 1.96

    required_cols = {
        "roi_name",
        "roi_type",
        "hemisphere",
        "metric",
        "normalized_value",
    }

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()

    # --------------------------------------------------
    # Step 2: Metric → family + semantic label
    # --------------------------------------------------
    METRIC_DEFINITIONS = {
        # Volumetric
        "volume": {
            "family": "volume",
            "semantic": "volume",
        },

        # Thickness
        "ThickAvg_mm": {
            "family": "thickness",
            "semantic": "thickness",
        },
        "ThickStd_mm": {
            "family": "thickness_variability",
            "semantic": "thickness_variability",
        },

        # Surface
        "SurfaceArea_mm2": {
            "family": "surface_area",
            "semantic": "surface_area",
        },

        # Curvature / folding
        "MeanCurv": {
            "family": "curvature",
            "semantic": "curvature",
        },
        "GausCurv": {
            "family": "curvature",
            "semantic": "curvature",
        },
        "FoldInd": {
            "family": "gyrification",
            "semantic": "gyrification",
        },
        "CurvInd": {
            "family": "gyrification",
            "semantic": "gyrification",
        },
    }

    df["metric_family"] = df["metric"].map(
        lambda m: METRIC_DEFINITIONS.get(m, {}).get("family", "other")
    )

    df["metric_semantic"] = df["metric"].map(
        lambda m: METRIC_DEFINITIONS.get(m, {}).get("semantic", "morphometry")
    )

    # --------------------------------------------------
    # Step 3: Deviation level (vectorized)
    # --------------------------------------------------
    z = df["normalized_value"]

    df["deviation"] = np.select(
        [
            z.isna(),
            z <= Z_LOW,
            z >= Z_HIGH,
        ],
        [
            "undefined",
            "low",
            "high",
        ],
        default="normal",
    )

    # --------------------------------------------------
    # Step 4: Final semantic bucket
    # --------------------------------------------------
    df["bucket"] = np.where(
        df["deviation"] == "undefined",
        "undefined",
        df["deviation"] + "_" + df["metric_semantic"],
    )

    # --------------------------------------------------
    # Step 5: Summary metrics
    # --------------------------------------------------
    metrics = {
        "num_rois": int(df["roi_name"].nunique()),
        "num_metrics": int(df["metric"].nunique()),
        "num_metric_families": int(df["metric_family"].nunique()),
        "num_buckets": int(df["bucket"].nunique()),
        "num_undefined": int((df["deviation"] == "undefined").sum()),
    }

    # --------------------------------------------------
    # Step 6: Output entities
    # --------------------------------------------------
    output_entities = {
        "desc": "morphometryCategorized",
        "space": "fsaverage",
        "extension": ".tsv",
    }

    forced_outputs: List = []

    return df, metrics, output_entities, forced_outputs
