from neuroanalyst.models.process.logic.core import Metric
from bids.layout import parse_file_entities

import pandas as pd
import numpy as np
import os


def distill_derived_morphometric_phenotypes(
    input_filepath: str,
) -> tuple[pd.DataFrame, dict, dict, list]:
    """
    Derive subject-level (Tier 3) morphometric phenotypes by aggregating
    ROI-level composite phenotypes.

    This step intentionally produces a *small*, semantically rich set of
    phenotypes suitable for Knowledge Graph ingestion.

    Args:
        input_filepath (str): TSV produced by derive_morphometric_phenotypes

    Returns:
        output_data (pd.DataFrame): Subject-level phenotype table
        metrics (dict): KG-ready Metric objects
        output_entities (dict): BIDS-like entities
        forced_outputs (list): Empty
    """

    # --------------------------------------------------
    # Step 1: Load ROI-level phenotypes
    # --------------------------------------------------
    df = pd.read_csv(input_filepath, sep="\t")

    required_cols = {
        "roi_name",
        "roi_type",
        "hemisphere",
        "composite_phenotype",
    }
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"Missing required columns: {required_cols - set(df.columns)}"
        )

    entities = parse_file_entities(input_filepath)
    subject = entities.get("subject")
    session = entities.get("session")

    # --------------------------------------------------
    # Step 2: Basic counts
    # --------------------------------------------------
    n_rois = (
        df[["roi_name", "hemisphere"]]
        .drop_duplicates()
        .shape[0]
    )

    phenotype_counts = (
        df["composite_phenotype"]
        .value_counts()
        .to_dict()
    )

    def fraction(name: str) -> float:
        return phenotype_counts.get(name, 0) / max(n_rois, 1)

    MIN_ROI_FRACTION = 0.15  # heuristic, demo-friendly

    # --------------------------------------------------
    # Step 3: Compute global phenotypes
    # --------------------------------------------------
    records = []

    def add_record(name, value, description):
        records.append({
            "subject": subject,
            "session": session,
            "phenotype": name,
            "value": value,
            "description": description,
        })

    cortical_atrophy_fraction = fraction("cortical_atrophy")

    add_record(
        "global_cortical_atrophy_fraction",
        cortical_atrophy_fraction,
        "Fraction of cortical ROIs showing atrophy-related morphometric patterns.",
    )

    add_record(
        "global_cortical_atrophy_present",
        cortical_atrophy_fraction >= MIN_ROI_FRACTION,
        f"True if ≥{int(MIN_ROI_FRACTION*100)}% of cortical ROIs show atrophy.",
    )

    folding_fraction = (
        fraction("hypogyrification")
        + fraction("hypergyrification")
    )

    add_record(
        "global_folding_abnormality_fraction",
        folding_fraction,
        "Fraction of ROIs with abnormal cortical folding.",
    )

    subcortical_loss_fraction = fraction("subcortical_atrophy")

    add_record(
        "subcortical_volume_loss_fraction",
        subcortical_loss_fraction,
        "Fraction of subcortical ROIs with volume loss.",
    )

    abnormal_fraction = (
        df[df["composite_phenotype"] != "morphometrically_typical"]
        .shape[0] / max(len(df), 1)
    )

    add_record(
        "overall_morphometric_abnormality_fraction",
        abnormal_fraction,
        "Fraction of ROI-hemisphere units with any abnormal morphometry.",
    )

    # --------------------------------------------------
    # Step 4: Laterality phenotype
    # --------------------------------------------------
    hemi_counts = (
        df[df["composite_phenotype"] == "cortical_atrophy"]
        .groupby("hemisphere")
        .size()
        .to_dict()
    )

    lh = hemi_counts.get("lh", 0)
    rh = hemi_counts.get("rh", 0)

    laterality_index = (lh - rh) / (lh + rh) if (lh + rh) > 0 else 0.0

    add_record(
        "atrophy_laterality_index",
        laterality_index,
        "Laterality index of cortical atrophy (positive = left-dominant).",
    )

    output_data = pd.DataFrame.from_records(records)

    # --------------------------------------------------
    # Step 5: KG Metrics (small on purpose)
    # --------------------------------------------------
    metrics = {
        "num_rois": Metric(
            name="num_rois",
            value=n_rois,
            unit=None,
            category="summary",
            description="Number of ROI-hemisphere units evaluated.",
            labels=["count"],
        ),
        "global_cortical_atrophy_fraction": Metric(
            name="global_cortical_atrophy_fraction",
            value=cortical_atrophy_fraction,
            unit="fraction",
            category="global_morphometry",
            labels=["atrophy", "cortical"],
        ),
        "global_cortical_atrophy_present": Metric(
            name="global_cortical_atrophy_present",
            value=cortical_atrophy_fraction >= MIN_ROI_FRACTION,
            unit=None,
            category="global_morphometry",
            labels=["atrophy", "binary"],
        ),
        "atrophy_laterality_index": Metric(
            name="atrophy_laterality_index",
            value=laterality_index,
            unit=None,
            category="laterality",
            labels=["atrophy", "hemispheric"],
        ),
        "overall_morphometric_abnormality_fraction": Metric(
            name="overall_morphometric_abnormality_fraction",
            value=abnormal_fraction,
            unit="fraction",
            category="global_morphometry",
            labels=["burden"],
        ),
    }

    # --------------------------------------------------
    # Step 6: Output entities
    # --------------------------------------------------
    output_entities = {
        "desc": "distilledMorphometricPhenotypes",
        "suffix": "stats",
        "extension": ".tsv",
    }

    forced_outputs: list = []

    return output_data, metrics, output_entities, forced_outputs
