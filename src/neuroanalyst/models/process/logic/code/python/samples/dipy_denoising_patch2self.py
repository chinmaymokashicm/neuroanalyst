import os, subprocess, json
from pathlib import Path
import traceback
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
    bval_file, bvec_file, json_file = [os.path.join(input_dir, f"{input_file_stem}{extension}") for extension in [".bval", ".bvec", ".json"]]
    bvals, bvecs = read_bvals_bvecs(bval_file, bvec_file)
    gtab = gradient_table(bvals=bvals, bvecs=bvecs)
    dwi_data, affine = load_nifti(input_filepath)
    
    denoised_data = patch2self(dwi_data, bvals, model='ols')
    denoised_img = nib.Nifti1Image(denoised_data, affine)
    denoised_img.to_filename("denoised_dwi.nii.gz")
    
    # Prepare metrics and output entities
    snr_before = calculate_snr(dwi_data)
    snr_after = calculate_snr(denoised_data)
    
    metrics: dict = {
        "num_volumes": dwi_data.shape[-1],
        "snr_before": float(snr_before),
        "snr_after": float(snr_after),
    }

    output_entities: dict = {
        "desc": "denoised",
        "suffix": "dwi",
        "extension": ".nii.gz"
    }

    forced_outputs: list = []

    return denoised_img, metrics, output_entities, forced_outputs