import os
import subprocess
from pathlib import Path

import nibabel as nib
import numpy as np

def fsl_fast(input_filepath: str):
    """
    Tissue Segmentation using FSL FAST. (https://web.mit.edu/fsl_v5.0.10/fsl/doc/wiki/FAST.html)
    Runs FSL FAST inside the provided FSL Singularity image.
    Assumptions-
    - The path of the FSL Singularity image is mounted to /opt/fsl in the container
    - The name of the image is passed via the FSL_IMG_NAME environment variable.
    - Apptainer/Singularity is available in the container.
    - All the required parameters are passed via environment variables.
      If not provided, default values will be used.
    Output will be eventually saved as a stacked Nifti file with multiple channels,
    each channel corresponding to a tissue type (CSF, GM, WM.), HMRF segmentation, mixeltype, and restored image.
    
    Args:
        input_filepath (str): Path to input NIfTI file. Takes the array of brain-extracted image and brain mask as input. 
            Shape should be (X, Y, Z, 2), where the last dimension corresponds to [brain, brain_mask].
    Returns:
        output_data (np.ndarray): Array of segmented tissue image data arrays [CSF, GM, WM, seg, mixeltype, restored].
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    
    # Step 1: Prepare environment and paths
    n_channels: int = int(os.getenv("N_CHANNELS", "1"))  # number of input channels
    image_type: int = int(os.getenv("IMAGE_TYPE", "1"))  # 1=T1, 2=T2, 3=PD
    n_classes: int = int(os.getenv("N_CLASSES", "3"))  # number of tissue-type classes
    hyper: float = float(os.getenv("HYPER", "0.1"))  # spatial smoothness
    iter: int = int(os.getenv("ITER", "4"))  # number of main iterations
    lowpass: float = float(os.getenv("LOWPASS", "20.0"))  # lowpass filter (FWHM) in mm
    
    DATA_DIR = "/data"  # shared data dir bind
    fsl_img_name = os.getenv("FSL_IMG_NAME")
    fsl_img_path = f"/opt/fsl_images/{fsl_img_name}"  # path to FSL Singularity image inside container
    
    output_dir = f"/tmp/"

    # Step 2: Define output file paths - this is necessary because FAST creates multiple outputs automatically.
    # These outputs will then be deleted by the NeuroAnalyst wrapper.
    # We need to pass the actual output data to the NeuroAnalyst wrapper, so that it can be saved correctly with exhaustive metadata.
    
    # Load brain-extracted image and save it temporarily. Use this temporary file as input to FAST.
    img = nib.load(input_filepath)
    img_data = img.get_fdata()
    if img_data.ndim != 4 or img_data.shape[3] != n_channels:
        raise ValueError(f"Input NIfTI file must be a 4D file with {n_channels} channels.")
    brain_data = img_data[:, :, :, 0]  # assuming first channel is brain
    brain_mask = img_data[:, :, :, 1]  # assuming second channel is brain mask
    if not (brain_mask > 0).any():
        raise ValueError("Brain mask contains no non-zero values.")
    input_filename = input_filepath.split("/")[-1]
    brain_temp_path = os.path.join(output_dir, input_filename.replace(".nii.gz", "_brain_temp.nii.gz"))
    nib.save(nib.Nifti1Image(brain_data, img.affine, img.header), brain_temp_path)

    input_filename_stem: str = brain_temp_path.split("/")[-1].replace(".nii.gz", "")
    output_filename_stem: str = input_filename_stem + "_FSL_FAST"
    output_basename: str = str(Path(output_dir) / output_filename_stem)
    
    # Step 3: Build and run the Apptainer/Singularity command. This runs FSL FAST inside an Apptainer container.
    internal_bash_command: str = f"""
. ${{FSLDIR}}/etc/fslconf/fsl.sh
fast -t {image_type} -n {n_classes} -H {hyper} -I {iter} -l {lowpass} -B -o {output_basename} {brain_temp_path}
    """
    cmd = [
        "apptainer", "exec",
        fsl_img_path,
        "bash", "-c", internal_bash_command
    ]
    print(f"Running command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, check=True)
    print(f"FSL FAST command finished with return code {result.returncode}")
    
    print(f"=== Command Output ===\n{result.stdout}\n===================")
    print(result.stdout)
    
    print(f"=== Command Error (if any) ===\n{result.stderr}\n===================")
    print(result.stderr)
    
    # Step 4: Load output data and prepare return values
    # This is necessary because the NeuroAnalyst wrapper expects the output data to be returned from this function.
    # The wrapper will then save the data to the appropriate NeuroAnalyst-compliant location with metadata.
    # Load all tissue probability maps (pve_0, pve_1, pve_2, etc.), HMRF segmentation, mixeltype, and restored image.
    # Stack all these maps into a single array with shape (X, Y, Z, n_classes + 2)
    # where the last dimension corresponds to different tissue types and segmentations.
    # The NeuroAnalyst wrapper will then save this stacked array as a multi-channel Nifti file.
    # Sequence of outputs: CSF, GM, WM, HMRF segmentation, mixeltype, restored image/bias-corrected image.
    tissue_data_list = []
    tissue_file_suffixes: list[str] = [f"_pve_{i}" for i in range(0, n_classes)] + ["_seg", "_mixeltype", "_restore"]
    
    for suffix in tissue_file_suffixes:
        filepath = f"{output_basename}{suffix}.nii.gz"
        data = nib.load(filepath).get_fdata()
        print(f"Loaded tissue data from {filepath} with shape {data.shape}")
        tissue_data_list.append(data)
    output_data = np.stack(tissue_data_list, axis=-1)  # shape will be (X, Y, Z, n_classes + 2)
    print(f"Stacked output data shape: {output_data.shape}")

    # Compute volume metrics for each tissue type
    # Compute SNR (Signal-to-Noise Ratio) -> mean signal (within brain mask) / std of background (outside brain mask) of the restored image
    # Assuming the restored image is the last channel in output_data
    brain_mask = output_data[..., 0] > 0  # CSF mask
    background_mask = ~brain_mask
    snr = output_data[..., -1][brain_mask].mean() / output_data[..., -1][background_mask].std() if background_mask.any() else 0
    
    # Compute CNR (Contrast-to-Noise Ratio) -> |mean GM - mean WM| / std of background (outside brain mask)
    if n_classes >= 3:
        gm_mask = output_data[..., 1] > 0  # GM mask
        wm_mask = output_data[..., 2] > 0  # WM mask
        mean_gm = output_data[..., -1][gm_mask].mean() if gm_mask.any() else 0
        mean_wm = output_data[..., -1][wm_mask].mean() if wm_mask.any() else 0
        cnr = abs(mean_gm - mean_wm) / output_data[..., -1][background_mask].std() if background_mask.any() else 0
    else:
        cnr = 0

    metrics: dict = {
        "shape": output_data.shape,
        "csf_volume": int((output_data[..., 0] > 0).sum()) if n_classes > 0 else 0,
        "gm_volume": int((output_data[..., 1] > 0).sum()) if n_classes > 1 else 0,
        "wm_volume": int((output_data[..., 2] > 0).sum()) if n_classes > 2 else 0,
        "gm_volume_fraction": float((output_data[..., 1] > 0).sum()) / output_data[..., 1].size if n_classes > 1 else 0.0,
        "wm_volume_fraction": float((output_data[..., 2] > 0).sum()) / output_data[..., 2].size if n_classes > 2 else 0.0,
        "mixeltype_volume": int((output_data[..., -2] > 0).sum()),
        "snr": float(snr),
        "cnr": float(cnr),
        "tool": "FSL FAST",
        "version": "6.0.5",  # Ideally, we would extract the actual version from the FSL image.
        "parameters": {
            "n_channels": n_channels,
            "image_type": image_type,
            "n_classes": n_classes,
            "hyper": hyper,
            "iter": iter,
            "lowpass": lowpass
        }
    }
    
    output_entities: dict = {
        "desc": "fast",
        "suffix": "seg",
        "extension": ".nii.gz"
    }

    # Forced outputs - files that are saved are by the application but not NeuroAnalyst-compliant
    all_tissue_file_suffixes: list[str] = tissue_file_suffixes + ["_pveseg"]
    forced_outputs: list[str] = [f"{output_basename}{suffix}.nii.gz" for suffix in all_tissue_file_suffixes] + [brain_temp_path]

    return output_data, metrics, output_entities, forced_outputs