from neuroanalyst.models.process.logic.core import Metric

import os, json, traceback
from pathlib import Path
from typing import Optional

import numpy as np
import nibabel as nib
from dipy.io.gradients import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from dipy.reconst.dti import TensorModel


def dti_tensor_fit(input_filepath: str):
    """Fit a diffusion tensor model and output scalar maps plus full tensor information.

    The stacked scalar maps are the canonical reference output.
    The full tensor eigenvalues are saved separately as a forced output.

    Args:
        input_filepath (str): Path to the DWI NIfTI file.

    Returns:
        output_data (nib.Nifti1Image): Stacked scalar maps (FA, MD, RD, AD).
        metrics (dict): Summary metrics.
        output_entities (dict): BIDS entities.
        forced_outputs (list): Paths to full tensor representations.
    """
    def get_input_bval_bvec_paths(sidecar_path: str, input_filepath: str) -> tuple[Optional[str], Optional[str]]:
        """Retrieve bval and bvec file paths from the sidecar JSON. If not found, infer from input filepath.

        Args:
            sidecar_path (str): Path to the sidecar JSON file.
            
        Returns:
            A tuple containing paths to the bval and bvec files, or None if not found.
        """
        bval_filepath, bvec_filepath = None, None
        try:
            with open(sidecar_path, 'r') as f:
                sidecar_data = json.load(f)
            bval_filepath = sidecar_data.get("metrics", {}).get("bval_filepath", None)
            bvec_filepath = sidecar_data.get("metrics", {}).get("bvec_filepath", None)
        except Exception as e:
            print(f"Error reading sidecar JSON: {e}. Attempting to infer from input filepath.")
        
        # If not found in sidecar, infer from input filepath
        if bval_filepath is None or bvec_filepath is None:
            input_dir: str = os.path.dirname(input_filepath)
            input_file_stem: str = os.path.basename(input_filepath).split(".")[0]
            if bval_filepath is None:
                inferred_bval = os.path.join(input_dir, f"{input_file_stem}.bval")
                if os.path.exists(inferred_bval):
                    bval_filepath = inferred_bval
            if bvec_filepath is None:
                inferred_bvec = os.path.join(input_dir, f"{input_file_stem}.bvec")
                if os.path.exists(inferred_bvec):
                    bvec_filepath = inferred_bvec
                    
        print(f"Using BVAL file: {bval_filepath}")
        print(f"Using BVECS file: {bvec_filepath}")
        
        return bval_filepath, bvec_filepath
    
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
    # Step 1: Load Data
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
    input_bval_filepath, input_bvec_filepath = get_input_bval_bvec_paths(input_sidecar_path, input_filepath)
    if input_bval_filepath is None or input_bvec_filepath is None:
        print("Bval or Bvec file paths not found in sidecar JSON or inferred from input filepath.")

    try:
        bval, bvec = read_bvals_bvecs(input_bval_filepath, input_bvec_filepath)
        gtab = gradient_table(bval, bvec)
    except Exception as e:
        print(f"Error reading BVAL or BVECS files: {e}")
        print("Cannot proceed with tensor fitting without valid gradient information. Exiting gracefully.")
        print(traceback.format_exc())
        return None, {}, {}, []

    # ============================
    # Step 2: Fit Tensor Model
    # ============================
    tenmodel = TensorModel(gtab)
    mask = img_data[..., 0] > 0
    tenfit = tenmodel.fit(img_data, mask=mask)
    
    # Scalar maps (canonical output)
    fa = tenfit.fa
    md = tenfit.md
    rd = tenfit.rd
    ad = tenfit.ad
    
    output_data = np.stack([fa, md, rd, ad], axis=-1)

    # ============================
    # Step 3: Prepare Outputs
    # ============================
    # Full tensor representation
    try:
        output_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")
        os.makedirs(output_dir, exist_ok=True)
        input_file_stem: str = "dti_fit_" + input_filepath.split("/")[-1].split(".")[0]
        bval_filepath, bvec_filepath = save_bval_bvec_files(bval, bvec, output_dir, input_file_stem)
    except Exception as e:
        print(f"Error saving tensor representation or bval/bvec files: {e}")
        bval_filepath, bvec_filepath = None, None
    
    try:
        tensor_path = os.path.join(output_dir, f"{input_file_stem}_tensor_evals.npz")
        np.savez_compressed(
            tensor_path,
            evals=tenfit.evals,
            affine=affine
        )
    except Exception as e:
        print(f"Error saving tensor eigenvalues: {e}")
        tensor_path = None

    metrics = {
        "mean_fa": Metric(
            name="mean_fa",
            value=float(np.nanmean(fa)),
            unit=None,
            description="Mean Fractional Anisotropy (FA) across the brain volume."
        ),
        "mean_md": Metric(
            name="mean_md",
            value=float(np.nanmean(md)),
            unit="mm^2/s",
            description="Mean Diffusivity (MD) across the brain volume."
        ),
        "mean_rd": Metric(
            name="mean_rd",
            value=float(np.nanmean(rd)),
            unit="mm^2/s",
            description="Mean Radial Diffusivity (RD) across the brain volume."
        ),
        "mean_ad": Metric(
            name="mean_ad",
            value=float(np.nanmean(ad)),
            unit="mm^2/s",
            description="Mean Axial Diffusivity (AD) across the brain volume."
        ),
        "std_fa": Metric(
            name="std_fa",
            value=float(np.nanstd(fa)),
            unit=None,
            description="Standard Deviation of Fractional Anisotropy (FA)."
        ),
        "std_md": Metric(
            name="std_md",
            value=float(np.nanstd(md)),
            unit="mm^2/s",
            description="Standard Deviation of Mean Diffusivity (MD)."
        ),
        "std_rd": Metric(
            name="std_rd",
            value=float(np.nanstd(rd)),
            unit="mm^2/s",
            description="Standard Deviation of Radial Diffusivity (RD)."
        ),
        "std_ad": Metric(
            name="std_ad",
            value=float(np.nanstd(ad)),
            unit="mm^2/s",
            description="Standard Deviation of Axial Diffusivity (AD)."
        ),
        "tensor_representation": "eigenvalues_only",
        "bval_filepath": bval_filepath,
        "bvec_filepath": bvec_filepath,
        "tensor_filepath": tensor_path,
        "fa_shape": output_data[..., 0].shape,
        "md_shape": output_data[..., 1].shape,
        "rd_shape": output_data[..., 2].shape,
        "ad_shape": output_data[..., 3].shape,
    }

    output_entities = {
        "suffix": "dwi",
        "desc": "dtiFit",
        "extension": ".nii.gz"
    }

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs
