from ..utils.data import convert_string_to_number

import os, json
from pathlib import Path
from typing import Optional, Union, Literal

import numpy as np
import pandas as pd
import nibabel as nib
import nibabel.freesurfer.io as fsio

# ============================================================================
# SUBCORTICAL VOLUMETRIC METRICS (aseg.stats)
# ============================================================================

def load_aseg_stats(aseg_stats_path: str) -> tuple[dict, pd.DataFrame]:
    """
    Load subcortical segmentation statistics from aseg.stats file.

    Parameters:
    -----------
    aseg_stats_path : str
        Path to the aseg.stats file (typically <SUBJECTS_DIR>/<subject>/stats/aseg.stats)

    Returns:
    --------
    dict
        Dictionary containing measures with keys as column names.
    
    pd.DataFrame
        DataFrame containing segmentation index, segmentation name, number of voxels,
        volume (mm³), mean intensity, std intensity, min intensity, max intensity,
        and range of intensities.

    Example:
    --------
    >>> aseg_df = load_aseg_stats('subjects/subject01/stats/aseg.stats')
    >>> brain_volume = aseg_df[aseg_df['SegId'] == 0]['Volume'].values[0]
    """
    global_measures = {}
    columns: list[str] = []
    rows: list[dict] = []
    
    with open(aseg_stats_path, 'r') as f:
        lines = [line for line in f.readlines() if line.strip() != '']
        
        # Load global measures
        for line in lines:
            if line.startswith('# Measure'):
                parts = line.split(',')
                measure_name = parts[0].split()[2].strip()
                measure_value = convert_string_to_number(parts[3].strip()) if convert_string_to_number(parts[3].strip()) is not None else parts[3].strip()
                global_measures[measure_name] = measure_value
            # Load table columns
            if line.startswith("# TableCol"):
                line = line.replace("#", "").strip()
                parts = line.split()
                if parts[1] == "1":
                    continue # Skip index column
                if parts[2] == "ColHeader":
                    column_name: str = parts[3].strip()
                    columns.append(column_name)
                    
        # Load table rows
        for line in lines:
            if not line.startswith('#') and line.strip() != '':
                parts = line.strip().split()[1:]  # Skip index column
                if len(parts) >= len(columns):
                    row_dict: dict = {}
                    for col_name, value in zip(columns, parts):
                        row_dict[col_name] = convert_string_to_number(value) if convert_string_to_number(value) is not None else value
                    rows.append(row_dict)
                    
        df_aseg = pd.DataFrame(rows)
        # Create column for hemisphere
        def determine_hemisphere(struct_name: str) -> str:
            if struct_name.startswith('Left-') or struct_name.startswith('lh-'):
                return 'left'
            elif struct_name.startswith('Right-') or struct_name.startswith('rh-'):
                return 'right'
            else:
                return 'bilateral'

        df_aseg['Hemisphere'] = df_aseg['StructName'].apply(determine_hemisphere)
    return global_measures, df_aseg


def extract_subcortical_volumes(aseg_df: pd.DataFrame, hemisphere: Literal["left", "right", "bilateral"] = "bilateral") -> dict[str, float]:
    """
    Extract individual subcortical structure volumes.

    Parameters:
    -----------
    aseg_df : pd.DataFrame
        DataFrame from load_aseg_stats()
    hemisphere : Literal["left", "right", "bilateral"]
        Hemisphere to extract volumes for: 'left', 'right', or 'bilateral' (default: 'bilateral')

    Returns:
    --------
    dict[str, float]
        dictionary with structure names and volumes in mm³

    Example:
    --------
    >>> subcort_vols = extract_subcortical_volumes(aseg_df, hemisphere='both')
    >>> print(f"Left thalamus: {subcort_vols['Left-Thalamus']} mm³")
    """
    structures = {
        'Thalamus': ['Thalamus'],
        'Caudate': ['Caudate'],
        'Putamen': ['Putamen'],
        'Pallidum': ['Pallidum'],
        'Hippocampus': ['Hippocampus'],
        'Amygdala': ['Amygdala'],
        'Nucleus Accumbens': ['Accumbens'],
        'Ventricles': ['Ventricle'],
        'Cerebellum': ['Cerebellum'],
    }

    volumes = {}

    for struct_name, search_terms in structures.items():
        for term in search_terms:
            # Filter by hemisphere if specified
            if hemisphere == 'left':
                rows = aseg_df[aseg_df['Hemisphere'] == 'left']
            elif hemisphere == 'right':
                rows = aseg_df[aseg_df['Hemisphere'] == 'right']
            else:  # bilateral
                rows = aseg_df[aseg_df['StructName'].str.contains(term, case=False)]
            if len(rows) > 0:
                vol = float(rows['Volume_mm3'].sum())
                struct_full_name = f'{struct_name}' if hemisphere == 'bilateral' else f'{hemisphere.capitalize()}-{struct_name}'
                volumes[struct_full_name] = vol

    return volumes


