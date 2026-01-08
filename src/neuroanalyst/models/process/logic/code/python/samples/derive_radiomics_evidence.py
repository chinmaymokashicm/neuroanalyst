from neuroanalyst.models.process.logic.core import Metric

import pandas as pd
from collections import Counter

def derive_radiomics_evidence(input_filepath: str):
    """
    Derive Tier 2 (Descriptive Signals) and Tier 3 (Evidence Patterns)
    from bucketed radiomics features.

    Args:
        input_filepath (str): Path to TSV produced by categorize_radiomics_features

    Returns:
        output_data (pd.DataFrame): DataFrame containing derived radiomics evidence
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """

    df = pd.read_csv(input_filepath, sep="\t")

    records = []

    group_cols = ["label_id", "roi_type", "roi_hemisphere", "mask_filename"]
    grouped = df.groupby(group_cols)

    # -------------------------
    # Helper utilities
    # -------------------------
    def bucket_profile(buckets: list[str]) -> Counter:
        return Counter(buckets)

    def has_any(profile: Counter, *keys) -> bool:
        return any(k in profile for k in keys)

    def has_all(profile: Counter, *keys) -> bool:
        return all(k in profile for k in keys)

    # -------------------------
    # Main loop
    # -------------------------
    for roi_keys, roi_df in grouped:
        label_id, roi_type, hemi, mask = roi_keys

        family_groups = roi_df.groupby("feature_family")

        family_signals = {}
        all_buckets = set(roi_df["bucket"])

        # ==========
        # Tier 2: Family-level descriptive signals
        # ==========
        for family, fam_df in family_groups:
            buckets = fam_df["bucket"].tolist()
            profile = bucket_profile(buckets)

            signal_name = None

            if family == "texture":
                if has_any(profile, "high_entropy", "medium_entropy"):
                    signal_name = "elevated_texture_complexity"
                elif has_any(profile, "low_entropy"):
                    signal_name = "low_texture_complexity"
                else:
                    signal_name = "indeterminate_texture_profile"

            elif family == "intensity":
                if has_any(profile, "high_signal_energy"):
                    signal_name = "high_signal_dominance"
                elif has_any(profile, "low_signal_energy"):
                    signal_name = "low_signal_dominance"
                else:
                    signal_name = "balanced_intensity_profile"

            elif family == "shape":
                if has_any(profile, "large_extent"):
                    signal_name = "large_spatial_extent"
                elif has_any(profile, "small_extent"):
                    signal_name = "compact_spatial_extent"
                else:
                    signal_name = "moderate_spatial_extent"

            else:
                signal_name = "unclassified_feature_family"

            family_signals[family] = signal_name

            records.append({
                "label_id": label_id,
                "roi_type": roi_type,
                "roi_hemisphere": hemi,
                "mask_filename": mask,
                "evidence_tier": "Tier2",
                "evidence_type": "descriptive_signal",
                "evidence_name": signal_name,
                "evidence_family": family,
                "evidence_buckets": sorted(profile.keys())
            })

        # ==========
        # Tier 3: Cross-family evidence patterns
        # ==========
        pattern_buckets = sorted(all_buckets)
        patterns = []

        # Texture–Intensity relationships
        if (
            family_signals.get("texture") == "elevated_texture_complexity"
            and family_signals.get("intensity") == "low_signal_dominance"
        ):
            patterns.append("texture_intensity_decoupling")

        if (
            family_signals.get("texture") == "elevated_texture_complexity"
            and family_signals.get("intensity") == "high_signal_dominance"
        ):
            patterns.append("texture_intensity_concordance")

        # Shape–Texture relationships
        if (
            family_signals.get("shape") == "large_spatial_extent"
            and family_signals.get("texture") == "elevated_texture_complexity"
        ):
            patterns.append("diffuse_complex_structure")

        # Fallback: explicitly record absence of higher-order pattern
        if not patterns:
            patterns.append("no_cross_family_pattern")

        for pattern in patterns:
            records.append({
                "label_id": label_id,
                "roi_type": roi_type,
                "roi_hemisphere": hemi,
                "mask_filename": mask,
                "evidence_tier": "Tier3",
                "evidence_type": "evidence_pattern",
                "evidence_name": pattern,
                "evidence_family": "cross_family",
                "evidence_buckets": pattern_buckets
            })

    # -------------------------
    # Final outputs
    # -------------------------
    output_data = pd.DataFrame.from_records(records)
    output_data["evidence_tier"] = output_data["evidence_tier"].astype("category")
    output_data["evidence_type"] = output_data["evidence_type"].astype("category")

    # -------------------------
    # Metrics (lightweight, non-interpretive)
    # -------------------------
    metrics = {
        "num_rois": output_data["label_id"].nunique(),
        "num_tier2_signals": (output_data["evidence_tier"] == "Tier2").sum(),
        "num_tier3_patterns": (output_data["evidence_tier"] == "Tier3").sum(),
    }
    KG_ELIGIBLE_PATTERNS = {
        "texture_intensity_decoupling",
        "texture_intensity_concordance",
        "diffuse_complex_structure",
    }

    CATEGORY: str = "radiomics_evidence"
    for pattern in patterns:
        if pattern in KG_ELIGIBLE_PATTERNS:
            metrics[pattern] = Metric(
                name=pattern,
                value=pattern,
                description=f"Tier 3 radiomics evidence pattern: {pattern}",
                unit=None,
                category=CATEGORY,
                labels=["evidence_pattern", "tier3", "radiomics"]
            )

    output_entities = {
        "desc": "radiomicsEvidence",
        "suffix": "T1w",
        "extension": ".tsv"
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs
