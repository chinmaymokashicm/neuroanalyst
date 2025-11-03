import numpy as np
import pandas as pd
from rich.progress import track

def summarize_regionwise_metrics(label_map: np.ndarray,
                                metrics_dict: dict,
                                df_lut: pd.DataFrame,
                                mask: np.ndarray = None,
                                min_voxel_count: int = 5,
                                ) -> pd.DataFrame:
    """
    Compute summary stats for DTI metrics within each region.

    Parameters
    ----------
    label_map : np.ndarray
        3D or 4D integer array with region labels (e.g., aseg, aparc+aseg)
    metrics_dict : dict
        Dict of np.ndarray; keys are metric names ('FA', 'MD', etc.), values are 3D arrays matching label_map
    df_lut : pd.DataFrame
        LUT DataFrame: columns {Index, StructName, ...} mapping label integer to name
    mask : np.ndarray, optional
        Boolean mask of same shape as label_map; restricts analysis to brain/tissue voxels only (default None)
    min_voxel_count : int
        Minimum number of voxels to include region in summary (default 5)

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ['Label', 'StructName', 'n_vox'] + metric stats for each region

    Example
    -------
    >>> result = summarize_regionwise_metrics(seg, {'FA': fa_arr, 'MD': md_arr}, lut_df)
    >>> print(result.head())
    """
    # Select labels from LUT
    labels = df_lut['Index'].unique()
    results = []
    print(f"Computing region-wise metrics for {len(labels)} labels...")

    for label in labels:
        if label == 0:  # Often background
            continue
        roi_mask = (label_map == label)
        if mask is not None:
            roi_mask = roi_mask & mask
        n_vox = np.sum(roi_mask)
        if n_vox < min_voxel_count:
            continue  # skip tiny regions

        lookup = df_lut[df_lut["Index"] == label]
        struct_name = lookup["StructName"].iloc[0] if not lookup.empty else str(label)

        row = {'Label': label, 'StructName': struct_name, 'n_vox': n_vox}
        for metric_name, arr in metrics_dict.items():
            vals = arr[roi_mask]
            valid_vals = vals[~np.isnan(vals)]
            if len(valid_vals) == 0:
                stat_mean, stat_std, stat_median = np.nan, np.nan, np.nan
            else:
                stat_mean = float(np.mean(valid_vals))
                stat_std = float(np.std(valid_vals))
                stat_median = float(np.median(valid_vals))
            row[f'{metric_name}_mean'] = stat_mean
            row[f'{metric_name}_std'] = stat_std
            row[f'{metric_name}_median'] = stat_median
        results.append(row)
    return pd.DataFrame(results)

def metrics_to_long_df(label_map: np.ndarray,
                      metrics_dict: dict,
                      mask: np.ndarray = None
                      ) -> pd.DataFrame:
    """
    Returns a long-form DataFrame with each voxel's label and values for each supplied metric.

    Parameters
    ----------
    label_map : np.ndarray
        3D array of region/segmentation labels (same space as each metric).
    metrics_dict : dict
        {metric_name: np.ndarray} of same shape as label_map.
    mask : np.ndarray, optional
        If provided, only output rows for voxels where mask == True.

    Returns
    -------
    pd.DataFrame
        Columns: ['Label'] + list(metrics_dict.keys())
    """
    idxs = np.where(mask) if mask is not None else np.where(np.ones_like(label_map, dtype=bool))
    data = {'Label': label_map[idxs].astype(int)}
    for mname, arr in metrics_dict.items():
        data[mname] = arr[idxs]
    df = pd.DataFrame(data)
    return df