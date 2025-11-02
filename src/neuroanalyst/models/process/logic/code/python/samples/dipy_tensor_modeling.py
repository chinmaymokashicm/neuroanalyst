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
from dipy.reconst.dti import TensorModel

def dipy_tensor_modeling(input_filepath: str):
    """
    Diffusion Tensor Modeling using dipy.
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (np.ndarray): Array of diffusion tensor maps. 
            Shape will be (X, Y, Z, 6) where the last dimension corresponds to 
            [FA, MD, AD, RD, ColorFA, Trace].
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
    
    tensor_model = TensorModel(gtab, fit_method="WLS")
    tensor_fit = tensor_model.fit(dwi_data)

    # Extract diffusion tensor metrics
    fa = tensor_fit.fa
    md = tensor_fit.md
    ad = tensor_fit.ad
    rd = tensor_fit.rd
    color_fa = tensor_fit.color_fa
    trace = tensor_fit.trace

    # Stack the metrics into a single 4D array
    output_data = np.stack([fa, md, ad, rd, color_fa[..., 0], trace], axis=-1)

    metrics = {
        "mean_fa": float(np.mean(fa)),
        "std_fa": float(np.std(fa)),
        "mean_md": float(np.mean(md)),
        "std_md": float(np.std(md)),
        "mean_ad": float(np.mean(ad)),
        "std_ad": float(np.std(ad)),
        "mean_rd": float(np.mean(rd)),
        "std_rd": float(np.std(rd)),
        "mean_trace": float(np.mean(trace)),
        "std_trace": float(np.std(trace)),
    }

    output_entities = {
        "desc": "tensor",
        "suffix": "dwi",
        "extension": ".nii.gz"
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs