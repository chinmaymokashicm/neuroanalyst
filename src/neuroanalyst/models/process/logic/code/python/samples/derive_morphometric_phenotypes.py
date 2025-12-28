import pandas as pd


def derive_morphometric_phenotypes(input_filepath: str):
    """
    Derive composite morphometric phenotypes from categorized
    FreeSurfer-derived morphometric metrics.

    Args:
        input_filepath (str): Path to categorized morphometry TSV.

    Returns:
        output_data (pd.DataFrame): ROI-level composite phenotypes.
        metrics (dict): Summary statistics.
        output_entities (dict): BIDS-like entities.
        forced_outputs (list): None
    """

    # --------------------------------------------------
    # Step 1: Load categorized data
    # --------------------------------------------------
    df = pd.read_csv(input_filepath, sep="\t")

    required_cols = {
        "roi_name", "roi_type", "hemisphere",
        "metric_family", "bucket"
    }
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_cols - set(df.columns)}")

    records = []

    # --------------------------------------------------
    # Step 2: Aggregate per ROI
    # --------------------------------------------------
    grouped = df.groupby(
        ["roi_name", "roi_type", "hemisphere"],
        dropna=False
    )

    for (roi, roi_type, hemi), g in grouped:
        buckets = set(g["bucket"].tolist())

        phenotypes = []

        # -----------------------------
        # Cortical phenotypes
        # -----------------------------
        if roi_type == "cortical_gm":
            if (
                "low_thickness" in buckets
                or "low_surface_area" in buckets
            ):
                phenotypes.append("cortical_atrophy")

            if (
                "high_thickness" in buckets
                and "high_surface_area" in buckets
            ):
                phenotypes.append("cortical_hypertrophy")

            if any(b.endswith("gyrification") for b in buckets):
                phenotypes.append("altered_gyrification")

            if any(b.endswith("curvature") for b in buckets):
                phenotypes.append("curvature_abnormality")

        # -----------------------------
        # Subcortical phenotypes
        # -----------------------------
        if roi_type == "subcortical_gm":
            if "low_volume" in buckets:
                phenotypes.append("subcortical_atrophy")
            if "high_volume" in buckets:
                phenotypes.append("subcortical_hypertrophy")

        # -----------------------------
        # Default / typical
        # -----------------------------
        if not phenotypes:
            phenotypes.append("morphometrically_typical")

        for phenotype in phenotypes:
            records.append({
                "roi_name": roi,
                "roi_type": roi_type,
                "hemisphere": hemi,
                "composite_phenotype": phenotype,
            })

    output_data = pd.DataFrame.from_records(records)

    # --------------------------------------------------
    # Step 3: Metrics
    # --------------------------------------------------
    metrics = {
        "num_rois": output_data[["roi_name", "hemisphere"]].drop_duplicates().shape[0],
        "num_phenotypes": output_data["composite_phenotype"].nunique(),
        "num_records": len(output_data),
    }

    # --------------------------------------------------
    # Step 4: Output entities
    # --------------------------------------------------
    output_entities = {
        "desc": "morphometryPhenotypes",
        "space": "fsaverage",
        "extension": ".tsv",
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs
