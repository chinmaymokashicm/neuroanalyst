import pandas as pd
import numpy as np


def categorize_morphometry_measures(input_filepath: str):
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
    # Step 1: Load data
    # --------------------------------------------------
    df = pd.read_csv(input_filepath, sep="\t")

    required_cols = {
        "roi_name", "roi_type", "hemisphere",
        "metric", "normalized_value"
    }
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_cols - set(df.columns)}")

    df = df.copy()

    # --------------------------------------------------
    # Step 2: Define metric families
    # --------------------------------------------------
    METRIC_FAMILY_MAP = {
        # Volumetric
        "volume": "volume",

        # Cortical thickness
        "ThickAvg_mm": "thickness",
        "ThickStd_mm": "thickness_variability",

        # Surface / geometry
        "SurfaceArea_mm2": "surface_area",

        # Curvature
        "MeanCurv": "curvature",
        "GausCurv": "curvature",
        "FoldInd": "gyrification",
        "CurvInd": "gyrification",
    }

    # --------------------------------------------------
    # Step 3: Bucketing logic
    # --------------------------------------------------
    def _bucket_value(metric: str, z: float) -> str:
        if pd.isna(z):
            return "undefined"

        # Generic deviation buckets
        if z <= -1.0:
            level = "low"
        elif z >= 1.0:
            level = "high"
        else:
            level = "normal"

        # Metric-specific semantics
        if "Thick" in metric:
            return f"{level}_thickness"
        if "SurfaceArea" in metric:
            return f"{level}_surface_area"
        if "Curv" in metric:
            return f"{level}_curvature"
        if "Fold" in metric or "Gyr" in metric:
            return f"{level}_gyrification"
        if metric.lower().startswith("volume"):
            return f"{level}_volume"

        return f"{level}_morphometry"

    # --------------------------------------------------
    # Step 4: Apply categorization
    # --------------------------------------------------
    df["metric_family"] = df["metric"].map(
        lambda m: METRIC_FAMILY_MAP.get(m, "other")
    )

    df["bucket"] = df.apply(
        lambda r: _bucket_value(r["metric"], r["normalized_value"]),
        axis=1
    )

    # --------------------------------------------------
    # Step 5: Metrics summary
    # --------------------------------------------------
    metrics = {
        "num_rois": df["roi_name"].nunique(),
        "num_metrics": df["metric"].nunique(),
        "num_metric_families": df["metric_family"].nunique(),
        "num_buckets": df["bucket"].nunique(),
    }

    # --------------------------------------------------
    # Step 6: Output entities
    # --------------------------------------------------
    output_entities = {
        "desc": "morphometryCategorized",
        "space": "fsaverage",
        "extension": ".tsv",
    }

    forced_outputs = []

    return df, metrics, output_entities, forced_outputs
