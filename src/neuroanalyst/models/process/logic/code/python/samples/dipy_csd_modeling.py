"""
! Not fully implemented yet, do not use.
Constrained Spherical Deconvolution (CSD) Modeling using dipy.
"""

import os, subprocess, json
from pathlib import Path
import traceback
from typing import Optional

import nibabel as nib
import numpy as np
import pandas as pd
from dipy.core.gradients import gradient_table
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti
from dipy.reconst.csdeconv import auto_response_ssst, ConstrainedSphericalDeconvModel
from dipy.direction import peaks_from_model

def dipy_csd_modeling(input_filepath: str):
    """
    Constrained Spherical Deconvolution (CSD) Modeling using dipy.
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (np.ndarray): Array of CSD peaks data. 
            Shape will be (X, Y, Z, 3) where the last dimension corresponds to 
            [peak1, peak2, peak3].
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    input_dir: str = Path(input_filepath).parent
    input_file_stem: str = Path(input_filepath).stem.split(".")[0]
    bval_file, bvec_file, json_file = [os.path.join(input_dir, f"{input_file_stem}{extension}") for extension in [".bval", ".bvec", ".json"]]
    bvals, bvecs = read_bvals_bvecs(bval_file, bvec_file)
    gtab = gradient_table(bvals=bvals, bvecs=bvecs)
    dwi_data, affine = load_nifti(input_filepath)

    response, ratio = auto_response_ssst(gtab, dwi_data, roi_radius=10, fa_thr=0.7)
    csd_model = ConstrainedSphericalDeconvModel(gtab, response)
    csd_fit = csd_model.fit(dwi_data)

    peaks = peaks_from_model(model=csd_model, data=dwi_data, sphere=None, relative_peak_threshold=0.5, min_separation_angle=25, mask=None, return_sh=True)
    output_data = peaks.peak_dirs

    metrics = {
        "mean_peak1": float(np.mean(output_data[..., 0])),
        "mean_peak2": float(np.mean(output_data[..., 1])),
        "mean_peak3": float(np.mean(output_data[..., 2])),
    }

    output_entities = {
        "desc": "csd",
        "suffix": "dwi",
        "extension": ".nii.gz"
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs