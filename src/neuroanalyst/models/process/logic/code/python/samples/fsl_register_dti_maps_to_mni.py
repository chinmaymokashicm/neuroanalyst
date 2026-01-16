from neuroanalyst.models.process.logic.core import Metric

import os
import subprocess
from pathlib import Path

import numpy as np
import nibabel as nib


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
    output_dir = Path(DATA_DIR) / "derivatives" / PIPELINE_NAME / "tmp"
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
        "set -e",
        "",
        ". ${FSLDIR}/etc/fslconf/fsl.sh",
        "",
        "MNI_REF=${FSLDIR}/data/standard/MNI152_T1_1mm.nii.gz",
        "",
        "# 1) Estimate transform using FA",
        f"flirt \\",
        f"  -in {scalar_paths['fa']} \\",
        f"  -ref $MNI_REF \\",
        f"  -omat {fa2mni_mat} \\",
        f"  -out {output_dir / 'fa_mni.nii.gz'} \\",
        f"  -dof 12 \\",
        f"  -interp trilinear",
        "",
        "# 2) Apply transform to remaining scalars",
        "for scalar in md rd ad; do",
        f"  flirt \\",
        f"    -in {output_dir}/${{scalar}}.nii.gz \\",
        f"    -ref $MNI_REF \\",
        f"    -applyxfm \\",
        f"    -init {fa2mni_mat} \\",
        f"    -out {output_dir}/${{scalar}}_mni.nii.gz \\",
        f"    -interp trilinear",
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
        subprocess.run(cmd, check=True)
        print("FSL FLIRT registration completed successfully.")
    except Exception as e:
        raise RuntimeError(f"FSL FLIRT registration failed: {e}")

    # ============================
    # Step 4: Load output & return
    # ============================
    output_data: nib.Nifti1Image = nib.load(str(temp_output_path))

    metrics = {
        "registration_tool": "FSL FLIRT",
        "reference_space": "MNI152_T1_1mm",
        "input_shape": img_data.shape,
        "output_shape": output_data.shape,
        "reference_scalar": "FA",
    }

    output_entities: dict = {
        "suffix": "map",
        "desc": "registeredToMNI",
        "extension": ".nii.gz",
    }

    forced_outputs = [str(output_dir)]

    return output_data, metrics, output_entities, forced_outputs
