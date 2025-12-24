from pathlib import Path
import os, json
from typing import Optional

import numpy as np
import nibabel as nib
from dipy.align.imaffine import AffineMap
from dipy.align.transforms import RigidTransform3D
from dipy.align.imaffine import MutualInformationMetric, AffineRegistration
from dipy.io.gradients import read_bvals_bvecs

def dipy_correct_distortions_and_motion(input_filepath: str):
    """
    Correct motion and eddy current distortions in a DWI image using DIPY.

    Args:
        input_filepath (str): Path to the input DWI NIfTI file.

    Returns:
        output_data (np.ndarray): Corrected DWI image data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
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
            input_dir: str = Path(input_filepath).parent
            input_file_stem: str = Path(input_filepath).stem.split(".")[0]
            if bval_filepath is None:
                inferred_bval = os.path.join(input_dir, f"{input_file_stem}.bval")
                if os.path.exists(inferred_bval):
                    bval_filepath = inferred_bval
            if bvec_filepath is None:
                inferred_bvec = os.path.join(input_dir, f"{input_file_stem}.bvec")
                if os.path.exists(inferred_bvec):
                    bvec_filepath = inferred_bvec
        
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
    except Exception as e:
        print(f"Error reading BVAL or BVECS files: {e}")
        bval, bvec = None, None

    n_volumes = img_data.shape[3]

    # ============================
    # Step 2: Simple Motion Correction
    # ============================
    # Align each volume to the first b0 volume (assumes first volume is b0)
    # Using a simple rigid-body affine registration
    reference_volume = img_data[..., 0]
    corrected_data = np.zeros_like(img_data)

    corrected_data[..., 0] = reference_volume  # reference stays the same

    # Affine registration metric
    metric = MutualInformationMetric(nbins=32, sampling_proportion=None)
    affreg = AffineRegistration(metric=metric, level_iters=[1000, 100, 10], sigmas=[3.0, 1.0, 0.0], factors=[4, 2, 1])

    for i in range(1, n_volumes):
        moving = img_data[..., i]
        transform = affreg.optimize(
            static=reference_volume,
            moving=moving,
            transform=RigidTransform3D(),
            params0=None,
            static_grid2world=None,
            moving_grid2world=None
        )
        corrected_data[..., i] = transform.transform(moving)

    # ============================
    # Step 3: Placeholder for Eddy & Susceptibility
    # ============================
    # For full correction, FSL 'eddy' or 'topup' would be used.
    # Here we only do rigid-body motion correction.

    # ============================
    # Step 4: Prepare Outputs
    # ============================
    # Save bvals and bvecs for reference in downstream processing if needed
    try:
        output_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")
        os.makedirs(output_dir, exist_ok=True)
        input_file_stem: str = "motion_corrected_" + input_filepath.split("/")[-1].split(".")[0]
        bval_filepath, bvec_filepath = save_bval_bvec_files(bval, bvec, output_dir, input_file_stem)
    except Exception as e:
        print(f"Error saving bval and bvec files: {e}")
        bval_filepath, bvec_filepath = None, None
    
    corrected_img = nib.Nifti1Image(corrected_data, affine, header)
    output_data = corrected_img.get_fdata()

    metrics: dict = {
        "correction_method": "motion_rigid_affine",
        "num_volumes": n_volumes,
        "note": "Eddy current and susceptibility corrections are placeholders; full correction requires FSL eddy/topup.",
        "bvecs_updated": False, # In a full implementation, bvecs would be updated based on motion parameters
        "bval_filepath": bval_filepath,
        "bvec_filepath": bvec_filepath,
    }

    output_entities: dict = {
        "suffix": "dwi",
        "desc": "motionCorrected",
    }

    forced_outputs: list = []  # No extra files generated in this simple implementation

    return output_data, metrics, output_entities, forced_outputs
