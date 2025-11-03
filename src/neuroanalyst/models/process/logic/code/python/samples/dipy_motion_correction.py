import shutil
from neuroanalyst.analysis.provenance import trace_root_sidecar

import os, subprocess, json
from pathlib import Path
import traceback
from warnings import warn
from typing import Optional

import nibabel as nib
import numpy as np
import pandas as pd
from dipy.align import motion_correction
from dipy.core.gradients import gradient_table, reorient_bvecs
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti
from dipy.segment.mask import median_otsu
from bids.layout.writing import build_path

def dipy_motion_correction(input_filepath: str):
    """
    Motion current correction using dipy.
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (nibabel.Nifti1Image): NIfTI image of motion-corrected DWI data.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    def extract_motion_metrics(reg_affines: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Decomposes affine matrices into translational and rotational components, 
        and calculates Framewise Displacement (FD).
        
        Args:
            reg_affines: A numpy array of shape (N, 4, 4) containing the affine 
                        transformation matrix for each of the N volumes.
                        
        Returns:
            A tuple of (translations, rotations, fd) arrays.
        """
        n_vols = reg_affines.shape[0]
        
        # 1. Translation (mm)
        # The translation vector is the last column of the affine matrix (index 0, 1, 2)
        # The last row is [0, 0, 0, 1], so we extract the first three components of the 4th column.
        translations = reg_affines[:, :3, 3] # Shape (N, 3)

        # Total displacement (Euclidean distance from the origin) for each volume
        total_translation = np.sqrt(np.sum(translations**2, axis=1))

        # 2. Rotation (degrees)
        # The rotational part is the 3x3 block in the top-left corner.
        rotations_matrix = reg_affines[:, :3, :3] # Shape (N, 3, 3)
        
        roll = np.arctan2(rotations_matrix[:, 2, 1], rotations_matrix[:, 2, 2])
        pitch = np.arctan2(-rotations_matrix[:, 2, 0], np.sqrt(rotations_matrix[:, 2, 1]**2 + rotations_matrix[:, 2, 2]**2))
        yaw = np.arctan2(rotations_matrix[:, 1, 0], rotations_matrix[:, 0, 0])
        
        # Convert to degrees
        rotations = np.vstack([roll, pitch, yaw]).T # Shape (N, 3)
        rotations_deg = np.degrees(rotations)

        # 3. Framewise Displacement (FD)
        # FD combines translation and rotation changes between adjacent volumes.
        # A common convention (Power et al., 2012) is to convert rotations to a translational 
        # equivalent at a 50mm radius.

        # Calculate derivative (volume-to-volume difference) for translations and rotations
        trans_diff = np.diff(translations, axis=0, prepend=translations[0:1])
        rot_diff = np.diff(rotations, axis=0, prepend=rotations[0:1])

        # Convert rotational change to translational change (50mm radius)
        rot_trans_equiv = 50 * np.abs(rot_diff) # Use radians here

        # FD is the sum of the absolute translational changes (x, y, z)
        # and the rotational equivalent translational changes (roll, pitch, yaw)
        fd = np.sum(np.abs(trans_diff), axis=1) + np.sum(rot_trans_equiv, axis=1)

        return translations, rotations_deg, fd
    
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
    pipeline_name: str = os.getenv("PIPELINE_NAME", None)
    if not pipeline_name:
        raise EnvironmentError("PIPELINE_NAME environment variable is not set.")
    pipeline_dir: str = os.path.join("/data", "derivatives", pipeline_name)
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
    
    # Generate brain mask from b0 image
    b0_indices = np.where(bvals < 50)[0]
    b0_ref = int(b0_indices[0])
    b0_data = dwi_data[..., b0_indices]
    b0_mean = np.mean(b0_data, axis=3)
    b0_mask, _ = median_otsu(b0_mean, median_radius=2, numpass=1)
    b0_mask = b0_mask.astype(np.uint8)
    b0_mask = np.where(b0_mask > 0, 1, 0)
    if np.sum(b0_mask) == 0:
        print("Warning: Generated brain mask is empty.")
        b0_mask = None  # Fallback to no mask if empty
    
    # Perform motion correction
    output_data, reg_affines = motion_correction(dwi_data, gtab, affine=affine, b0_ref=b0_ref, static_mask=b0_mask)

    # Extract rotation matrices and compute their inverses
    rot_mats = np.array([reg_aff[:3, :3] for reg_aff in reg_affines])
    
    # Only rotate non-zero bvecs (b > threshold, typically 50)
    b_threshold = 50
    non_zero_mask = bvals > b_threshold
    
    rotated_bvecs = bvecs.copy()
    try:
        if np.any(non_zero_mask):
            # Use rotation matrices directly (NOT inverse)
            R = rot_mats[non_zero_mask]

            rotated_bvecs[non_zero_mask] = np.einsum(
                "nij,nj->ni", R, bvecs[non_zero_mask]
            )

            # Normalize only the non-zero bvecs
            norms = np.linalg.norm(rotated_bvecs[non_zero_mask], axis=1, keepdims=True)
            rotated_bvecs[non_zero_mask] /= norms
    except Exception as e:
        warn(f"Error during bvec rotation: {e}. Using original bvecs.")
        rotated_bvecs = bvecs
    
    # Prepare metrics and output entities
    translations_mm, rotations_deg, fd_mm = extract_motion_metrics(reg_affines)
    max_translation = np.max(np.sqrt(np.sum(translations_mm**2, axis=1)))
    avg_translation = np.mean(np.sqrt(np.sum(translations_mm**2, axis=1)))
    max_rotation = np.max(np.abs(rotations_deg))
    avg_rotation = np.mean(np.abs(rotations_deg))
    max_framewise_displacement = np.max(fd_mm)
    avg_framewise_displacement = np.mean(fd_mm)
    snr_before = calculate_snr(dwi_data)
    snr_after = calculate_snr(output_data.get_fdata())
    
    metrics: dict = {
        "mask_shape": b0_mask.shape if b0_mask is not None else None,
        "mask_sum": int(np.sum(b0_mask)) if b0_mask is not None else None,
        "num_volumes": dwi_data.shape[-1],
        "max_translation_mm": float(max_translation),
        "avg_translation_mm": float(avg_translation),
        "max_rotation_deg": float(max_rotation),
        "avg_rotation_deg": float(avg_rotation),
        "max_framewise_displacement_mm": float(max_framewise_displacement),
        "avg_framewise_displacement_mm": float(avg_framewise_displacement),
        "snr_before": float(snr_before),
        "snr_after": float(snr_after),
        "reg_affines_shape": reg_affines.shape,
        "reg_affines": reg_affines.tolist(),
        "translations_mm": translations_mm.tolist(),
        "rotations_deg": rotations_deg.tolist(),
        "framewise_displacement_mm": fd_mm.tolist()
    }

    output_entities = {
        "desc": "motionCorrected",
        "suffix": "dwi",
        "extension": ".nii.gz"
        }
    
    # Save bval and bvec files for the motion-corrected data
    custom_path_patterns = [
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][acq-{acquisition}_][run-{run}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][task-{task}_][acq-{acquisition}_][ce-{ce}_][dir-{dir}_][rec-{rec}_][run-{run}_][echo-{echo}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][task-{task}_][acq-{acquisition}_][run-{run}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][space-{space}_][hemi-{hemi}_][model-{model}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/][sample-{sample}/]{datatype}/sub-{subject}_[ses-{session}_][sample-{sample}_][desc-{desc}_]{suffix}{extension}",
        "[sub-{subject}/][ses-{session}/][sample-{sample}/][modality-{modality}_]{datatype}/sub-{subject}_[ses-{session}_][sample-{sample}_][modality-{modality}_][desc-{desc}_]{suffix}{extension}"
        ]

    bval_entities = output_entities.copy()
    bval_entities["extension"] = ".bval"

    bvec_entities = output_entities.copy()
    bvec_entities["extension"] = ".bvec"
    
    try:
        bval_filepath = os.path.join(pipeline_dir, build_path(custom_path_patterns, bval_entities))
        bvec_filepath = os.path.join(pipeline_dir, build_path(custom_path_patterns, bvec_entities))

        shutil.copyfile(bval_file, bval_filepath)
        np.savetxt(bvec_filepath, rotated_bvecs.T, fmt="%.8f")
        print(f"Saved motion-corrected BVAL and BVECS to: {bval_filepath}, {bvec_filepath}")
    except Exception as e:
        warn(f"Failed to save motion-corrected BVAL or BVECS files: {e}")

    forced_outputs = []

    return output_data, metrics, output_entities, forced_outputs