from src.neuroanalyst.models.process.logic.core import Metric

import pandas as pd
import numpy as np
from pathlib import Path


def distill_dti_semantic_phenotypes(
    input_filepath: str,
    max_phenotypes: int = 5,
    z_threshold: float = 2.0,
):
    """
    Distill ROI-level DTI semantic phenotypes into a limited set of
    file-level phenotypes for KG attachment.

    Args:
        input_filepath (str): TSV from dti_semantic_phenotypes
        max_phenotypes (int): Max number of phenotypes to emit
        z_threshold (float): Absolute z-score threshold

    Returns:
        output_data (pd.DataFrame): Reduced phenotype table
        metrics (dict): File-level semantic phenotypes
        output_entities (dict): BIDS-like entities
        forced_outputs (list): None
    """

    # ============================
    # Step 1: Load Input
    # ============================
    df = pd.read_csv(input_filepath, sep="\t")

    REQUIRED_COLUMNS = {
        "roi_name",
        "metric",
        "z_value",
        "phenotype",
        "bucket",
        "deviation",
    }

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # ============================
    # Step 2: Keep only salient abnormalities
    # ============================
    df_abnormal = df[
        df["z_value"].abs() >= z_threshold
    ].copy()

    if df_abnormal.empty:
        metrics = {
            "semantic_phenotypes": [Metric(name="dti_semantic_phenotype", value="no_significant_dti_abnormality", unit=None, description="DTI semantic phenotype")],
            "phenotype_count": Metric(name="dti_semantic_phenotype_count", value=0, unit="count", description="Number of distinct DTI semantic phenotypes"),
        }

        output_entities = {
            "suffix": "stats",
            "desc": "dtiPhenotypeSummary",
            "extension": ".tsv",
        }

        return (
            pd.DataFrame(),
            metrics,
            output_entities,
            [],
        )

    # ============================
    # Step 3: Aggregate phenotypes
    # ============================
    grouped = (
        df_abnormal
        .groupby(["metric", "deviation"])
        .agg(
            n_rois=("roi_name", "nunique"),
            mean_abs_z=("z_value", lambda x: np.mean(np.abs(x))),
            max_abs_z=("z_value", lambda x: np.max(np.abs(x))),
        )
        .reset_index()
    )

    # Rank by severity and extent
    grouped = grouped.sort_values(
        by=["mean_abs_z", "n_rois"],
        ascending=False,
    )

    # ============================
    # Step 4: Construct semantic labels
    # ============================
    phenotype_records = []
    semantic_labels = []

    for _, row in grouped.head(max_phenotypes).iterrows():
        metric = row["metric"].lower()
        deviation = row["deviation"]
        n_rois = int(row["n_rois"])

        if n_rois >= 10:
            extent = "widespread"
        elif n_rois >= 3:
            extent = "multifocal"
        else:
            extent = "focal"

        label = f"{extent}_{deviation}_{metric}"

        semantic_labels.append(label)

        phenotype_records.append({
            "phenotype": label,
            "metric": metric.upper(),
            "deviation": deviation,
            "extent": extent,
            "n_rois": n_rois,
            "mean_abs_z": row["mean_abs_z"],
            "max_abs_z": row["max_abs_z"],
        })

    output_data = pd.DataFrame.from_records(phenotype_records)

    # ============================
    # Step 5: Metrics for KG
    # ============================
    metrics = {
        "semantic_phenotypes": [Metric(name="dti_semantic_phenotype", value=label, unit=None, description="DTI semantic phenotype") for label in semantic_labels],
        "phenotype_count": Metric(name="dti_semantic_phenotype_count", value=len(semantic_labels), unit="count", description="Number of distinct DTI semantic phenotypes"),
        "z_threshold": Metric(name="dti_semantic_phenotype_z_threshold", value=z_threshold, unit="z-score", description="Z-score threshold for defining significant DTI abnormalities"),
        "max_phenotypes": Metric(name="dti_semantic_phenotype_max_phenotypes", value=max_phenotypes, unit="count", description="Maximum number of DTI semantic phenotypes to retain"),
    }

    output_entities = {
        "suffix": "stats",
        "desc": "dtiPhenotypeSummary",
        "extension": ".tsv",
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs
