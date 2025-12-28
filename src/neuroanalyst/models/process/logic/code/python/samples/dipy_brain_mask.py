import os, json
from pathlib import Path
from typing import Optional

import nibabel as nib
import numpy as np
from dipy.segment.mask import median_otsu
from dipy.io.gradients import read_bvals_bvecs

def dipy_brain_mask(input_filepath: str):
    """
    Apply brain masking to a DWI image using DIPY median_otsu.

    Args:
        input_filepath (str): Path to the input DWI NIfTI file.

    Returns:
        output_data (np.ndarray): Brain-masked DWI image data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of extra outputs (e.g., mask file).
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
                bval_info = sidecar_data.get("DWI", {}).get("bval", None)
                bvec_info = sidecar_data.get("DWI", {}).get("bvec", None)
                if bval_info and "value" in bval_info:
                    bval_filepath = bval_info["value"]
                if bvec_info and "value" in bvec_info:
                    bvec_filepath = bvec_info["value"]
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
    # ----------------------------
    # Load data
    # ----------------------------
    DATA_DIR: str = "/data"
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME", None)
    if PIPELINE_NAME is None:
        raise EnvironmentError("PIPELINE_NAME environment variable is not set.")
    img = nib.load(input_filepath)
    data = img.get_fdata()
    affine = img.affine
    header = img.header

    if data.ndim < 4:
        raise ValueError("Input image must be 4D DWI data.")
    
    input_sidecar_path: str = input_filepath.split(".")[0] + ".json"
    input_bval_filepath, input_bvec_filepath = get_input_bval_bvec_paths(input_sidecar_path, input_filepath)
    if input_bval_filepath is None or input_bvec_filepath is None:
        print("Bval or Bvec file paths not found in sidecar JSON or inferred from input filepath.")
    
    try:
        bval, bvec = read_bvals_bvecs(input_bval_filepath, input_bvec_filepath)
    except Exception as e:
        print(f"Error reading BVAL or BVECS files: {e}")
        bval, bvec = None, None

    # ----------------------------
    # Compute mean b0 (assume first volume)
    # ----------------------------
    b0 = data[..., 0]

    # ----------------------------
    # Median Otsu masking
    # ----------------------------
    masked_b0, mask = median_otsu(
        b0,
        vol_idx=None,
        median_radius=4,
        numpass=4,
        autocrop=False
    )

    # Apply mask to all volumes
    output_data = data * mask[..., np.newaxis]

    # ----------------------------
    # Outputs
    # ----------------------------
    # Save bvals and bvecs for reference in downstream processing if needed
    try:
        output_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")
        os.makedirs(output_dir, exist_ok=True)
        input_file_stem: str = "brain_masked_" + input_filepath.split("/")[-1].split(".")[0]
        bval_filepath, bvec_filepath = save_bval_bvec_files(bval, bvec, output_dir, input_file_stem)
    except Exception as e:
        print(f"Error saving bval and bvec files: {e}")
        bval_filepath, bvec_filepath = None, None
        
    metrics = {
        "masking_method": "median_otsu",
        "mask_shape": mask.shape,
        "num_volumes": data.shape[3],
        "bval_filepath": bval_filepath,
        "bvec_filepath": bvec_filepath,
    }

    output_entities = {
        "suffix": "dwi",
        "desc": "brainMasked",
        "extension": ".nii.gz"
    }

    forced_outputs = []  # mask could be saved later if desired

    return output_data, metrics, output_entities, forced_outputs