# ============================================================================
# CORTICAL PARCELLATION STATISTICS (aparc.stats)
# ============================================================================

def load_aparc_stats(aparc_stats_path: str) -> pd.DataFrame:
    """
    Load cortical parcellation statistics from aparc.stats file.

    Parameters:
    -----------
    aparc_stats_path : str
        Path to aparc.stats file (typically <SUBJECTS_DIR>/<subject>/stats/lh.aparc.stats
        or rh.aparc.stats)

    Returns:
    --------
    pd.DataFrame
        DataFrame with columns: StructName, NumVoxels, SurfaceArea_mm2, 
        GrayVolume_mm3, ThickAvg_mm, ThickStd_mm, MeanCurv, GausCurv, FoldInd,
        CurvInd

    Example:
    --------
    >>> lh_aparc = load_aparc_stats('subjects/subject01/stats/lh.aparc.stats')
    >>> print(lh_aparc[['StructName', 'ThickAvg_mm']].head())
    """
    stats_data = []

    with open(aparc_stats_path, 'r') as f:
        for line in f:
            # Skip comments and empty lines
            if line.startswith('#') or line.strip() == '':
                continue

            parts = line.strip().split()
            if len(parts) >= 10:
                try:
                    stats_dict = {
                        'StructName': parts[0],
                        'NumVoxels': int(parts[1]),
                        'SurfaceArea_mm2': float(parts[2]),
                        'GrayVolume_mm3': float(parts[3]),
                        'ThickAvg_mm': float(parts[4]),
                        'ThickStd_mm': float(parts[5]),
                        'MeanCurv': float(parts[6]),
                        'GausCurv': float(parts[7]),
                        'FoldInd': float(parts[8]),
                        'CurvInd': float(parts[9]),
                    }
                    stats_data.append(stats_dict)
                except (ValueError, IndexError):
                    continue

    return pd.DataFrame(stats_data)


