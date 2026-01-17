from neuroanalyst.models.process.logic.core import Metric

import os, subprocess, traceback
from pathlib import Path

import numpy as np
import nibabel as nib
from nilearn import plotting, datasets, masking, image
from nilearn.image import resample_to_img
from sklearn.metrics import jaccard_score, mutual_info_score


def fsl_register_dti_maps_to_mni(input_filepath: str):
    """Register DTI scalar maps (FA, MD, RD, AD) to MNI space using FSL FLIRT.

    Args:
        input_filepath (str): Path to a 4D NIfTI image with channels ordered as
                              [FA, MD, RD, AD].

    Returns:
        output_data (nib.Nifti1Image): 4D NIfTI image registered to MNI space.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): Temporary files/directories to be cleaned up.
    """
    def dice_coefficient(a: np.ndarray, b: np.ndarray) -> float:
        """Compute Dice between two boolean masks."""
        a = a.astype(bool).ravel()
        b = b.astype(bool).ravel()
        inter = np.logical_and(a, b).sum()
        return 2.0 * inter / (a.sum() + b.sum() + 1e-8)

    def compute_mni_overlap(
        img_ni: nib.Nifti1Image,
        mni_resolution: int | float = 2,
        threshold: float | None = None,
    ) -> dict:
        """
        Compute overlap or MI between a 3D NIfTI image and the MNI152 template.
        
        Args:
            img_ni (nib.Nifti1Image): Input 3D NIfTI image.
            mni_resolution (int | float): Resolution of MNI template to use (1, 2, or 3 mm).
            threshold (float | None): If provided, threshold to create a binary mask for overlap metrics.
        Returns:
            dict: Dictionary with 'dice', 'jaccard', and 'mi' values.
        """
        # Load MNI template
        mni_tpl = datasets.load_mni152_template(resolution=mni_resolution)

        # Resample input to MNI template grid
        img_resamp = image.resample_to_img(img_ni, mni_tpl, interpolation="continuous")

        mni_data = mni_tpl.get_fdata()
        img_data = img_resamp.get_fdata()

        # Mutual information between intensities (flattened, non-negative)
        # Quantizes to integers for sklearn mutual_info_score
        img_data = ((img_data - img_data.min()) / (img_data.max() - img_data.min() + 1e-8) * 255).astype(np.uint8)
        mni_data = ((mni_data - mni_data.min()) / (mni_data.max() - mni_data.min() + 1e-8) * 255).astype(np.uint8)
        mi = float(mutual_info_score(mni_data.ravel(), img_data.ravel()))

        # For Dice/Jaccard: build masks
        if threshold is not None:
            img_mask = np.abs(img_data) > threshold
        else:
            img_mask_img = masking.compute_brain_mask(img_resamp)
            img_mask = img_mask_img.get_fdata().astype(bool)

        mni_mask = mni_data > 0

        dice = float(dice_coefficient(img_mask, mni_mask))
        jaccard = float(jaccard_score(mni_mask.ravel(), img_mask.ravel()))
        return {"dice": dice, "jaccard": jaccard, "mi": mi}

    # ============================
    # Step 1: Environment & I/O
    # ============================
    DATA_DIR = "/data"
    PIPELINE_NAME = os.getenv("PIPELINE_NAME")
    if PIPELINE_NAME is None:
        raise EnvironmentError("PIPELINE_NAME environment variable is not set.")

    fsl_img_name = os.getenv("FSL_IMG_NAME")
    if fsl_img_name is None:
        raise EnvironmentError("FSL_IMG_NAME environment variable is not set.")

    fsl_img_path = f"/opt/fsl_images/{fsl_img_name}"
    output_dir = Path(DATA_DIR) / "derivatives" / PIPELINE_NAME / "tmp" / Path(input_filepath).name.split(".")[0]
    output_dir.mkdir(parents=True, exist_ok=True)

    img: nib.Nifti1Image = nib.load(input_filepath)
    img_data: np.ndarray = img.get_fdata()
    affine = img.affine
    header = img.header

    if img_data.ndim != 4 or img_data.shape[-1] != 4:
        raise ValueError(
            "Input image must be 4D with exactly 4 volumes (FA, MD, RD, AD)."
        )

    # ============================
    # Step 2: Save scalar maps explicitly
    # ============================
    scalar_names = ["fa", "md", "rd", "ad"]
    scalar_paths = {}

    for i, name in enumerate(scalar_names):
        path = output_dir / f"{name}.nii.gz"
        nib.save(
            nib.Nifti1Image(img_data[..., i], affine, header),
            path
        )
        scalar_paths[name] = path

    # ============================
    # Step 3: FSL FLIRT registration
    # ============================
    fa2mni_mat = output_dir / "fa2mni.mat"
    temp_output_path = output_dir / "dti_scalars_mni.nii.gz"
    
    internal_bash_command = "\n".join([
        "",
        ". ${FSLDIR}/etc/fslconf/fsl.sh",
        "",
        "MNI_REF=${FSLDIR}/data/standard/MNI152_T1_1mm.nii.gz",
        "",
        "# 1) Estimate transform using FA",
        f"flirt \\",
        f"  -in {scalar_paths['fa']} \\",
        "  -ref $MNI_REF \\",
        f"  -omat {fa2mni_mat} \\",
        f"  -out {output_dir / 'fa_mni.nii.gz'} \\",
        f"  -dof 12 \\",
        f"  -interp trilinear",
        "",
        "# 2) Apply transform to remaining scalars",
        "for scalar in md rd ad; do",
        f"  flirt \\",
        f"    -in {output_dir}/${{scalar}}.nii.gz \\",
        "    -ref $MNI_REF \\",
        "    -applyxfm \\",
        f"    -init {fa2mni_mat} \\",
        f"    -out {output_dir}/${{scalar}}_mni.nii.gz \\",
        "    -interp trilinear",
        "done",
        "",
        "# 3) Merge back into a single 4D image (FA, MD, RD, AD)",
        f"fslmerge -t {temp_output_path} \\",
        f"  {output_dir / 'fa_mni.nii.gz'} \\",
        f"  {output_dir / 'md_mni.nii.gz'} \\",
        f"  {output_dir / 'rd_mni.nii.gz'} \\",
        f"  {output_dir / 'ad_mni.nii.gz'}"
    ])


    try:
        cmd = [
            "apptainer", "exec",
            fsl_img_path,
            "bash", "-c", internal_bash_command
        ]
        print(f"Running FSL FLIRT registration with command: {' '.join(cmd)}")
        # subprocess.run(cmd, check=True)
        # Capture output for debugging
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print("FSL FLIRT Output:", result.stdout)
        if result.stderr:
            print("FSL FLIRT Errors:", result.stderr)
        print("FSL FLIRT registration completed successfully.")
    except Exception as e:
        print(f"Error during FSL FLIRT registration: {e}")
        print(traceback.format_exc())
        raise RuntimeError(f"FSL FLIRT registration failed: {e}")

    # ============================
    # Step 4: Load output & return
    # ============================
    output_data: nib.Nifti1Image = nib.load(str(temp_output_path))
    img_data: np.ndarray = output_data.get_fdata()
    # Compute overlap metrics for FA map
    fa_mni_img = nib.Nifti1Image(img_data[..., 0], output_data.affine, output_data.header)
    try:
        dice_fa = compute_mni_overlap(fa_mni_img, mni_resolution=1, threshold=0.2, metric="dice")
    except ValueError as ve:
        print(f"Skipping Dice computation for FA map: {ve}")
        dice_fa = None
    try:
        jaccard_fa = compute_mni_overlap(fa_mni_img, mni_resolution=1, threshold=0.2, metric="jaccard")
    except ValueError as ve:
        print(f"Skipping Jaccard computation for FA map: {ve}")
        jaccard_fa = None
    try:
        mi_fa = compute_mni_overlap(fa_mni_img, mni_resolution=1, metric="mi")
    except ValueError as ve:
        print(f"Skipping MI computation for FA map: {ve}")
        mi_fa = None

    metrics = {
        "registration_tool": "FSL FLIRT",
        "reference_space": "MNI152_T1_1mm",
        "input_shape": img_data.shape,
        "output_shape": output_data.shape,
        "reference_scalar": "FA",
        "fa_dice_with_mni": dice_fa,
        "fa_jaccard_with_mni": jaccard_fa,
        "fa_mi_with_mni": mi_fa,
    }

    output_entities: dict = {
        "suffix": "map",
        "desc": "registeredToMNI",
        "extension": ".nii.gz",
    }

    forced_outputs = [str(output_dir)]

    return output_data, metrics, output_entities, forced_outputs
