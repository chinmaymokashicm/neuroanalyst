from neuroanalyst.models.process.logic.core import Metric

import os, json
from pathlib import Path
from typing import Optional

import numpy as np
import nibabel as nib
from dipy.denoise.localpca import mppca
from dipy.io.gradients import read_bvals_bvecs


def dipy_denoise_mppca(input_filepath: str):
    """Apply MP-PCA denoising to a raw DWI image using DIPY.

    Args:
        input_filepath (str): Path to the input DWI nifti file.

    Returns:
        output_data (np.ndarray): Denoising image data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
    """
    def get_input_bval_bvec_paths(sidecar_path: str) -> tuple[Optional[str], Optional[str]]:
        """Retrieve bval and bvec file paths from the sidecar JSON.

        Args:
            sidecar_path (str): Path to the sidecar JSON file.
            
        Returns:
            A tuple containing paths to the bval and bvec files, or None if not found.
        """
        with open(sidecar_path, 'r') as f:
            sidecar_data = json.load(f)
            bval_path = sidecar_data.get("metrics", {}).get("bval_filepath", None)
            bvec_path = sidecar_data.get("metrics", {}).get("bvec_filepath", None)
        if bval_path is not None:
            bval_path = str(Path(sidecar_path).parent / bval_path)
        if bvec_path is not None:
            bvec_path = str(Path(sidecar_path).parent / bvec_path)
        return bval_path, bvec_path
    
    def save_bval_bvec_files(bval: np.ndarray, bvec: np.ndarray, output_dir: str, file_stem: str) -> tuple[str, str]:
        """Save bval and bvec files to the specified output directory.

        Args:
            bval (np.ndarray): Array of b-values.
            bvec (np.ndarray): Array of b-vectors.
            output_dir (str): Directory to save the files.
            file_stem (str): Stem for the output file names.
            
        Returns:
            A tuple containing paths to the saved bval and bvec files.
        """
        bval_filepath = os.path.join(output_dir, f"{file_stem}.bval")
        bvec_filepath = os.path.join(output_dir, f"{file_stem}.bvec")
        np.savetxt(bval_filepath, bval, fmt="%.6f")
        np.savetxt(bvec_filepath, bvec.T, fmt="%.6f")  # Transpose to match expected shape
        return bval_filepath, bvec_filepath
    

    # ============================
    # Step 1: Load Input Data
    # ============================
    DATA_DIR: str = "/data"
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME", None)
    if PIPELINE_NAME is None:
        raise EnvironmentError("PIPELINE_NAME environment variable is not set.")
    img: nib.Nifti1Image = nib.load(input_filepath)
    img_data: np.ndarray = img.get_fdata()
    affine: np.ndarray = img.affine
    header: nib.Nifti1Header = img.header
    
    if img_data.ndim < 4:
        raise ValueError("Input image must be a 4D DWI image.")
    
    input_sidecar_path: str = input_filepath.split(".")[0] + ".json"
    input_bval_filepath, input_bvec_filepath = get_input_bval_bvec_paths(input_sidecar_path)
    if input_bval_filepath is None or input_bvec_filepath is None:
        raise ValueError("BVAL or BVECS file paths not found in sidecar JSON.")
    
    bval, bvec = read_bvals_bvecs(input_bval_filepath, input_bvec_filepath)
    
    # ============================
    # Step 2: Apply MP-PCA Denoising
    # ============================
    denoised_data: np.ndarray = mppca(img_data, patch_radius=2, return_sigma=False)
    denoised_img: nib.Nifti1Image = nib.Nifti1Image(denoised_data, affine, header)
    output_data: np.ndarray = denoised_img.get_fdata()
    
    # ============================
    # Step 3: Prepare Outputs
    # ============================
    # Save bvals and bvecs for reference in downstream processing if needed
    output_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")
    os.makedirs(output_dir, exist_ok=True)
    input_file_stem: str = "denoised_mppca_" + input_filepath.split("/")[-1].split(".")[0]
    bval_filepath, bvec_filepath = save_bval_bvec_files(bval, bvec, output_dir, input_file_stem)
    
    metrics: dict = {
        "denoising_method": "MP-PCA",
        "input_shape": img_data.shape,
        "output_shape": output_data.shape,
        "bval_filepath": bval_filepath,
        "bvec_filepath": bvec_filepath
    }

    output_entities: dict = {
        "suffix": "dwi",
        "desc": "mppcaDenoised",
    }

    forced_outputs: list = [] # No forced outputs in this case

    return output_data, metrics, output_entities, forced_outputs