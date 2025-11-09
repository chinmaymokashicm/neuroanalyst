from neuroanalyst.models.process.logic.core import Metric
from neuroanalyst.analysis.provenance import trace_root_sidecar

import os, subprocess, json
from pathlib import Path
import traceback
from warnings import warn
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
    try:
        bvals, bvecs = read_bvals_bvecs(bval_file, bvec_file)
    except Exception as e:
        warn(f"BVAL or BVECS file not found for the given input NIfTI file.: {e}. Attempting to find root file via sidecar tracing...")
        root_sidecar_path = trace_root_sidecar(os.path.join(input_dir, f"{input_file_stem}.json"))
        root_bval_file = str(Path(root_sidecar_path).parent / (Path(root_sidecar_path).stem.split(".")[0] + ".bval"))
        root_bvec_file = str(Path(root_sidecar_path).parent / (Path(root_sidecar_path).stem.split(".")[0] + ".bvec"))
        try:
            bvals, bvecs = read_bvals_bvecs(root_bval_file, root_bvec_file)
            print(f"Successfully read BVAL and BVECS from root sidecar files: {root_bval_file}, {root_bvec_file}")
        except Exception as e:
            warn(f"Failed to read BVAL or BVECS from root sidecar files as well: {e}")
            return None, {}, {}, []
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
        "mean_fa": Metric(
            value=float(np.mean(fa)),
            description="Mean fractional anisotropy across the brain"
        ),
        "std_fa": Metric(
            value=float(np.std(fa)),
            description="Standard deviation of fractional anisotropy"
        ),
        "mean_md": Metric(
            value=float(np.mean(md)),
            unit="mm²/s",
            description="Mean diffusivity across the brain"
        ),
        "std_md": Metric(
            value=float(np.std(md)),
            unit="mm²/s",
            description="Standard deviation of mean diffusivity"
        ),
        "mean_ad": Metric(
            value=float(np.mean(ad)),
            unit="mm²/s",
            description="Mean axial diffusivity across the brain"
        ),
        "std_ad": Metric(
            value=float(np.std(ad)),
            unit="mm²/s",
            description="Standard deviation of axial diffusivity"
        ),
        "mean_rd": Metric(
            value=float(np.mean(rd)),
            unit="mm²/s",
            description="Mean radial diffusivity across the brain"
        ),
        "std_rd": Metric(
            value=float(np.std(rd)),
            unit="mm²/s",
            description="Standard deviation of radial diffusivity"
        ),
        "mean_trace": Metric(
            value=float(np.mean(trace)),
            unit="mm²/s",
            description="Mean trace of the diffusion tensor"
        ),
        "std_trace": Metric(
            value=float(np.std(trace)),
            unit="mm²/s",
            description="Standard deviation of trace"
        ),
        "channels": [
            Metric(value="FA", description="Fractional Anisotropy"),
            Metric(value="MD", description="Mean Diffusivity"),
            Metric(value="AD", description="Axial Diffusivity"),
            Metric(value="RD", description="Radial Diffusivity"),
            Metric(value="ColorFA", description="Color-coded FA"),
            Metric(value="Trace", description="Trace of the diffusion tensor")
        ],
        "fit_parameters": Metric(
            value={"method": "WLS"},
            description="Parameters used for tensor fitting"
        )
    }

    output_entities = {
        "desc": "tensor",
        "suffix": "dwi",
        "extension": ".nii.gz"
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs