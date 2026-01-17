from neuroanalyst.models.process.logic.core import Metric
from neuroanalyst.analysis.freesurfer import load_freesurfer_color_lut

import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import nibabel as nib
from bids.layout import parse_file_entities


def summarize_dti_measures(input_filepath: str):
    """
    Summarize DTI scalar metrics (FA, MD, RD, AD) within anatomical regions
    defined by FreeSurfer aparc+aseg.

    Assumes:
        - DTI scalar maps are already registered to FreeSurfer space
        - Channel order is [FA, MD, RD, AD]
    """

    # ============================
    # Step 1: Environment & Inputs
    # ============================
    DATA_DIR = "/data"
    FS_PIPELINE_NAME = os.getenv("FS_PIPELINE_NAME")

    if FS_PIPELINE_NAME is None:
        raise EnvironmentError("FS_PIPELINE_NAME environment variable is not set.")

    dti_img = nib.load(input_filepath)
    dti_data = dti_img.get_fdata()  # (X, Y, Z, 4)

    if dti_data.ndim != 4 or dti_data.shape[-1] != 4:
        raise ValueError("DTI input must be 4D with exactly 4 volumes (FA, MD, RD, AD).")

    scalar_names = ["FA", "MD", "RD", "AD"]
    scalar_index = dict(zip(scalar_names, range(4)))

    # ============================
    # Step 2: Load FreeSurfer segmentation
    # ============================
    entities = parse_file_entities(input_filepath)
    subject = entities.get("subject")
    session = entities.get("session")

    subject_session = subject + (f"_{session}" if session else "")

    fs_root = (
        Path(DATA_DIR)
        / "derivatives"
        / FS_PIPELINE_NAME
        / "tmp"
        / "freesurfer_subjects"
        / subject_session
    )

    aparc_path = fs_root / "mri" / "aparc+aseg.mgz"
    if not aparc_path.exists():
        raise FileNotFoundError(f"Missing FreeSurfer segmentation: {aparc_path}")

    aparc_img = nib.load(str(aparc_path))
    aparc_data = aparc_img.get_fdata()

    # ============================
    # Step 3: Space validation
    # ============================
    if dti_data.shape[:3] != aparc_data.shape:
        raise ValueError("DTI maps and aparc+aseg have different dimensions.")

    if not np.allclose(dti_img.affine, aparc_img.affine, atol=1e-3):
        raise ValueError("DTI maps and aparc+aseg affines do not match.")

    # ============================
    # Step 4: Valid DTI mask (FA-based)
    # ============================
    fa_data = dti_data[..., scalar_index["FA"]]
    valid_dti_mask = np.isfinite(fa_data) & (fa_data > 0.2)

    # ============================
    # Step 5: Regional statistics
    # ============================
    df_lut: pd.DataFrame = load_freesurfer_color_lut()[["Index", "StructName"]]

    records = []

    for _, row in df_lut.iterrows():
        label = int(row["Index"])
        name = row["StructName"]

        if label == 0:
            continue

        region_mask = (aparc_data == label) & valid_dti_mask
        voxel_count = int(np.sum(region_mask))

        if voxel_count == 0:
            continue

        stats = {
            "region_id": label,
            "region_name": name,
            "voxel_count": voxel_count,
        }

        for scalar in scalar_names:
            values = dti_data[..., scalar_index[scalar]][region_mask]
            values = values[np.isfinite(values)]

            stats[f"{scalar}_mean"] = float(np.mean(values))
            stats[f"{scalar}_median"] = float(np.median(values))
            stats[f"{scalar}_std"] = float(np.std(values))
            stats[f"{scalar}_p25"] = float(np.percentile(values, 25))
            stats[f"{scalar}_p75"] = float(np.percentile(values, 75))
            stats[f"{scalar}_min"] = float(np.min(values))
            stats[f"{scalar}_max"] = float(np.max(values))

        records.append(stats)

    # ============================
    # Step 6: Outputs
    # ============================
    output_data = pd.DataFrame.from_records(records)

    metrics = {
        "n_regions": len(output_data),
        "scalars": scalar_names,
        "scalar_order": scalar_names,
        "parcellation": "FreeSurfer aparc+aseg",
        "valid_fa_threshold": 0.2,
        "space": "FreeSurfer / registered DTI space",
    }

    output_entities: dict = {
        "suffix": "stats",
        "desc": "dtiRegionalMetrics",
        "extension": ".tsv",
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs
