from neuroanalyst.analysis.freesurfer import extract_all_freesurfer_metrics
from neuroanalyst.models.process.logic.core import Metric

import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from bids.layout import parse_file_entities


def load_morphometry_from_reconall(input_filepath: str):
    """Load region-wise morphometric measures from FreeSurfer recon-all outputs.

    Args:
        input_filepath (str): Path to the final file from the recon-all. This will only be used as a reference.

    Returns:
        output_data (pd.DataFrame): ROI-level morphometric measures.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """
    # --------------------------------------------------
    # Step 1: Locate FreeSurfer output directory
    # --------------------------------------------------
    DATA_DIR: str = "/data"
    RECON_ALL_PIPELINE_NAME: str = os.getenv("FS_PIPELINE_NAME")
    if RECON_ALL_PIPELINE_NAME is None:
        raise EnvironmentError("FS_PIPELINE_NAME environment variable is not set.")
    bids_entities: dict = parse_file_entities(input_filepath)
    subject_id, session_id = bids_entities.get("subject"), bids_entities.get("session")
    subject_session_id: str = subject_id + (f"_{session_id}" if session_id else "")
    fs_subject_session_results_root_dir: Path = Path(DATA_DIR) / "derivatives" / RECON_ALL_PIPELINE_NAME / "tmp" / "freesurfer_subjects" / subject_session_id
    
    stats_dir = fs_subject_session_results_root_dir / "stats"
    if not stats_dir.exists():
        raise FileNotFoundError(f"FreeSurfer stats directory not found: {stats_dir}")

    # --------------------------------------------------
    # Step 2: Extract all FreeSurfer metrics (your function)
    # --------------------------------------------------
    all_metrics = extract_all_freesurfer_metrics(str(fs_subject_session_results_root_dir))

    records = []

    # --------------------------------------------------
    # Step 3: Subcortical volumes (aseg)
    # --------------------------------------------------
    aseg_vols = all_metrics.get("subcortical_volumes", {})

    for roi_name, volume in aseg_vols.items():
        records.append({
            "roi_name": roi_name,
            "roi_type": "subcortical_gm",
            "hemisphere": "none",
            "metric": "volume",
            "value": volume,
            "source": "aseg",
        })

    # --------------------------------------------------
    # Step 4: Cortical regional metrics (aparc)
    # --------------------------------------------------
    df_cortical_left = all_metrics.get("cortical_regional_metrics")["lh"]
    df_cortical_right = all_metrics.get("cortical_regional_metrics")["rh"]
    
    features = ['SurfaceArea_mm2', 'GrayVolume_mm3', 'ThickAvg_mm', 'ThickStd_mm', 'MeanCurv', 'GausCurv', 'FoldInd', 'CurvInd']
    
    if isinstance(df_cortical_left, pd.DataFrame) and not df_cortical_left.empty:
        for _, row in df_cortical_left.iterrows():
            roi = row.get("StructName")

            for metric in features:
                if metric in row:
                    records.append({
                        "roi_name": roi,
                        "roi_type": "cortical_gm",
                        "hemisphere": "left",
                        "metric": metric,
                        "value": row[metric],
                        "source": "aparc",
                    })
    
    if isinstance(df_cortical_right, pd.DataFrame) and not df_cortical_right.empty:
        for _, row in df_cortical_right.iterrows():
            roi = row.get("StructName")

            for metric in features:
                if metric in row:
                    records.append({
                        "roi_name": roi,
                        "roi_type": "cortical_gm",
                        "hemisphere": "right",
                        "metric": metric,
                        "value": row[metric],
                        "source": "aparc",
                    })

    # --------------------------------------------------
    # Step 5: Construct output table
    # --------------------------------------------------
    output_data = pd.DataFrame.from_records(records)

    if output_data.empty:
        raise RuntimeError("No morphometric measures could be extracted.")

    # --------------------------------------------------
    # Step 6: Metrics summary
    # --------------------------------------------------
    metrics = {
        "num_rois": output_data["roi_name"].nunique(),
        "num_metrics": output_data["metric"].nunique(),
        "num_records": len(output_data),
        "has_aparc": "aparc" in output_data["source"].unique(),
        "has_aseg": "aseg" in output_data["source"].unique(),
    }

    # --------------------------------------------------
    # Step 7: Output entities
    # --------------------------------------------------
    output_entities = {
        "desc": "morphometry",
        "space": "fsaverage",
        "extension": ".tsv",
    }

    forced_outputs: list[str] = []

    return output_data, metrics, output_entities, forced_outputs