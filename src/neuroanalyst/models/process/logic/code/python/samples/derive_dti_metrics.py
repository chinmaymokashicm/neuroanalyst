from neuroanalyst.models.process.logic.core import Metric

from pathlib import Path

import numpy as np
import pandas as pd
import nibabel as nib


def derive_dti_metrics(input_filepath: str):
    """
    Derive subject-level DTI metrics from stacked scalar maps.

    Args:
        input_filepath (str): Path to stacked FA/MD/RD/AD nifti image.

    Returns:
        output_data (pd.DataFrame): Subject-level metrics.
        metrics (dict): Metadata.
        output_entities (dict): BIDS entities.
        forced_outputs (list): Forced outputs.
    """

    stacked: np.ndarray = nib.load(input_filepath).get_fdata()
    metric_names = ["FA", "MD", "RD", "AD"]

    rows = []
    for i, name in enumerate(metric_names):
        data = stacked[..., i]
        data = data[np.isfinite(data)]

        rows.append({
            "metric": name,
            "mean": np.mean(data),
            "median": np.median(data),
            "std": np.std(data),
            "iqr": np.percentile(data, 75) - np.percentile(data, 25),
        })

    output_data = pd.DataFrame(rows)

    metrics = {
        "aggregation_level": "whole_brain",
        "n_metrics": len(rows),
    }

    output_entities = {
        "desc": "derivedDTIMetrics",
        "suffix": "dwi",
        "extension": ".tsv"
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs
