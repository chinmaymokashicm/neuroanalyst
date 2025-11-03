from neuroanalyst.analysis.provenance import trace_root_sidecar

from pathlib import Path
import os, json, shutil
from warnings import warn

import numpy as np
from dipy.align.imaffine import AffineRegistration, MutualInformationMetric
from dipy.align.transforms import AffineTransform3D
from dipy.align.imaffine import AffineMap
from dipy.segment.mask import median_otsu
from dipy.core.gradients import gradient_table
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti
from nilearn.plotting import plot_img
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from bids.layout import parse_file_entities
from bids.layout.writing import build_path

def dipy_registration(input_filepath: str):
    """
    Perform affine registration of DWI to T1-weighted image using dipy.
    
    Args:
        input_filepath (str): Path to input DWI NIfTI file.
        
    Returns:
        output_data (nib.Nifti1Image): Registered DWI image in T1 space.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    def register_dwi_to_t1(
        dwi_data,
        dwi_affine,
        bval_path,
        bvec_path,
        reg_affines,       # from DIPY motion_correction (list/array of Nx4x4)
        t1w_data,
        t1w_affine,
        b0_threshold=50
    ):
        """
        Register DWI to T1, resample all DWI volumes, and rotate bvecs properly.

        Returns:
            output_data : 4D array (DWI resampled to T1 space)
            rotated_bvecs : updated b-vectors in final space
            bvals         : unchanged b-values
            affine_registration : DIPY registration object
            R_coreg      : 3x3 rotation from DWI→T1
        """

        # ---------------------------------------------------------
        # 1. Load bvals/bvecs and compute mean b0 for registration
        # ---------------------------------------------------------
        bvals, bvecs = read_bvals_bvecs(bval_path, bvec_path)
        gtab = gradient_table(bvals=bvals, bvecs=bvecs)

        b0_mask = gtab.b0s_mask
        b0_data = dwi_data[..., b0_mask]
        mean_b0 = b0_data.mean(axis=3)

        # Apply median_otsu for robust registration
        mean_b0_masked, _ = median_otsu(mean_b0, vol_idx=None, numpass=4, dilate=2)

        # ---------------------------------------------------------
        # 2. Setup affine registration (b0 -> T1)
        # ---------------------------------------------------------
        nbins = 32
        metric = MutualInformationMetric(nbins=nbins, sampling_proportion=None)
        level_iters = [1000, 500, 100]
        sigmas = [3.0, 1.0, 0.0]
        factors = [4, 2, 1]

        affreg = AffineRegistration(
            metric=metric,
            level_iters=level_iters,
            sigmas=sigmas,
            factors=factors,
        )

        transform = AffineTransform3D()

        affine_registration = affreg.optimize(
            static=t1w_data,
            moving=mean_b0_masked,
            transform=transform,
            params0=None,
            static_grid2world=t1w_affine,
            moving_grid2world=dwi_affine,
        )

        coreg_affine = affine_registration.affine
        A3 = coreg_affine[:3, :3]

        # ---------------------------------------------------------
        # 3. Extract pure rotation R_coreg from potential scale/shear
        # ---------------------------------------------------------
        U, _, Vt = np.linalg.svd(A3)
        R_coreg = U @ Vt
        if np.linalg.det(R_coreg) < 0:
            U[:, -1] *= -1
            R_coreg = U @ Vt

        # ---------------------------------------------------------
        # 4. Handle motion correction rotations - FIX THE SHAPE ISSUE
        # ---------------------------------------------------------
        print(f"reg_affines shape: {reg_affines.shape}")
        print(f"dwi_data shape: {dwi_data.shape}")
        print(f"Number of gradients: {len(bvals)}")
        
        # Fix the reg_affines shape issue
        if reg_affines.shape == (4, dwi_data.shape[3], 4):
            # Reshape from (4, N, 4) to (N, 4, 4)
            reg_affines_reshaped = np.zeros((dwi_data.shape[3], 4, 4))
            for i in range(dwi_data.shape[3]):
                reg_affines_reshaped[i] = reg_affines[:, i, :].T  # Transpose to get proper 4x4
            reg_affines_full = reg_affines_reshaped
            print("Reshaped reg_affines from (4, N, 4) to (N, 4, 4)")
        
        elif reg_affines.shape[0] != dwi_data.shape[3]:
            print(f"Warning: reg_affines has {reg_affines.shape[0]} matrices but DWI has {dwi_data.shape[3]} volumes")
            
            # Option 1: Use identity for missing volumes
            if reg_affines.shape[0] < dwi_data.shape[3]:
                identity_matrices = np.tile(np.eye(4), (dwi_data.shape[3] - reg_affines.shape[0], 1, 1))
                reg_affines_full = np.concatenate([reg_affines, identity_matrices], axis=0)
            else:
                # Truncate if too many
                reg_affines_full = reg_affines[:dwi_data.shape[3]]
        else:
            reg_affines_full = reg_affines

        # Extract rotation matrices
        R_motion = np.array([A[:3, :3] for A in reg_affines_full])  # shape (N,3,3)

        # Combine them: R_total[n] = R_coreg @ R_motion[n]
        R_total = np.einsum("ij,njk->nik", R_coreg, R_motion)

        # ---------------------------------------------------------
        # 5. Rotate bvecs
        # ---------------------------------------------------------
        non_zero_mask = bvals > b0_threshold
        rotated_bvecs = bvecs.copy()

        # Apply rotations only to non-zero bvecs
        rotated_bvecs[non_zero_mask] = np.einsum(
            "nij,nj->ni", R_total[non_zero_mask], bvecs[non_zero_mask]
        )

        # Normalize
        norms = np.linalg.norm(rotated_bvecs[non_zero_mask], axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        rotated_bvecs[non_zero_mask] /= norms

        # ---------------------------------------------------------
        # 6. Resample ALL DWI volumes to T1 space
        # ---------------------------------------------------------
        affine_map = AffineMap(
            coreg_affine,
            t1w_data.shape, t1w_affine,
            mean_b0.shape, dwi_affine
        )

        output_data = np.zeros(t1w_data.shape + (dwi_data.shape[3],))

        for i in range(dwi_data.shape[3]):
            output_data[..., i] = affine_map.transform(dwi_data[..., i])

        return output_data, rotated_bvecs, bvals, affine_registration, R_coreg
    
    
    input_dir: str = Path(input_filepath).parent
    input_file_stem: str = Path(input_filepath).stem.split(".")[0]
    bval_file, bvec_file, json_file = [os.path.join(input_dir, f"{input_file_stem}{extension}") for extension in [".bval", ".bvec", ".json"]]
    pipeline_name: str = os.getenv("PIPELINE_NAME", None)
    pipeline_dir: str = os.path.join("/data", "derivatives", pipeline_name)
    if not pipeline_name:
        raise EnvironmentError("PIPELINE_NAME environment variable is not set.")
    
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
    dwi_data, dwi_affine = load_nifti(input_filepath)
    
    # Get skull-stripped T1w image from FreeSurfer outputs
    t1w_pipeline_name: str = os.getenv("T1W_PIPELINE_NAME", None)
    if not t1w_pipeline_name:
        raise EnvironmentError("T1W_PIPELINE_NAME environment variable is not set.")
    t1w_pipeline_dir: str = os.path.join("/data", "derivatives", t1w_pipeline_name)
    input_entities: dict = parse_file_entities(input_filepath)
    subject_id, session_id = None, None
    if "subject" in input_entities:
        subject_id = input_entities["subject"]
    if "session" in input_entities:
        session_id = input_entities["session"]
    # Get freesurfer subject dir name
    subject_dirname: str = f"{subject_id}"
    if session_id:
        subject_dirname += f"_{session_id}"
    if subject_dirname == "":
        subject_dirname = "unknown_subject"
    freesurfer_subjects_dir: str = os.path.join(t1w_pipeline_dir, "tmp", "freesurfer_subjects", subject_dirname)
    skull_stripped_t1w_path: str = os.path.join(freesurfer_subjects_dir, "mri", "brain.mgz")
    if not os.path.exists(skull_stripped_t1w_path):
        # raise FileNotFoundError(f"Skull-stripped T1w image not found at expected path: {skull_stripped_t1w_path}")
        warn(f"Skull-stripped T1w image not found at expected path: {skull_stripped_t1w_path}. Attempting to find any other T1w image of the subject...")
        same_subject_id_dirnames = [dir_name for dir_name in os.listdir(os.path.join(t1w_pipeline_dir, "tmp", "freesurfer_subjects")) if dir_name.startswith(f"{subject_id}")]
        if len(same_subject_id_dirnames) == 0:
            raise FileNotFoundError(f"No FreeSurfer subject directories found for subject {subject_id} in {os.path.join(t1w_pipeline_dir, 'tmp', 'freesurfer_subjects')}")
        subject_dirname = same_subject_id_dirnames[0]
        freesurfer_subjects_dir = os.path.join(t1w_pipeline_dir, "tmp", "freesurfer_subjects", subject_dirname)
        skull_stripped_t1w_path = os.path.join(freesurfer_subjects_dir, "mri", "brain.mgz")
        if not os.path.exists(skull_stripped_t1w_path):
            raise FileNotFoundError(f"Skull-stripped T1w image still not found at path: {skull_stripped_t1w_path}")
        else:
            print(f"Found skull-stripped T1w image at alternative path: {skull_stripped_t1w_path}")

    t1w_data, t1w_affine = load_nifti(skull_stripped_t1w_path)
    
    # Get reg_affines from previous step's sidecar (if available - should be there if motion correction was done)
    input_sidecar_path: str = input_filepath.replace(".nii.gz", ".nii").replace(".nii", ".json") # Works for both .nii and .nii.gz
    reg_affines: np.ndarray = None
    if os.path.exists(input_sidecar_path):
        try:
            with open(input_sidecar_path, 'r') as f:
                input_sidecar = json.load(f)
            reg_affines_shape: list = input_sidecar.get("metrics", {}).get("reg_affines_shape", None)
            reg_affines_dict: dict = input_sidecar.get("metrics", {}).get("reg_affines", None)
            if reg_affines_dict is not None:
                reg_affines = np.zeros(reg_affines_shape)

                for i in range(reg_affines_shape[0]):
                    for j in range(reg_affines_shape[1]):
                        for k in range(reg_affines_shape[2]):
                            reg_affines[i, j, k] = reg_affines_dict[str(i)][str(j)][str(k)]
                            
                reg_affines = np.transpose(reg_affines, (0, 1, 2))  # Ensure shape is (N,4,4)
                print(f"Loaded reg_affines from sidecar with shape: {reg_affines.shape}")
        except Exception as e:
            print(f"Error reading sidecar JSON file for reg_affines: {e}")
            
    # Get registered DWI, rotated bvecs
    output_data, rotated_bvecs, bvals, affine_registration, R_coreg = register_dwi_to_t1(
        dwi_data,
        dwi_affine,
        bval_file,
        bvec_file,
        reg_affines,
        t1w_data,
        t1w_affine
    )
    
    metrics = {
        "R_coreg": R_coreg.tolist(),
        "affine_registration_matrix": affine_registration.affine.tolist(),
        "registration_method": "Affine",
    }
    
    output_entities = {
        "desc": "registered",
        "suffix": "dwi",
        "extension": ".nii.gz"
    }
    
    # Save bval and bvec files for the registered data
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
        print(f"Saved registered BVAL to: {bval_filepath}")
        
        np.savetxt(bvec_filepath, rotated_bvecs, fmt="%.8f")
        print(f"Saved registered BVECS to: {bvec_filepath}")
    except Exception as e:
        warn(f"Failed to save registered BVAL/BVECS files: {e}")
        
    forced_outputs = []
    
    return output_data, metrics, output_entities, forced_outputs