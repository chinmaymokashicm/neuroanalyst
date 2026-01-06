from neuroanalyst.analysis.freesurfer import get_reconall_normative_morphometry
from neuroanalyst.models.process.logic.core import Metric

import pandas as pd
import numpy as np

from bids.layout import parse_file_entities


def derive_morphometric_phenotypes(
    input_filepath: str,
) -> tuple[pd.DataFrame, dict, dict, list]:
    """
    Derive composite morphometric phenotypes using a normative
    reference table.
    Objectives:
        - Identify deviations in morphometric measures relative to norms
        - Aggregate metric-level abnormalities into ROI-level phenotypes
    
    The morphometric measures table contains columns:
        - roi_name
        - raw_metric
        - value
        - z_value
        - hemisphere
        - metric
        - roi_type
        - metric_family
        - metric_semantic
        - deviation
        - bucket
        - bucket_type
    
    The reference table should contain columns:
        - roi_name
        - roi_type
        - metric
        - hemisphere
        - reference_population
        - age_min
        - age_max
        - sex
        - expected_mean
        - expected_sd
        - covariates
        - units
        - version

    Args:
        input_filepath (str): TSV from categorize_morphometry_measures

    Returns:
        output_data (pd.DataFrame): ROI-level phenotypes
        metrics (dict): Summary statistics
        output_entities (dict): BIDS-like entities
        forced_outputs (List): None
    """

    # --------------------------------------------------
    # Step 1: Load data
    # --------------------------------------------------
    DATA_DIR: str = "/data"
    df_categorized: pd.DataFrame = pd.read_csv(input_filepath, sep="\t")
    df_reference: pd.DataFrame = get_reconall_normative_morphometry()
    REFERENCE_POPULATION: str = "HCP"
    Z_THRESHOLD: float = 2.0

    required_cols = {
        "roi_name", "hemisphere", "metric", "value", "roi_type"
    }
    if not required_cols.issubset(df_categorized.columns):
        raise ValueError(f"Missing required columns: {required_cols - set(df_categorized.columns)}")
    
    # Get demographic data from participants.tsv
    try:
        df_participants: pd.DataFrame = pd.read_csv(f"{DATA_DIR}/participants.tsv", sep="\t")
        subject: str = parse_file_entities(input_filepath).get("subject")
        age_col: str = [col for col in df_participants.columns if col.startswith("age")][0]
        age: int = int(df_participants.loc[df_participants["participant_id"] == f"sub-{subject}", age_col].values[0])
        sex_col: str = [col for col in df_participants.columns if col.startswith("sex")][0]
        sex: str = df_participants.loc[df_participants["participant_id"] == f"sub-{subject}", sex_col].values[0]
    except Exception as e:
        raise ValueError(f"Error retrieving demographic data from participants.tsv: {e}")

    # --------------------------------------------------
    # Step 2: Filter reference table
    # --------------------------------------------------
    df_reference = df_reference[
        (df_reference["reference_population"] == REFERENCE_POPULATION)
        & (df_reference["sex"] == sex)
        & (df_reference["age_min"] <= age)
        & (df_reference["age_max"] >= age)
    ]

    # --------------------------------------------------
    # Step 3: Join observed data with reference norms
    # --------------------------------------------------
    merged = df_categorized.merge(
        df_reference,
        on=["roi_name", "metric", "hemisphere"],
        how="left",
        suffixes=("", "_ref"),
    )

    if merged["expected_mean"].isna().any():
        # For demo: warn, don’t crash
        merged = merged.dropna(subset=["expected_mean", "expected_sd"])

    # --------------------------------------------------
    # Step 4: Compute reference z-score
    # --------------------------------------------------
    merged["z_ref"] = (
        (merged["value"] - merged["expected_mean"]) / merged["expected_sd"]
    )

    # --------------------------------------------------
    # Step 5: Metric-level phenotypes
    # --------------------------------------------------
    def _metric_phenotype(row):
        z = row["z_ref"]
        metric = row["metric"]

        if metric == "thickness":
            if z <= -Z_THRESHOLD:
                return "low_thickness"
            if z >= Z_THRESHOLD:
                return "high_thickness"

        if metric == "surface_area":
            if z <= -Z_THRESHOLD:
                return "low_surface_area"
            if z >= Z_THRESHOLD:
                return "high_surface_area"

        if metric in {"mean_curvature", "gaussian_curvature"}:
            if abs(z) >= Z_THRESHOLD:
                return "curvature_abnormality"

        if metric == "volume":
            if z <= -Z_THRESHOLD:
                return "low_volume"
            if z >= Z_THRESHOLD:
                return "high_volume"

        return None

    merged["metric_phenotype"] = merged.apply(_metric_phenotype, axis=1)

    # --------------------------------------------------
    # Step 6: Aggregate to ROI-level phenotypes
    # --------------------------------------------------
    PHENOTYPE_RULES = {
        "cortical_atrophy": {
            "roi_type": "cortical",
            "required": {
                "any": ["low_thickness", "low_surface_area"],
            },
            "evidence_level": "structural_loss",
        },
        "cortical_hypertrophy": {
            "roi_type": "cortical",
            "required": {
                "all": ["high_thickness", "high_surface_area"],
            },
            "evidence_level": "structural_expansion",
        },
        "altered_cortical_folding": {
            "roi_type": "cortical",
            "required": {
                "any": ["curvature_abnormality"],
            },
            "evidence_level": "geometry",
        },
        "subcortical_atrophy": {
            "roi_type": "subcortical",
            "required": {
                "any": ["low_volume"],
            },
            "evidence_level": "volume_loss",
        },
        "subcortical_hypertrophy": {
            "roi_type": "subcortical",
            "required": {
                "any": ["high_volume"],
            },
            "evidence_level": "volume_expansion",
        },
    }
    
    def matches_rule(phenos: set[str], rule: dict) -> bool:
        req = rule["required"]

        if "all" in req:
            return set(req["all"]).issubset(phenos)

        if "any" in req:
            return bool(set(req["any"]) & phenos)

        return False
    
    records = []

    grouped = merged.groupby(["roi_name", "roi_type", "hemisphere"])

    for (roi, roi_type, hemi), g in grouped:
        phenos = set(g["metric_phenotype"].dropna())

        matched = []

        for phenotype, rule in PHENOTYPE_RULES.items():
            if rule["roi_type"] != roi_type:
                continue

            if matches_rule(phenos, rule):
                matched.append({
                    "roi_name": roi,
                    "roi_type": roi_type,
                    "hemisphere": hemi,
                    "composite_phenotype": phenotype,
                    "evidence_level": rule["evidence_level"],
                    "evidence_metrics": sorted(phenos),
                    "reference_population": REFERENCE_POPULATION,
                    "z_threshold": Z_THRESHOLD,
                })

        if not matched:
            matched.append({
                "roi_name": roi,
                "roi_type": roi_type,
                "hemisphere": hemi,
                "composite_phenotype": "morphometrically_typical",
                "evidence_level": "none",
                "evidence_metrics": [],
                "reference_population": REFERENCE_POPULATION,
                "z_threshold": Z_THRESHOLD,
            })

        records.extend(matched)

    output_data = pd.DataFrame.from_records(records)

    # --------------------------------------------------
    # Step 7: Metrics
    # --------------------------------------------------
    metrics = {
        "num_rois": output_data[["roi_name", "hemisphere"]].drop_duplicates().shape[0],
        "num_phenotypes": output_data["composite_phenotype"].nunique(),
        "num_records": len(output_data),
        "age": Metric(
            name="age",
            value=age,
            unit="years",
            description="Subject age used for normative comparison",
            category="demographic",
            labels=["age"],
        ),
        "sex": Metric(
            name="sex",
            value=sex,
            unit=None,
            description="Subject sex used for normative comparison",
            category="demographic",
            labels=["sex"],
        ),
    }

    # --------------------------------------------------
    # Step 8: Output entities
    # --------------------------------------------------
    output_entities = {
        "desc": "morphometryPhenotypes",
        "suffix": "stats",
        "extension": ".tsv",
    }

    forced_outputs: list = []

    return output_data, metrics, output_entities, forced_outputs
