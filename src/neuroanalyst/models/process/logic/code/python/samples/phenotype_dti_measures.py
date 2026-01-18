from neuroanalyst.models.process.logic.core import Metric

import os
from pathlib import Path

import pandas as pd
import numpy as np
from bids.layout import parse_file_entities


def phenotype_dti_measures(input_filepath: str):
    """
    Phenotype regional DTI measures by comparing subject-level values
    to a normative reference dataset and computing z-scores.

    This function performs *normative comparison*, not bucketing.

    Args:
        input_filepath (str): TSV with regional DTI summaries (wide format).

    Returns:
        output_data (pd.DataFrame): Long-form phenotyped DTI table.
        metrics (dict): Metadata about phenotyping.
        output_entities (dict): BIDS-like entities.
        forced_outputs (list): Non-BIDS outputs (none).
    """

    # ============================
    # Step 1: Load inputs
    # ============================
    DATA_DIR: str = "/data"
    REFERENCE_CSV_NAME: str = os.getenv("REFERENCE_CSV_NAME")
    if REFERENCE_CSV_NAME is None:
        raise EnvironmentError("REFERENCE_CSV_NAME environment variable is not set.")
    AGE_COL: str = os.getenv("AGE_COL", "age")
    print(f"Using age column: {AGE_COL}")
    normative_filepath: str = str(Path(DATA_DIR) / REFERENCE_CSV_NAME)
    participants_tsv: str = str(Path(DATA_DIR) / "participants.tsv")
    
    if not Path(normative_filepath).is_file():
        raise FileNotFoundError(f"Normative reference file not found: {normative_filepath}")
    
    if not Path(participants_tsv).is_file():
        raise FileNotFoundError(f"Participants TSV file not found: {participants_tsv}")
    
    df_measures = pd.read_csv(input_filepath, sep="\t")
    df_normative = pd.read_csv(normative_filepath)
    df_participants = pd.read_csv(participants_tsv, sep="\t")

    # ----------------------------
    # Validate required columns
    # ----------------------------
    required_norm_cols = {
        "roi_name",
        "roi_type",
        "metric",
        "age_min",
        "age_max",
        "sex",
        "expected_mean",
        "expected_sd",
    }
    missing = required_norm_cols - set(df_normative.columns)
    if missing:
        raise ValueError(f"Normative table missing columns: {missing}")

    # ============================
    # Step 2: Extract subject metadata
    # ============================
    entities = parse_file_entities(input_filepath)
    subject = entities.get("subject")

    if subject is None:
        raise ValueError("Could not determine subject from input filename")

    subj_row = df_participants[df_participants["participant_id"] == f"sub-{subject}"]
    if subj_row.empty:
        raise ValueError(f"Subject {subject} not found in participants.tsv")

    age = float(subj_row.iloc[0][AGE_COL])
    sex = str(subj_row.iloc[0]["sex"]).lower()
    print(f"Using sex: {sex}")

    # ============================
    # Step 3: Convert wide → long
    # ============================
    scalar_names = ["FA", "MD", "RD", "AD"]
    value_cols = {s: f"{s}_mean" for s in scalar_names}

    long_records = []

    for _, row in df_measures.iterrows():
        for scalar, col in value_cols.items():
            if col not in df_measures.columns:
                continue
            long_records.append({
                "roi_name": row["region_name"],
                "metric": scalar,
                "value": float(row[col]),
                "voxel_count": int(row.get("voxel_count", np.nan)),
                "valid_fraction": float(row.get("valid_fraction", np.nan)),
            })

    df_long = pd.DataFrame.from_records(long_records)
    if df_long.empty:
        raise ValueError("No valid DTI measures found in input data.")

    # ============================
    # Step 4: Match to normative data
    # ============================
    phenotypes = []

    for _, row in df_long.iterrows():
        roi = row["roi_name"]
        metric = row["metric"]
        value = row["value"]

        df_normative_matches: pd.DataFrame = df_normative[
            (df_normative["roi_name"] == roi)
            & (df_normative["metric"] == metric)
            & (df_normative["age_min"] <= age)
            & (df_normative["age_max"] >= age)
            & ((df_normative["sex"].str.lower() == sex) | (df_normative["sex"] == "any"))
        ]

        if df_normative_matches.empty:
            continue

        # If multiple matches exist, pick the most specific (narrowest age range)
        norm_row = df_normative_matches.sort_values(
            by=(df_normative_matches["age_max"] - df_normative_matches["age_min"])
        ).iloc[0]

        mu = float(norm_row["expected_mean"])
        sd = float(norm_row["expected_sd"])

        if sd <= 0:
            z = np.nan
        else:
            z = (value - mu) / sd

        phenotypes.append({
            "roi_name": roi,
            "roi_type": norm_row.get("roi_type"),
            "metric": metric,
            "value": value,
            "expected_mean": mu,
            "expected_sd": sd,
            "z_value": float(z),
            "age": age,
            "sex": sex,
            "reference_population": norm_row.get("reference_population"),
            "units": norm_row.get("units"),
            "version": norm_row.get("version"),
        })

    # ============================
    # Step 5: Outputs
    # ============================
    output_data = pd.DataFrame.from_records(phenotypes)
    if output_data.empty:
        raise ValueError("No phenotyped DTI measures could be computed.")

    metrics = {
        "n_regions": output_data["roi_name"].nunique(),
        "n_measures": len(output_data),
        "scalars": sorted(output_data["metric"].unique()),
        "reference_population": output_data["reference_population"].unique().tolist(),
        "phenotyping_method": "z-score",
    }

    output_entities = {
        "suffix": "stats",
        "desc": "dtiNormative",
        "extension": ".tsv",
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs
