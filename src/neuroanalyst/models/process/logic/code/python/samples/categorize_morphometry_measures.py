import os

import pandas as pd
import numpy as np


def categorize_morphometry_measures(
    input_filepath: str,
) -> tuple[pd.DataFrame, dict, dict, list]:
    """
    Categorize morphometric measures from a wide FreeSurfer-style
    morphometry table into biologically interpretable semantic buckets.

    Expected input columns include:
      - StructName_base
      - LH_*, RH_*, Bilateral_* morphometry measures

    Args:
        input_filepath (str): Path to morphometry CSV file.
        
    Returns:
        output_data (pd.DataFrame): Categorized morphometry table (long format).
        metrics (dict): Summary statistics of categorization.
        output_entities (dict): BIDS-like entities for output file.
        forced_outputs (list): Non-BIDS outputs (none).
    """
    def str_to_bool(s):
        """Converts a string to a boolean value, handling various representations."""
        if s.lower() in ('true', '1', 'yes', 'on', 't', 'y'):
            return True
        elif s.lower() in ('false', '0', 'no', 'off', 'f', 'n', ''):
            return False
        elif s is None:
            raise ValueError(f"Please set the environment variable {s} to 'true' or 'false'.")
        else:
            # Raise an error or handle unexpected values as appropriate
            raise ValueError(f"Invalid boolean value for environment variable: {s}")
    
    DATA_DIR: str = "/data"
    NORMALIZE: bool = str_to_bool(os.getenv("NORMALIZE_MORPHOMETRY"))
    
    Z_LOW = -1.96 # 95% confidence interval lower bound
    Z_HIGH = 1.96 # 95% confidence interval upper bound

    # --------------------------------------------------
    # Step 1: Load input data and validate
    # --------------------------------------------------
    df_wide = pd.read_csv(input_filepath)

    if "StructName_base" not in df_wide.columns:
        raise ValueError(f"Missing required column: StructName_base. Found columns: {df_wide.columns.tolist()}")

    metric_cols = [c for c in df_wide.columns if c != "StructName_base"]
    if not metric_cols:
        raise ValueError(f"No morphometry metric columns found. Found columns: {df_wide.columns.tolist()}")

    # --------------------------------------------------
    # Step 2: Wide → long reshape
    # --------------------------------------------------
    df_long = (
        df_wide
        .melt(
            id_vars="StructName_base",
            value_vars=metric_cols,
            var_name="raw_metric",
            value_name="value",
        )
        .rename(columns={"StructName_base": "roi_name"})
    )
    if NORMALIZE:
        # Z-score normalization per metric
        df_long["value"] = (
            df_long
            .groupby("raw_metric")["value"]
            .transform(lambda x: (x - x.mean()) / x.std(ddof=0) if x.std(ddof=0) > 0 else 0)
        )

    # --------------------------------------------------
    # Step 3: Parse hemisphere + metric name
    # --------------------------------------------------
    def _parse_metric(col: str):
        if col.startswith("LH_"):
            return "LH", col[3:]
        if col.startswith("RH_"):
            return "RH", col[3:]
        if col.startswith("Bilateral_"):
            return "bilateral", col[10:]
        raise ValueError(f"Unrecognized metric column: {col}")

    parsed = df_long["raw_metric"].apply(_parse_metric)
    df_long["hemisphere"] = parsed.map(lambda x: x[0])
    df_long["metric"] = parsed.map(lambda x: x[1])

    df_long["roi_type"] = "cortical"  # explicit, future-proof

    # --------------------------------------------------
    # Step 4: Metric definitions
    # --------------------------------------------------
    METRIC_DEFINITIONS = {
        "GrayVolume_mm3": ("volume", "volume"),
        "SurfaceArea_mm2": ("surface_area", "surface_area"),
        "ThickAvg_mm": ("thickness", "thickness"),
        "MeanCurv": ("curvature", "curvature"),
        "GausCurv": ("curvature", "curvature"),
    }

    df_long["metric_family"] = df_long["metric"].map(
        lambda m: METRIC_DEFINITIONS.get(m, ("other", "morphometry"))[0]
    )

    df_long["metric_semantic"] = df_long["metric"].map(
        lambda m: METRIC_DEFINITIONS.get(m, ("other", "morphometry"))[1]
    )

    # --------------------------------------------------
    # Step 5: Deviation categorization (vectorized)
    # --------------------------------------------------
    z = df_long["value"]

    df_long["deviation"] = np.select(
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
    # Step 6: Semantic buckets
    # --------------------------------------------------
    df_long["bucket"] = np.where(
        df_long["deviation"] == "undefined",
        "undefined",
        df_long["deviation"] + "_" + df_long["metric_semantic"],
    )

    # --------------------------------------------------
    # Step 7: Summary metrics
    # --------------------------------------------------
    metrics = {
        "num_rois": int(df_long["roi_name"].nunique()),
        "num_metrics": int(df_long["metric"].nunique()),
        "num_metric_families": int(df_long["metric_family"].nunique()),
        "num_buckets": int(df_long["bucket"].nunique()),
        "num_undefined": int((df_long["deviation"] == "undefined").sum()),
        "num_hemispheres": int(df_long["hemisphere"].nunique()),
    }

    # --------------------------------------------------
    # Step 8: Output entities
    # --------------------------------------------------
    output_entities = {
        "desc": "morphometryCategorized",
        "space": "fsaverage",
        "extension": ".tsv",
    }

    forced_outputs: list = []

    return df_long, metrics, output_entities, forced_outputs
