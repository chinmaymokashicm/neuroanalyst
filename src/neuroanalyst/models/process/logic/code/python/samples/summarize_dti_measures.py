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
    Summarize DTI scalar metrics (FA, MD, RD, AD) within anatomical region.
    Use aparc+aseg.mgz from recon-all to parcellate the registered DTI maps and generate metrics per region.
    Both files should be in the same space (i.e., DTI maps registered to FreeSurfer/MNI space).

    Args:
        input_filepath (str): Path to the input NifTi file that is a stacked DTI scalar maps file (FA, MD, RD, AD).

    Returns:
        output_data (pd.DataFrame): Summary table of regional metrics.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """

    # ============================
    # Step 1: Load Input Data
    # ============================
    DATA_DIR: str = "/data"
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME")
    RECON_ALL_PIPELINE_NAME: str = os.getenv("FS_PIPELINE_NAME")
    if RECON_ALL_PIPELINE_NAME is None:
        raise EnvironmentError("FS_PIPELINE_NAME environment variable is not set.")
    # Get registered DTI scalar maps
    dti_maps: nib.Nifti1Image = nib.load(input_filepath)
    dti_maps_data: np.ndarray = dti_maps.get_fdata()  # Shape: (X, Y, Z, 4) for FA, MD, RD, AD
    
    # Get FreeSurfer aparc+aseg segmentation
    bids_entities: dict = parse_file_entities(input_filepath)
    subject_id, session_id = bids_entities.get("subject"), bids_entities.get("session")
    subject_session_id: str = subject_id + (f"_{session_id}" if session_id else "")
    fs_subject_session_results_root_dir: Path = Path(DATA_DIR) / "derivatives" / RECON_ALL_PIPELINE_NAME / "tmp" / "freesurfer_subjects" / subject_session_id
    aparc_aseg_path: Path = fs_subject_session_results_root_dir / "mri" / "aparc+aseg.mgz"
    if not aparc_aseg_path.exists():
        raise FileNotFoundError(f"FreeSurfer aparc+aseg.mgz file not found: {aparc_aseg_path}")
    aparc_aseg_img: nib.Nifti1Image = nib.Nifti1Image.from_image(nib.load(str(aparc_aseg_path)))
    aparc_aseg_data: np.ndarray = aparc_aseg_img.get_fdata()  # Shape: (X, Y, Z)
    
    # Verify that the images are in the same space
    if dti_maps.shape[:3] != aparc_aseg_data.shape:
        raise ValueError("Input DTI maps and FreeSurfer aparc+aseg segmentation are not in the same space or have different dimensions.")
    if not np.allclose(dti_maps.affine, aparc_aseg_img.affine):
        raise ValueError("Input DTI maps and FreeSurfer aparc+aseg segmentation do not have the same affine transformation.")
    
    # ============================
    # Step 2: Compute Regional Metrics
    # ============================
    df_lut: pd.DataFrame = load_freesurfer_color_lut() # Load FreeSurfer color LUT for region names - columns: ['Index', 'StructName', 'R', 'G', 'B', 'A']
    df_lut = df_lut[["Index", "StructName"]]
    scalar_names = ["FA", "MD", "RD", "AD"]
    records = []
    
    for _, row in df_lut.iterrows():
        region_index = row["Index"]
        region_name = row["StructName"]
        
        if region_index == 0:
            continue  # Skip background
        
        region_mask = aparc_aseg_data == region_index
        if not np.any(region_mask):
            continue  # Skip regions not present in the segmentation
        
        voxel_count = int(np.sum(region_mask))
        if voxel_count == 0:
            continue  # Skip regions with no voxels
        
        region_stats: dict = {
            "region_id": int(region_index),
            "region_name": region_name,
            "voxel_count": voxel_count,
        }
        
        for i, scalar_name in enumerate(scalar_names):
            scalar_data = dti_maps_data[:, :, :, i]
            region_scalar_values = scalar_data[region_mask]
            region_scalar_values = region_scalar_values[np.isfinite(region_scalar_values)] # Remove NaNs/Infs
            region_stats[f"{scalar_name}_mean"] = float(np.mean(region_scalar_values))
            region_stats[f"{scalar_name}_std"] = float(np.std(region_scalar_values))
            region_stats[f"{scalar_name}_min"] = float(np.min(region_scalar_values))
            region_stats[f"{scalar_name}_max"] = float(np.max(region_scalar_values))
        records.append(region_stats)

    # ============================
    # Step 3: Prepare Outputs
    # ============================
    output_data = pd.DataFrame.from_records(records)

    metrics: dict = {
        "n_regions": len(output_data),
        "scalar_maps": scalar_names,
        "parcellation": "FreeSurfer aparc+aseg",
        "space": "registered DTI / FreeSurfer space",
    }

    output_entities: dict = {
        "suffix": "stats",
        "desc": "dtiRegionalMetrics",
        "extension": ".tsv"
    }

    forced_outputs: list = []

    return output_data, metrics, output_entities, forced_outputs