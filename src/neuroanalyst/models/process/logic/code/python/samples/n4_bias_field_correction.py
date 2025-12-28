import os, json
from pathlib import Path
from typing import Optional

import numpy as np
import SimpleITK as sitk
import nibabel as nib
from dipy.io.gradients import read_bvals_bvecs


def n4_bias_field_correction(input_filepath: str):
    """Apply N4 Bias Field Correction to a 3D or 4D image using SimpleITK.

    Args:
        input_filepath (str): Path to the input nifti file.

    Returns:
        output_data (np.ndarray): Bias-field corrected image data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant. These will be deleted.
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

    # ============================
    # Step 1: Load Input Data
    # ============================
    DATA_DIR: str = "/data"
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME", None)
    if PIPELINE_NAME is None:
        raise EnvironmentError("PIPELINE_NAME environment variable is not set.")
    img: nib.Nifti1Image = nib.load(input_filepath)
    img_data: np.ndarray = img.get_fdata()
    
    # ============================
    # Step 2: Apply N4 Bias Field Correction
    # ============================
    if img_data.ndim == 4:
        # Apply N4 correction on each volume separately
        output_data = np.zeros_like(img_data)
        for i in range(img_data.shape[3]):
            sitk_img = sitk.GetImageFromArray(img_data[..., i])
            n4_corrector = sitk.N4BiasFieldCorrectionImageFilter()
            corrected_sitk_img = n4_corrector.Execute(sitk_img)
            output_data[..., i] = sitk.GetArrayFromImage(corrected_sitk_img)
    else:
        sitk_img = sitk.GetImageFromArray(img_data)
        n4_corrector = sitk.N4BiasFieldCorrectionImageFilter()
        corrected_sitk_img = n4_corrector.Execute(sitk_img)
        output_data = sitk.GetArrayFromImage(corrected_sitk_img)
        
    input_sidecar_path: str = input_filepath.split(".")[0] + ".json"
    input_bval_filepath, input_bvec_filepath = get_input_bval_bvec_paths(input_sidecar_path, input_filepath)
    if input_bval_filepath is None or input_bvec_filepath is None:
        print("Bval or Bvec file paths not found in sidecar JSON or inferred from input filepath.")
    
    try:
        bval, bvec = read_bvals_bvecs(input_bval_filepath, input_bvec_filepath)
    except Exception as e:
        print(f"Error reading BVAL or BVECS files: {e}")
        bval, bvec = None, None

    # ============================
    # Step 3: Prepare Outputs
    # ============================
    # Save bvals and bvecs for reference in downstream processing if needed
    try:
        output_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")
        os.makedirs(output_dir, exist_ok=True)
        input_file_stem: str = "n4corrected_" + input_filepath.split("/")[-1].split(".")[0]
        bval_filepath, bvec_filepath = save_bval_bvec_files(bval, bvec, output_dir, input_file_stem)
    except Exception as e:
        print(f"Error saving bval and bvec files: {e}")
        bval_filepath, bvec_filepath = None, None
        
    metrics: dict = {
        "correction_method": "N4 Bias Field Correction",
        "input_shape": img_data.shape,
        "output_shape": output_data.shape,
        "bval_filepath": bval_filepath,
        "bvec_filepath": bvec_filepath,
    }

    output_entities: dict = {
        "suffix": "dwi",
        "desc": "n4corrected",
        "extension": ".nii.gz"
    }

    forced_outputs: list = [] # Placeholder for forced outputs

    return output_data, metrics, output_entities, forced_outputs