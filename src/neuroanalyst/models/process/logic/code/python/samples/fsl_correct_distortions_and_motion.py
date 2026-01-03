from pathlib import Path
import os, json, subprocess, traceback, shutil
from typing import Optional

import numpy as np
import nibabel as nib
from dipy.align.imaffine import AffineMap
from dipy.align.transforms import RigidTransform3D
from dipy.align.imaffine import MutualInformationMetric, AffineRegistration
from dipy.io.gradients import read_bvals_bvecs

def fsl_correct_distortions_and_motion(input_filepath: str):
    """
    Correct motion and eddy current distortions in a DWI image using FSL.
    Steps:
        1. Use FSL's eddy tool to correct for eddy currents and motion.
        2. Save corrected image and updated bvals/bvecs.

    Args:
        input_filepath (str): Path to the input DWI NIfTI file.

    Returns:
        output_data (nib.Nifti1Image): Motion and distortion corrected image
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
    # Step 1: Load Input Data
    # ============================
    DATA_DIR: str = "/data"
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME", None)
    if PIPELINE_NAME is None:
        raise EnvironmentError("PIPELINE_NAME environment variable is not set.")
    FSL_IMG_NAME = os.getenv("FSL_IMG_NAME")
    if FSL_IMG_NAME is None:
        raise EnvironmentError("FSL_IMG_NAME environment variable is not set.")
    fsl_img_path = f"/opt/fsl_images/{FSL_IMG_NAME}"  # path to FSL Singularity image inside container
    output_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")  # Temporary directory for bval/bvecs outputs for reference by the next downstream process;
    os.makedirs(output_dir, exist_ok=True)
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
    # Step 2: Eddy & Susceptibility Distortion Correction
    # ============================
    
    # Copy inputs to a temporary directory for FSL processing
    temp_fsl_dir = os.path.join(output_dir, "fsl", os.path.basename(input_filepath).split(".")[0])
    os.makedirs(temp_fsl_dir, exist_ok=True)
    dwi_path = os.path.join(temp_fsl_dir, "dwi.nii.gz")
    nib.save(nib.Nifti1Image(img_data, affine, header), dwi_path)
    fsl_processing_bval_path = os.path.join(temp_fsl_dir, "bvals")
    fsl_processing_bvec_path = os.path.join(temp_fsl_dir, "bvecs")
    if bval is not None and bvec is not None:
        np.savetxt(fsl_processing_bval_path, bval, fmt="%.6f")
        np.savetxt(fsl_processing_bvec_path, bvec.T, fmt="%.6f")  # Transpose to match expected shape
        
    # Minimal required eddy files
    # index.txt: one index per volume
    index_path = os.path.join(temp_fsl_dir, "index.txt")
    with open(index_path, 'w') as f:
        f.write(" ".join(["1"] * n_volumes) + "\n")
    
    # acq.txt: acquisition parameters; here we use a placeholder
    acq_path = os.path.join(temp_fsl_dir, "acq.txt")
    with open(acq_path, 'w') as f:
        f.write("0 1 0 0.05\n")  # Placeholder; in practice, use actual parameters
        
    # Crude brain mask from b0
    mask_path = os.path.join(temp_fsl_dir, "mask.nii.gz")
    
    internal_bash_command = "\n".join([
        ". ${FSLDIR}/etc/fslconf/fsl.sh",
        f"fslroi {dwi_path} {temp_fsl_dir}/b0 0 1",
        f"bet {temp_fsl_dir}/b0 {temp_fsl_dir}/b0_brain -m -f 0.3",
        f"mv {temp_fsl_dir}/b0_brain_mask.nii.gz {mask_path}",
        f"eddy \\",
        f"    --imain={dwi_path} \\",
        f"    --mask={mask_path} \\",
        f"    --acqp={acq_path} \\",
        f"    --index={index_path} \\",
        f"    --bvecs={fsl_processing_bvec_path} \\",
        f"    --bvals={fsl_processing_bval_path} \\",
        f"    --out={temp_fsl_dir}/eddy_corrected"
    ])
    
    
    cmd = [
        "apptainer", "exec",
        fsl_img_path,
        "bash", "-c", internal_bash_command
    ]
    print(f"Running FSL eddy and topup with command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print("FSL Output:", result.stdout)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd,
                output=result.stdout,
                stderr=result.stderr
            )
    except subprocess.CalledProcessError as e:
        print(f"Error during FSL eddy/topup execution: {e}")
        if getattr(e, 'output', None):
            print("Output:", e.output)
        if getattr(e, 'stderr', None):
            print("Errors:", e.stderr)
        traceback.print_exc()
    # ============================
    # Step 3: Prepare Outputs
    # ============================
    try:
        corrected_img: nib.Nifti1Image = nib.load(os.path.join(temp_fsl_dir, "eddy_corrected.nii.gz"))
        output_data = corrected_img.get_fdata()
    except Exception as e:
        print(f"Error loading corrected image: {e}")
        raise e
    
    # Save bvals and bvecs for reference in downstream processing if needed
    try:
        input_file_stem: str = "motion_corrected_" + input_filepath.split("/")[-1].split(".")[0]
        bval_filepath = os.path.join(output_dir, f"{input_file_stem}.bval")
        bvec_filepath = os.path.join(output_dir, f"{input_file_stem}.bvec")
        # Copy updated bvals and bvecs from eddy output to output directory
        corrected_bvec_path = os.path.join(temp_fsl_dir, "eddy_corrected.eddy_rotated_bvecs")
        shutil.copyfile(corrected_bvec_path, bvec_filepath)
        shutil.copyfile(input_bval_filepath, bval_filepath)
    except Exception as e:
        print(f"Error saving bval and bvec files: {e}")
        bval_filepath, bvec_filepath = None, None

    metrics: dict = {
        "correction_method": "FSL Eddy",
        "num_volumes": n_volumes,
        "note": "Eddy correction applied for motion and eddy currents.",
        "bvecs_updated": True,
        "bval_filepath": bval_filepath,
        "bvec_filepath": bvec_filepath,
    }

    output_entities: dict = {
        "suffix": "dwi",
        "desc": "motionCorrected",
        "extension": ".nii.gz"
    }

    forced_outputs: list = []  # No extra files generated in this simple implementation

    return output_data, metrics, output_entities, forced_outputs
