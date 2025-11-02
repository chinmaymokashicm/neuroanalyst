import os, subprocess, json
from pathlib import Path
import traceback
from warnings import warn
from typing import Optional

from dipy.io.image import load_nifti
from dipy.core.gradients import gradient_table
from dipy.io.gradients import read_bvals_bvecs
from dipy.denoise.patch2self import patch2self
import nibabel as nib
import numpy as np

def dipy_denoising_patch2self(input_filepath: str):
    """
    Denoising using dipy patch2self algorithm.
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (nibabel.Nifti1Image): NIfTI image of denoised DWI data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    def calculate_snr(data: np.ndarray, mask: Optional[np.ndarray] = None) -> float:
        """
        Calculate the SNR of the given data.
        
        Args:
            data: A numpy array of shape (X, Y, Z, N) representing the DWI data.
            mask: An optional binary mask to specify the region for SNR calculation.
            
        Returns:
            The calculated SNR value.
        """
        if mask is None:
            # Create a simple brain mask by thresholding
            mean_data = np.mean(data, axis=-1)
            mask = mean_data > (0.1 * np.max(mean_data))
        
        signal = np.mean(data[mask])
        noise = np.std(data[~mask])
        
        snr = signal / noise if noise != 0 else float('inf')
        return snr
    
    input_dir: str = Path(input_filepath).parent
    input_file_stem: str = Path(input_filepath).stem.split(".")[0]
    bval_file, bvec_file, _ = [os.path.join(input_dir, f"{input_file_stem}{extension}") for extension in [".bval", ".bvec", ".json"]]
    try:
        bvals, bvecs = read_bvals_bvecs(bval_file, bvec_file)
    except Exception as e:
        warn(f"BVAL or BVECS file not found for the given input NIfTI file.: {e}")
        return None, {}, {}, []
    gtab = gradient_table(bvals=bvals, bvecs=bvecs)
    dwi_data, affine = load_nifti(input_filepath)
    
    denoised_data = patch2self(dwi_data, bvals, model='ols')
    denoised_img = nib.Nifti1Image(denoised_data, affine)
    
    # Prepare metrics and output entities
    snr_before = None
    try:
        snr_before = calculate_snr(dwi_data)
    except Exception as e:
        warn(f"Could not calculate SNR before denoising: {e}")
    snr_after = None
    try:
        snr_after = calculate_snr(denoised_data)
    except Exception as e:
        warn(f"Could not calculate SNR after denoising: {e}")

    metrics: dict = {
        "snr_before": float(snr_before) if snr_before is not None else None,
        "snr_after": float(snr_after) if snr_after is not None else None,
    }

    output_entities: dict = {
        "desc": "denoised",
        "suffix": "dwi",
        "extension": ".nii.gz"
    }

    forced_outputs: list = []

    return denoised_img, metrics, output_entities, forced_outputs