def extract_cortical_regional_metrics(lh_aparc: pd.DataFrame, 
                                      rh_aparc: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Extract and combine cortical regional metrics from both hemispheres.

    Parameters:
    -----------
    lh_aparc : pd.DataFrame
        Left hemisphere aparc.stats DataFrame
    rh_aparc : pd.DataFrame
        Right hemisphere aparc.stats DataFrame

    Returns:
    --------
    dict[str, pd.DataFrame]
        dictionary with 'lh', 'rh', and 'bilateral' keys containing regional metrics

    Example:
    --------
    >>> cortical_metrics = extract_cortical_regional_metrics(lh_aparc, rh_aparc)
    >>> print(cortical_metrics['bilateral'][['StructName', 'ThickAvg_mm']])
    """
    results = {
        'lh': lh_aparc.copy(),
        'rh': rh_aparc.copy(),
    }

    # Merge hemispheres and compute bilateral statistics
    lh_aparc['Hemisphere'] = 'LH'
    rh_aparc['Hemisphere'] = 'RH'

    bilateral = pd.concat([lh_aparc, rh_aparc], ignore_index=True)

    # Group by structure name (removing hemisphere prefix) and compute means
    bilateral['StructName_base'] = bilateral['StructName'].str.replace('lh_|rh_', '', regex=True)
    bilateral_summary = bilateral.groupby('StructName_base')[
        ['SurfaceArea_mm2', 'GrayVolume_mm3', 'ThickAvg_mm', 'MeanCurv', 'GausCurv']
    ].mean()

    results['bilateral'] = bilateral_summary

    return results


def extract_total_cortical_metrics(lh_aparc: pd.DataFrame, 
                                    rh_aparc: pd.DataFrame) -> dict[str, float]:
    """
    Extract total cortical surface area, volume, and thickness from both hemispheres.

    Parameters:
    -----------
    lh_aparc : pd.DataFrame
        Left hemisphere aparc.stats DataFrame
    rh_aparc : pd.DataFrame
        Right hemisphere aparc.stats DataFrame

    Returns:
    --------
    dict[str, float]
        dictionary with total cortical metrics (excluding corpus callosum)

    Example:
    --------
    >>> total_metrics = extract_total_cortical_metrics(lh_aparc, rh_aparc)
    >>> print(f"Total cortical thickness: {total_metrics['TotalThickAvg_mm']:.2f} mm")
    """
    # Filter out corpus callosum (not cortical tissue)
    lh_filtered = lh_aparc[~lh_aparc['StructName'].str.contains('corpus', case=False)]
    rh_filtered = rh_aparc[~rh_aparc['StructName'].str.contains('corpus', case=False)]

    metrics = {
        'LH_TotalSurfaceArea_mm2': float(lh_filtered['SurfaceArea_mm2'].sum()),
        'RH_TotalSurfaceArea_mm2': float(rh_filtered['SurfaceArea_mm2'].sum()),
        'Bilateral_TotalSurfaceArea_mm2': float(lh_filtered['SurfaceArea_mm2'].sum() + rh_filtered['SurfaceArea_mm2'].sum()),

        'LH_TotalGrayVolume_mm3': float(lh_filtered['GrayVolume_mm3'].sum()),
        'RH_TotalGrayVolume_mm3': float(rh_filtered['GrayVolume_mm3'].sum()),
        'Bilateral_TotalGrayVolume_mm3': float(lh_filtered['GrayVolume_mm3'].sum() + rh_filtered['GrayVolume_mm3'].sum()),

        'LH_AvgThickness_mm': float(lh_filtered['ThickAvg_mm'].mean()),
        'RH_AvgThickness_mm': float(rh_filtered['ThickAvg_mm'].mean()),
        'Bilateral_AvgThickness_mm': float((lh_filtered['ThickAvg_mm'].mean() + rh_filtered['ThickAvg_mm'].mean()) / 2),
    }

    return metrics


# ============================================================================
# SURFACE-BASED VERTEX-WISE METRICS
# ============================================================================

def load_surface_overlay(surface_file_path: str) -> np.ndarray:
    """
    Load vertex-wise surface overlay file (e.g., thickness, curvature, area).

    Parameters:
    -----------
    surface_file_path : str
        Path to surface file (typically <SUBJECTS_DIR>/<subject>/surf/lh.thickness,
        lh.area, lh.curv, lh.sulc, etc.)

    Returns:
    --------
    np.ndarray
        1D array containing vertex-wise values (~160k vertices per hemisphere)

    Example:
    --------
    >>> thickness = load_surface_overlay('subjects/subject01/surf/lh.thickness')
    >>> print(f"Number of vertices: {len(thickness)}")
    >>> print(f"Mean thickness: {np.nanmean(thickness):.3f} mm")

    Notes:
    ------
    Uses nibabel's freesurfer.io module to read MGH/MGZ surface files.
    """
    try:
        data = fsio.read_morph_data(surface_file_path)
        return data
    except Exception as e:
        raise RuntimeError(f"Error loading surface overlay: {e}")


def compute_vertex_wise_statistics(vertex_data: np.ndarray) -> dict[str, float]:
    """
    Compute summary statistics for vertex-wise surface data.

    Parameters:
    -----------
    vertex_data : np.ndarray
        1D array from load_surface_overlay()

    Returns:
    --------
    dict[str, float]
        dictionary with mean, median, std, min, max, 95th percentile, etc.

    Example:
    --------
    >>> thickness = load_surface_overlay('subjects/subject01/surf/lh.thickness')
    >>> stats = compute_vertex_wise_statistics(thickness)
    >>> print(stats)
    """
    valid_data = vertex_data[~np.isnan(vertex_data)]

    stats = {
        'Mean': np.mean(valid_data),
        'Median': np.median(valid_data),
        'Std': np.std(valid_data),
        'Min': np.min(valid_data),
        'Max': np.max(valid_data),
        'P5': np.percentile(valid_data, 5),
        'P95': np.percentile(valid_data, 95),
        'Skewness': float(pd.Series(valid_data).skew()),
        'Kurtosis': float(pd.Series(valid_data).kurtosis()),
        'NValid': len(valid_data),
        'NInvalid': np.sum(np.isnan(vertex_data)),
    }

    return stats


def load_multiple_surface_overlays(subject_dir: str, 
                                    hemisphere: str = 'lh') -> dict[str, np.ndarray]:
    """
    Load all standard surface overlays for a given hemisphere.

    Parameters:
    -----------
    subject_dir : str
        Path to subject directory (parent of surf/ subdirectory)
    hemisphere : str
        'lh' for left hemisphere or 'rh' for right hemisphere

    Returns:
    --------
    dict[str, np.ndarray]
        dictionary mapping metric names to vertex-wise data arrays
        (thickness, area, volume, curv, sulc, jacobian_white, pial_lgi)

    Example:
    --------
    >>> surf_data = load_multiple_surface_overlays('subjects/subject01', hemisphere='lh')
    >>> print(surf_data.keys())
    """
    surf_dir = os.path.join(subject_dir, 'surf')
    metric_names = ['thickness', 'area', 'volume', 'curv', 'sulc', 'jacobian_white', 'pial_lgi', 'white', 'pial']

    overlays = {}
    for metric in metric_names:
        file_path = os.path.join(surf_dir, f'{hemisphere}.{metric}')
        if os.path.exists(file_path):
            try:
                overlays[metric] = load_surface_overlay(file_path)
            except Exception as e:
                print(f"Warning: Could not load {metric} from {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")

    return overlays


def extract_surface_statistics_summary(subject_dir: str) -> pd.DataFrame:
    """
    Extract summary statistics for all surface overlays (both hemispheres).

    Parameters:
    -----------
    subject_dir : str
        Path to subject directory

    Returns:
    --------
    pd.DataFrame
        Summary statistics table with metrics as rows and statistics as columns

    Example:
    --------
    >>> surface_summary = extract_surface_statistics_summary('subjects/subject01')
    >>> print(surface_summary)
    """
    summary_rows = []

    for hemisphere in ['lh', 'rh']:
        overlays = load_multiple_surface_overlays(subject_dir, hemisphere=hemisphere)

        for metric_name, data in overlays.items():
            stats = compute_vertex_wise_statistics(data)
            stats['Hemisphere'] = hemisphere
            stats['Metric'] = metric_name
            summary_rows.append(stats)

    # Re-arrange columns
    if summary_rows:
        columns: list[str] = ['Hemisphere', 'Metric'] + [key for key in summary_rows[0].keys() if key not in ['Hemisphere', 'Metric']]
        return pd.DataFrame(summary_rows, columns=columns)
    else:
        return pd.DataFrame()  # Return empty DataFrame if no data


# ============================================================================
# GRAY-TO-WHITE MATTER CONTRAST RATIO
# ============================================================================

def load_gwr_overlay(subject_dir: str, hemisphere: str = 'lh') -> np.ndarray:
    """
    Load gray-to-white matter contrast ratio (GWR) surface overlay.

    Parameters:
    -----------
    subject_dir : str
        Path to subject directory
    hemisphere : str
        'lh' or 'rh'

    Returns:
    --------
    np.ndarray
        Vertex-wise gray-to-white contrast ratio values

    Example:
    --------
    >>> gwr = load_gwr_overlay('subjects/subject01', hemisphere='lh')
    >>> print(f"Mean GWR: {np.nanmean(gwr):.3f}")
    """
    gwr_file = os.path.join(subject_dir, 'surf', f'{hemisphere}.w-g.pct.mgh')

    if os.path.exists(gwr_file):
        return load_surface_overlay(gwr_file)
    else:
        print(f"GWR file not found: {gwr_file}")
        return None


def extract_gwr_statistics(subject_dir: str) -> dict[str, float]:
    """
    Extract gray-to-white matter contrast ratio statistics.

    Parameters:
    -----------
    subject_dir : str
        Path to subject directory

    Returns:
    --------
    dict[str, float]
        dictionary with GWR statistics for both hemispheres

    Example:
    --------
    >>> gwr_stats = extract_gwr_statistics('subjects/subject01')
    >>> print(f"Mean GWR LH: {gwr_stats['LH_Mean']:.3f}")
    """
    gwr_stats = {}

    for hemisphere in ['lh', 'rh']:
        gwr = load_gwr_overlay(subject_dir, hemisphere=hemisphere)
        if gwr is not None:
            stats = compute_vertex_wise_statistics(gwr)
            prefix = 'LH' if hemisphere == 'lh' else 'RH'
            for key, val in stats.items():
                gwr_stats[f'{prefix}_{key}'] = val

    return gwr_stats


# ============================================================================
# SUBFIELD SEGMENTATIONS (Hippocampus, Amygdala)
# ============================================================================

def load_subfield_segmentation(aseg_subfield_path: str, 
                               structure: str = 'hippocampus') -> pd.DataFrame:
    """
    Load hippocampal subfield or amygdala nuclei segmentation statistics.

    Parameters:
    -----------
    aseg_subfield_path : str
        Path to subfield segmentation stats file 
        (e.g., <SUBJECTS_DIR>/<subject>/stats/lh.hippoSf.stats or
        <SUBJECTS_DIR>/<subject>/stats/lh.amygNucSf.stats)
    structure : str
        'hippocampus' or 'amygdala' (for proper naming of subfields/nuclei)

    Returns:
    --------
    pd.DataFrame
        DataFrame with subfield/nuclei volumes and statistics

    Example:
    --------
    >>> hipp_sf = load_subfield_segmentation('subjects/subject01/stats/lh.hippoSf.stats',
    ...                                       structure='hippocampus')
    >>> print(hipp_sf[['SubfieldName', 'Volume_mm3']])
    """
    stats_data = []

    with open(aseg_subfield_path, 'r') as f:
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue

            parts = line.strip().split()
            if len(parts) >= 3:
                try:
                    stats_dict = {
                        'SubfieldId': int(parts[0]),
                        'SubfieldName': parts[1],
                        'Volume_mm3': float(parts[2]),
                        'Mean_Intensity': float(parts[3]) if len(parts) > 3 else np.nan,
                    }
                    stats_data.append(stats_dict)
                except (ValueError, IndexError):
                    continue

    return pd.DataFrame(stats_data)


def extract_hippocampal_volumes(subject_dir: str) -> dict[str, float]:
    """
    Extract total and subfield-specific hippocampal volumes.

    Parameters:
    -----------
    subject_dir : str
        Path to subject directory

    Returns:
    --------
    dict[str, float]
        dictionary with hippocampal subfield volumes for both hemispheres
        (CA1, CA2/3, CA4, dentate gyrus, subiculum, presubiculum, etc.)

    Example:
    --------
    >>> hipp_vols = extract_hippocampal_volumes('subjects/subject01')
    >>> print(f"Left CA1: {hipp_vols['LH_CA1']} mm³")
    """
    hip_volumes = {}

    for hemisphere, prefix in [('lh', 'LH'), ('rh', 'RH')]:
        stats_file = os.path.join(subject_dir, 'stats', f'{hemisphere}.hippoSf.stats')

        if os.path.exists(stats_file):
            hipp_df = load_subfield_segmentation(stats_file, structure='hippocampus')
            for _, row in hipp_df.iterrows():
                key = f'{prefix}_{row["SubfieldName"]}'
                hip_volumes[key] = row['Volume_mm3']
        else:
            print(f"Hippocampal subfield file not found: {stats_file}")

    return hip_volumes


def extract_amygdala_volumes(subject_dir: str) -> dict[str, float]:
    """
    Extract amygdala nuclei volumes.

    Parameters:
    -----------
    subject_dir : str
        Path to subject directory

    Returns:
    --------
    dict[str, float]
        dictionary with amygdala nuclei volumes for both hemispheres

    Example:
    --------
    >>> amyg_vols = extract_amygdala_volumes('subjects/subject01')
    >>> print(f"Left lateral nucleus: {amyg_vols['LH_Lateral']} mm³")
    """
    amyg_volumes = {}

    for hemisphere, prefix in [('lh', 'LH'), ('rh', 'RH')]:
        stats_file = os.path.join(subject_dir, 'stats', f'{hemisphere}.amygNucSf.stats')

        if os.path.exists(stats_file):
            amyg_df = load_subfield_segmentation(stats_file, structure='amygdala')
            for _, row in amyg_df.iterrows():
                key = f'{prefix}_{row["SubfieldName"]}'
                amyg_volumes[key] = row['Volume_mm3']
        else:
            print(f"Amygdala nuclei file not found: {stats_file}")

    return amyg_volumes


# ============================================================================
# BRAINSTEM SUBSTRUCTURES
# ============================================================================

def load_brainstem_segmentation(brainstem_stats_path: str) -> pd.DataFrame:
    """
    Load brainstem substructure segmentation statistics.

    Parameters:
    -----------
    brainstem_stats_path : str
        Path to brainstem stats file
        (e.g., <SUBJECTS_DIR>/<subject>/stats/brainstemSf.stats)

    Returns:
    --------
    pd.DataFrame
        DataFrame with brainstem substructure volumes

    Example:
    --------
    >>> brainstem = load_brainstem_segmentation('subjects/subject01/stats/brainstemSf.stats')
    >>> print(brainstem)
    """
    stats_data = []

    with open(brainstem_stats_path, 'r') as f:
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue

            parts = line.strip().split()
            if len(parts) >= 3:
                try:
                    stats_dict = {
                        'StructureId': int(parts[0]),
                        'StructureName': parts[1],
                        'Volume_mm3': float(parts[2]),
                        'Mean_Intensity': float(parts[3]) if len(parts) > 3 else np.nan,
                    }
                    stats_data.append(stats_dict)
                except (ValueError, IndexError):
                    continue

    return pd.DataFrame(stats_data)


# ============================================================================
# COMPREHENSIVE SUBJECT-LEVEL EXTRACTION
# ============================================================================

def extract_all_freesurfer_metrics(subject_dir: str) -> dict[str, Union[float, dict, pd.DataFrame]]:
    """
    Comprehensive function to extract all available FreeSurfer metrics for a subject.

    Parameters:
    -----------
    subject_dir : str
        Path to subject directory (parent of stats/ and surf/ subdirectories)

    Returns:
    --------
    dict
        Nested dictionary containing:
        - global_volumes: global brain volume metrics
        - subcortical_volumes: individual structure volumes
        - cortical_metrics: regional cortical statistics
        - surface_statistics: vertex-wise surface metric summaries
        - gwr_statistics: gray-to-white matter contrast ratio
        - hippocampal_volumes: hippocampal subfield volumes
        - amygdala_volumes: amygdala nuclei volumes
        - brainstem_volumes: brainstem substructure volumes

    Example:
    --------
    >>> all_metrics = extract_all_freesurfer_metrics('subjects/subject01')
    >>> print(all_metrics.keys())
    >>> print(all_metrics['global_volumes'])
    """
    all_metrics = {}

    # Load aseg statistics
    aseg_stats_path = os.path.join(subject_dir, 'stats', 'aseg.stats')
    if os.path.exists(aseg_stats_path):
        global_measures, aseg_df = load_aseg_stats(aseg_stats_path)
        all_metrics['global_volumes'] = global_measures
        all_metrics['subcortical_volumes'] = extract_subcortical_volumes(aseg_df)
    else:
        print(f"aseg.stats not found: {aseg_stats_path}")
        all_metrics['global_volumes'] = {}
        all_metrics['subcortical_volumes'] = {}

    # Load cortical parcellation
    lh_aparc_path = os.path.join(subject_dir, 'stats', 'lh.aparc.stats')
    rh_aparc_path = os.path.join(subject_dir, 'stats', 'rh.aparc.stats')

    if os.path.exists(lh_aparc_path) and os.path.exists(rh_aparc_path):
        lh_aparc = load_aparc_stats(lh_aparc_path)
        rh_aparc = load_aparc_stats(rh_aparc_path)
        all_metrics['cortical_regional_metrics'] = extract_cortical_regional_metrics(lh_aparc, rh_aparc)
        all_metrics['total_cortical_metrics'] = extract_total_cortical_metrics(lh_aparc, rh_aparc)
    else:
        print(f"aparc.stats files not found")
        all_metrics['cortical_regional_metrics'] = {}
        all_metrics['total_cortical_metrics'] = {}

    # Load surface statistics
    all_metrics['surface_statistics'] = extract_surface_statistics_summary(subject_dir)

    # Load GWR statistics
    all_metrics['gwr_statistics'] = extract_gwr_statistics(subject_dir)

    # Load subfield segmentations (optional)
    all_metrics['hippocampal_volumes'] = extract_hippocampal_volumes(subject_dir)
    all_metrics['amygdala_volumes'] = extract_amygdala_volumes(subject_dir)

    # Load brainstem segmentation (optional)
    brainstem_path = os.path.join(subject_dir, 'stats', 'brainstemSf.stats')
    if os.path.exists(brainstem_path):
        all_metrics['brainstem_volumes'] = load_brainstem_segmentation(brainstem_path)
    else:
        all_metrics['brainstem_volumes'] = pd.DataFrame()

    return all_metrics

def export_metrics(all_metrics: dict, output_dir: str) -> None:
    """
    Export extracted metrics to separate CSV files.

    Parameters:
    -----------
    all_metrics : dict
        Output from extract_all_freesurfer_metrics()
    output_prefix : str
        Prefix for output CSV files (e.g., 'subject01')

    Example:
    --------
    >>> all_metrics = extract_all_freesurfer_metrics('subjects/subject01')
    >>> export_metrics_to_csv(all_metrics, 'subject01')
    # Creates: subject01_global_volumes.csv, subject01_cortical_metrics.csv, etc.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Global volumes
    if all_metrics['global_volumes']:
        with open(os.path.join(output_dir, 'global_volumes.json'), 'w') as f:
            json.dump(all_metrics['global_volumes'], f, indent=4)

    # Subcortical volumes
    if all_metrics['subcortical_volumes']:
        with open(os.path.join(output_dir, 'subcortical_volumes.json'), 'w') as f:
            json.dump(all_metrics['subcortical_volumes'], f, indent=4)

    # Cortical regional metrics
    if 'bilateral' in all_metrics['cortical_regional_metrics']:
        all_metrics['cortical_regional_metrics']['bilateral'].to_csv(
            os.path.join(output_dir, 'cortical_bilateral.csv')
        )

    # Total cortical metrics
    if all_metrics['total_cortical_metrics']:
        with open(os.path.join(output_dir, 'total_cortical_metrics.json'), 'w') as f:
            json.dump(all_metrics['total_cortical_metrics'], f, indent=4)

    # Surface statistics
    all_metrics['surface_statistics'].to_csv(
        os.path.join(output_dir, 'surface_statistics.csv'), index=False
    )

    # GWR statistics
    if all_metrics['gwr_statistics']:
        gwr_df = pd.DataFrame([all_metrics['gwr_statistics']])
        gwr_df.to_csv(os.path.join(output_dir, 'gwr_statistics.csv'), index=False)

    # Hippocampal volumes
    if all_metrics['hippocampal_volumes']:
        hipp_df = pd.DataFrame([all_metrics['hippocampal_volumes']])
        hipp_df.to_csv(os.path.join(output_dir, 'hippocampal_volumes.csv'), index=False)

    # Amygdala volumes
    if all_metrics['amygdala_volumes']:
        amyg_df = pd.DataFrame([all_metrics['amygdala_volumes']])
        amyg_df.to_csv(os.path.join(output_dir, 'amygdala_volumes.csv'), index=False)

    print(f"Metrics exported to directory: {output_dir}")