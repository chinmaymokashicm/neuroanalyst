from pathlib import Path
import pandas as pd
import numpy as np


def dti_semantic_phenotypes(input_filepath: str):
    """
    Convert z-scored regional DTI measures into semantic phenotypes.

    Args:
        input_filepath (str): TSV produced by phenotype_dti_measures
                              containing z-scored DTI metrics.

    Returns:
        output_data (pd.DataFrame): Long-form phenotyped DTI measures
        metrics (dict): Summary metadata
        output_entities (dict): BIDS-like entities
        forced_outputs (list): Non-BIDS outputs (none)
    """

    # ============================
    # Step 1: Load Input
    # ============================
    df = pd.read_csv(input_filepath, sep="\t")

    REQUIRED_COLUMNS = {
        "roi_name",
        "roi_type",
        "metric",
        "value",
        "z_value",
    }

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # ============================
    # Step 2: Metric Semantics
    # ============================
    DTI_SEMANTICS = {
        "FA": {
            "metric_family": "microstructure",
            "metric_semantic": "fractional_anisotropy",
            "directionality": "higher_is_better",
        },
        "MD": {
            "metric_family": "microstructure",
            "metric_semantic": "mean_diffusivity",
            "directionality": "lower_is_better",
        },
        "RD": {
            "metric_family": "microstructure",
            "metric_semantic": "radial_diffusivity",
            "directionality": "lower_is_better",
        },
        "AD": {
            "metric_family": "microstructure",
            "metric_semantic": "axial_diffusivity",
            "directionality": "context_dependent",
        },
    }

    # ============================
    # Step 3: Phenotyping Logic
    # ============================
    records = []

    for _, row in df.iterrows():
        metric = row["metric"]
        z = row["z_value"]

        if metric not in DTI_SEMANTICS or pd.isna(z):
            continue

        semantic = DTI_SEMANTICS[metric]

        # ----------------------------
        # Z-score interpretation
        # ----------------------------
        if z <= -2:
            deviation = "low"
        elif z >= 2:
            deviation = "high"
        else:
            deviation = "normal"

        # ----------------------------
        # Direction-aware phenotype
        # ----------------------------
        if deviation == "normal":
            phenotype = "within_expected_range"
        else:
            if semantic["directionality"] == "higher_is_better":
                phenotype = (
                    "pathologically_low"
                    if deviation == "low"
                    else "supranormal"
                )
            elif semantic["directionality"] == "lower_is_better":
                phenotype = (
                    "pathologically_high"
                    if deviation == "high"
                    else "supranormal"
                )
            else:
                phenotype = f"{deviation}_abnormal"

        bucket = f"{deviation}_{metric.lower()}"

        records.append({
            "roi_name": row["roi_name"],
            "roi_type": row["roi_type"],
            "metric": metric,
            "value": row["value"],
            "z_value": z,
            "metric_family": semantic["metric_family"],
            "metric_semantic": semantic["metric_semantic"],
            "directionality": semantic["directionality"],
            "deviation": deviation,
            "phenotype": phenotype,
            "bucket": bucket,
            "bucket_type": "statistical_normative",
        })

    # ============================
    # Step 4: Outputs
    # ============================
    output_data = pd.DataFrame.from_records(records)

    metrics = {
        "n_phenotypes": len(output_data),
        "metrics": sorted(output_data["metric"].unique()),
        "phenotype_types": sorted(output_data["phenotype"].unique()),
        "bucket_type": "statistical_normative",
    }

    output_entities = {
        "suffix": "dti",
        "desc": "phenotyped",
        "extension": ".tsv",
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs
