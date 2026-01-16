from neuroanalyst.models.process.logic.core import Metric

import os, subprocess, traceback

import nibabel as nib
import numpy as np
from bids.layout import parse_file_entities
from skimage.filters import threshold_otsu

def autorecon1(input_filepath: str):
    """
    FreeSurfer Autorecon1.
    Runs FreeSurfer's autorecon1 on the input NIfTI file. (https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all).
        1.  Motion Correction and Conform
        2.  NU (Non-Uniform intensity normalization)
        3.  Talairach transform computation
        4.  Intensity Normalization 1
        5.  Skull Strip
    
    Notes for future implementations and error handling:
    - If a subject directory has been created previously, re-running with -i flag will error out. Remove the flag or delete the subject directory beforehand.
    - If a process is already running for the same subject, it will error out. Run this command to check and remove the lock:
        rm /data/tmp/freesurfer_subjects/{subject_dirname}/scripts/IsRunning.lh+rh
    - Add -qcache flag
    
    Args:
        input_filepath (str): Path to input NIfTI file.
    Returns:
        output_data (np.ndarray): Array of intensity-normalized brain ("T1") and skull-stripped brain ("brainmask.mgz").
            Shape will be (X, Y, Z, 2) where the last dimension corresponds to [T1, brainmask].
            *Note - this output is only as a reference for downstream processing; the actual outputs are saved in FreeSurfer's subject directory structure.
        metrics (dict): Dictionary of relevant metrics.
        output_entities (dict): Dictionary of BIDS entities for the output file.
        forced_outputs (list): List of file paths that are saved as outputs but not BIDS-compliant.
    """
    def pre_autorecon1_basic_checks(img: nib.Nifti1Image):
        """
        Perform basic checks on the input T1 image before running FreeSurfer Autorecon1.
        
        Args:
            img (nib.Nifti1Image): Input T1 NIfTI image.
        Raises:
            ValueError: If any of the checks fail.
        """
        data = img.get_fdata()
        zooms = img.header.get_zooms()[:3]

        if data.ndim != 3:
            raise ValueError("T1 image is not 3D")

        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            raise ValueError("T1 image contains NaNs or Infs")

        if np.max(data) <= 0:
            raise ValueError("T1 image has no positive intensities")

        if not all(0.5 <= z <= 2.0 for z in zooms):
            raise ValueError(f"Unexpected voxel size for T1: {zooms}")

    def foreground_fraction(data: np.ndarray) -> float:
        """
        Calculate the fraction of foreground voxels in the image using Otsu's thresholding.
        
        Args:
            data (np.ndarray): Input image data.
        Returns:
            float: Fraction of foreground voxels.
        """
        thresh = threshold_otsu(data[data > 0])
        fg = data > thresh
        return np.mean(fg)
    
    def cnr_proxy(data: np.ndarray) -> float:
        """
        Calculate a proxy for the contrast-to-noise ratio (CNR) in the image.
        
        Args:
            data (np.ndarray): Input image data.
        Returns:
            float: CNR proxy value.
        """
        nonzero = data[data > 0]
        p30, p70 = np.percentile(nonzero, [30, 70])
        low = nonzero[nonzero < p30]
        high = nonzero[nonzero > p70]
        return (np.mean(high) - np.mean(low)) / np.std(nonzero)
        
    # Step 1: Prepare environment and paths
    DATA_DIR: str = "/data"  # shared data dir bind
    PIPELINE_NAME: str = os.getenv("PIPELINE_NAME", "default_pipeline")
    FREESURFER_HOME: str = os.getenv("FREESURFER_HOME", None)
    FOREGROUND_FRACTION_MIN: float = float(os.getenv("FOREGROUND_FRACTION_MIN", 0.1))
    print("FOREGROUND_FRACTION_MIN:", FOREGROUND_FRACTION_MIN)
    FOREGROUND_FRACTION_MAX: float = float(os.getenv("FOREGROUND_FRACTION_MAX", 0.7))
    print("FOREGROUND_FRACTION_MAX:", FOREGROUND_FRACTION_MAX)
    CNR_THRESHOLD: float = float(os.getenv("CNR_THRESHOLD", 0.6))
    print("CNR_THRESHOLD:", CNR_THRESHOLD)
    if not FREESURFER_HOME:
        raise EnvironmentError("FREESURFER_HOME environment variable is not set.")
    freesurfer_outputs_dir: str = os.path.join(DATA_DIR, "derivatives", PIPELINE_NAME, "tmp")  #! Temporary directory for outputs; which would be usually be cleaned up by NeuroAnalyst wrapper, but here we keep it for FreeSurfer's intermediate files.
    os.makedirs(freesurfer_outputs_dir, exist_ok=True)
    
    # Step 2: Validate input image
    img: nib.Nifti1Image = nib.load(input_filepath)
    try:
        pre_autorecon1_basic_checks(img)
    except Exception as e:
        print(f"Pre-Autorecon1 basic checks failed: {e}")
        print(traceback.format_exc())
        raise e
    
    if not (FOREGROUND_FRACTION_MIN <= foreground_fraction(img.get_fdata()) <= FOREGROUND_FRACTION_MAX):
        raise ValueError(f"T1 image foreground fraction is outside acceptable range for FreeSurfer processing. Calculated: {foreground_fraction(img.get_fdata())}, Expected: [{FOREGROUND_FRACTION_MIN}, {FOREGROUND_FRACTION_MAX}]")
    
    cnr_proxy_value = cnr_proxy(img.get_fdata())
    print("CNR Proxy Value:", cnr_proxy_value)
    if cnr_proxy_value < CNR_THRESHOLD:
        raise ValueError(f"T1 image CNR proxy is below acceptable threshold for FreeSurfer processing. Calculated: {cnr_proxy_value}, Threshold: {CNR_THRESHOLD}")
    
    # Step 3: Prepare FreeSurfer command
    entities: dict = parse_file_entities(input_filepath)
    subject_dirname: str = ""
    subject_id, session_id = None, None
    if "subject" in entities:
        subject_id = entities["subject"]
    if "session" in entities:
        session_id = entities["session"]
    subject_dirname = f"{subject_id}"
    if session_id:
        subject_dirname += f"_{session_id}"
    if subject_dirname == "":
        subject_dirname = "unknown_subject"
    fs_subjects_dir: str = os.path.join(freesurfer_outputs_dir, "freesurfer_subjects")
    os.makedirs(fs_subjects_dir, exist_ok=True)
    
    cmd = [
        "bash", "-c",
        f"""
        source {FREESURFER_HOME}/SetUpFreeSurfer.sh && \\
        export OMP_NUM_THREADS=8 && \\
        export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=8 && \\
        export SUBJECTS_DIR={fs_subjects_dir} && \\
        recon-all -i '{input_filepath}' -s '{subject_dirname}' -autorecon1
        """
    ]
    
    # Step 4: Prepare outputs
    skull_stripped_filepath: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "brainmask.mgz")
    t1_filepath: str = os.path.join(fs_subjects_dir, subject_dirname, "mri", "T1.mgz")

    # Step 5: Run the FreeSurfer command if the outputs do not already exist
    if not os.path.exists(skull_stripped_filepath) or not os.path.exists(t1_filepath):
        print(f"Running command: {cmd}")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"FreeSurfer Autorecon1 command finished with return code {result.returncode}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error running FreeSurfer Autorecon1 command: {e}")
            if getattr(e, "stdout", None):
                print("Stdout:", e.stdout)
            if getattr(e, "stderr", None):
                print("Stderr:", e.stderr)
            traceback.print_exc()
            raise e
    else:
        print("Outputs already exist. Skipping FreeSurfer command execution.")

    if not os.path.exists(skull_stripped_filepath) or not os.path.exists(t1_filepath):
        raise FileNotFoundError(f"Expected outputs from FreeSurfer Autorecon1 not found: {skull_stripped_filepath}, {t1_filepath}.")
    
    skull_stripped_img: nib.Nifti1Image = nib.load(skull_stripped_filepath)
    t1_img: nib.Nifti1Image = nib.load(t1_filepath)
    t1_data: np.ndarray = t1_img.get_fdata()[..., np.newaxis]
    skull_stripped_data: np.ndarray = skull_stripped_img.get_fdata()[..., np.newaxis]
    t1_data = np.concatenate([t1_data, skull_stripped_data], axis=-1)  # Shape: (X, Y, Z, 2)
    
    # Calculate metrics using skull-stripped image and whole T1 image
    brain_volume: float = np.sum(skull_stripped_img.get_fdata() > 0) * np.prod(skull_stripped_img.header.get_zooms()[:3])  # in mm³
    
    # QC metrics
    mask_ratio: float = np.sum(skull_stripped_img.get_fdata() > 0) / np.sum(t1_img.get_fdata() > 0)
    mask_intensity_mean: float = np.mean(t1_img.get_fdata()[skull_stripped_img.get_fdata() > 0])

    CATEGORY: str = "anatomical"
    metrics = {
        "brain_volume": Metric(
            name="brain_volume",
            value=brain_volume,
            unit="mm3",
            description="Volume of the brain mask",
            category=CATEGORY,
            labels=["brain", "volume"]
        ),
        "brain_dimensions": t1_data.shape[:-1],
        "mask_ratio": Metric(
            name="mask_ratio",
            value=mask_ratio,
            description="Ratio of brain mask voxels to total T1 voxels",
            category=CATEGORY,
            labels=["qc", "mask"]
        ),
        "mask_intensity_mean": Metric(
            name="mask_intensity_mean",
            value=mask_intensity_mean,
            description="Mean intensity within the brain mask",
            category=CATEGORY,
            labels=["qc", "intensity"]
        ),
        "contrast_to_noise_proxy": Metric(
            name="contrast_to_noise_proxy",
            value=cnr_proxy_value,
            description="Proxy measure for contrast-to-noise ratio in the T1 image",
            category=CATEGORY,
            labels=["qc", "cnr"]
        ),
        "channels": ["T1", "brainmask"],
        "freesurfer_version": FREESURFER_HOME.split("/")[-1],
        "original_output_path": fs_subjects_dir,
    }
    
    output_entities = {
        "desc": "autorecon1",
        "suffix": "T1w",
        "extension": ".nii.gz"
    }
    
    
    # forced_outputs = [brain_filepath, brain_mask_filepath]
    forced_outputs = []
    
    return t1_data, metrics, output_entities, forced_outputs