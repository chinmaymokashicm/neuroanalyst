"""
Complete DTI Analysis Pipeline using DIPY
Production-ready code for diffusion tensor imaging analysis
Combines DTI with T1w anatomical reference
"""

import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Tuple, Optional
import json
from warnings import warn
import copy

# DIPY imports
from dipy.core.gradients import gradient_table
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti, load_nifti_data, save_nifti
from dipy.reconst.dti import TensorModel, fractional_anisotropy, mean_diffusivity
from dipy.reconst.dti import axial_diffusivity, radial_diffusivity, color_fa
from dipy.reconst.shm import CsaOdfModel
from dipy.reconst.csdeconv import auto_response_ssst
from dipy.segment.mask import median_otsu
from dipy.direction import peaks_from_model
from dipy.tracking.stopping_criterion import ThresholdStoppingCriterion
from dipy.tracking.local_tracking import LocalTracking
from dipy.tracking.streamline import Streamlines
from dipy.tracking import utils as tutils
from dipy.io.streamline import save_tractogram, load_tractogram
from dipy.io.stateful_tractogram import StatefulTractogram, Space
from dipy.data import default_sphere
from dipy.denoise.noise_estimate import estimate_sigma
from dipy.denoise.localpca import genpca, localpca, mppca
from dipy.denoise.patch2self import patch2self
from dipy.align.imaffine import AffineMap
from dipy.align.transforms import AffineTransform3D
from dipy.align.imaffine import MutualInformationMetric, AffineRegistration
from dipy.align.transforms import TranslationTransform3D, RigidTransform3D
from scipy import ndimage


# ============================================================================
# MAIN PIPELINE CLASS
# ============================================================================

class DTIAnalysisPipeline:
    """
    Complete DTI analysis pipeline with T1w anatomical reference
    
    This pipeline implements best practices for DTI analysis including:
    - Data loading and quality checks
    - Preprocessing (denoising)
    - Tensor model fitting
    - Advanced diffusion modeling (CSD)
    - Fiber tractography
    - Multimodal T1w integration
    - ROI analysis
    """
    
    def __init__(self, dwi_path: str, bval_path: str, bvec_path: str, 
                 t1w_path: str, output_dir: str):
        """
        Initialize pipeline with file paths
        
        Parameters
        ----------
        dwi_path : str
            Path to diffusion weighted imaging NIfTI file
        bval_path : str
            Path to b-values file
        bvec_path : str
            Path to b-vectors file (gradient directions)
        t1w_path : str
            Path to T1-weighted anatomical image
        output_dir : str
            Directory for saving outputs
        """
        self.dwi_path = dwi_path
        self.bval_path = bval_path
        self.bvec_path = bvec_path
        self.t1w_path = t1w_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Store loaded data
        self.dwi_data = None
        self.dwi_affine = None
        self.bvals = None
        self.bvecs = None
        self.gtab = None
        self.t1w_data = None
        self.t1w_affine = None
        self.mask = None
        
        # Results storage
        self.results = {}
        
    def load_data(self) -> Dict:
        """
        STEP 1: Load all necessary imaging data
        
        Extracts:
        - DWI 4D volume (X, Y, Z, N_directions)
        - Gradient table (b-values and directions)
        - T1w reference anatomy
        - Computes a mask from the DWI data
        
        Returns
        -------
        Dict
            Dictionary containing loaded data info
        """
        print("\n" + "="*70)
        print("STEP 1: LOADING DATA")
        print("="*70)
        
        # Load DWI data
        print(f"\nLoading DWI from: {self.dwi_path}")
        self.dwi_data, self.dwi_affine = load_nifti(self.dwi_path)
        print(f"✓ DWI shape: {self.dwi_data.shape}")
        print(f"  - Spatial dimensions: {self.dwi_data.shape[:3]}")
        print(f"  - Number of volumes: {self.dwi_data.shape[3]}")
        
        # Load gradient information
        print(f"\nLoading gradient information...")
        self.bvals, self.bvecs = read_bvals_bvecs(self.bval_path, self.bvec_path)
        self.gtab = gradient_table(self.bvals, self.bvecs)
        print(f"✓ Number of gradient directions: {len(self.bvals)}")
        print(f"  - Unique b-values: {np.unique(self.bvals)} s/mm²")
        print(f"  - b0 images: {np.sum(self.gtab.b0s_mask)}")
        
        # Load T1w reference
        print(f"\nLoading T1w anatomical reference...")
        self.t1w_data, self.t1w_affine = load_nifti(self.t1w_path)
        print(f"✓ T1w shape: {self.t1w_data.shape}")
        
        # Create mask
        self._compute_mask()
        
        info = {
            'dwi_shape': self.dwi_data.shape,
            'num_directions': self.dwi_data.shape[3],
            'b_values': np.unique(self.bvals).tolist(),
            'mask_voxels': int(np.sum(self.mask)),
            't1w_shape': self.t1w_data.shape
        }
        
        self.results['load_info'] = info
        return info
    
    def _compute_mask(self, threshold: float = 0.5):
        """
        Compute brain mask from DWI data using Otsu thresholding
        """
        
        print("Computing brain mask...")
        # Use first b0 image
        b0_img = self.dwi_data[..., self.gtab.b0s_mask]
        b0_mean = np.mean(b0_img, axis=-1)
        
        _, self.mask = median_otsu(b0_mean, vol_idx=[0], median_radius=3, 
                                    numpass=2)
        print(f"✓ Mask computed: {np.sum(self.mask)} voxels")
    
    # ========================================================================
    # STEP 2: PREPROCESSING
    # ========================================================================
    
    def denoise_data(self) -> Dict:
        """
        STEP 2: Denoising using Marchenko-Pastur PCA
        
        Removes thermal noise while preserving tissue microstructure
        
        Metrics Extracted:
        - Noise standard deviation estimate
        - Signal-to-noise ratio before/after
        - Data quality metrics
        
        Returns
        -------
        Dict
            Denoising statistics
        """
        print("\n" + "="*70)
        print("STEP 2: DENOISING")
        print("="*70)
        
        try:
            # Store original data
            original_data = self.dwi_data.copy()
        
            # Estimate noise - get scalar sigma
            print("\nEstimating noise characteristics...")
            sigma_arr = estimate_sigma(self.dwi_data, N=4)
            
            if isinstance(sigma_arr, np.ndarray):
                sigma = float(np.mean(sigma_arr))
            else:
                sigma = float(sigma_arr)
            
            print(f"✓ Estimated noise std: {sigma:.4f}")
            
            # Apply PCA denoising with error handling
            print("Applying PCA denoising...")
            # denoised_data = mppca(self.dwi_data, patch_radius=2, mask=self.mask)
            denoised_data = patch2self(
                data=self.dwi_data,
                bvals=self.bvals,
                model="ols",
                shift_intensity=True,
                clip_negative_vals=False,
                b0_threshold=50,
            )
            
            # Compute noise as difference between original and denoised
            noise_removed = original_data - denoised_data
            actual_noise_std = np.std(noise_removed[self.mask])
            
            # Get b0 data for SNR calculation
            b0_mask = self.gtab.b0s_mask
            b0_original = original_data[..., b0_mask]
            b0_denoised = denoised_data[..., b0_mask]
            
            # Calculate signals
            signal_original = np.mean(b0_original[self.mask])
            signal_denoised = np.mean(b0_denoised[self.mask])
            
            # True SNR calculation
            # Before: (signal + noise) / noise_estimate
            # After: signal / residual_noise_estimate
            snr_before = signal_original / sigma
            
            # Estimate residual noise in denoised data
            residual_noise = np.std(b0_denoised[self.mask] - np.mean(b0_denoised[self.mask]))
            snr_after = signal_denoised / max(residual_noise, sigma * 0.1)  # Floor for numerical stability
            
            # Alternative: Compare noise levels directly
            noise_reduction = (sigma - actual_noise_std) / sigma * 100
            
            self.dwi_data = denoised_data
            
            denoise_stats = {
                'original_noise_std': float(sigma),
                'noise_removed_std': float(actual_noise_std),
                'noise_reduction_percent': float(noise_reduction),
                'signal_before': float(signal_original),
                'signal_after': float(signal_denoised),
                'signal_preservation': float(signal_denoised / signal_original * 100),
                'snr_before': float(snr_before),
                'snr_after': float(snr_after),
                'denoising_applied': True
            }
            
            print(f"✓ Original signal: {signal_original:.1f}")
            print(f"✓ Denoised signal: {signal_denoised:.1f}")
            print(f"✓ Signal preserved: {signal_denoised/signal_original*100:.1f}%")
            print(f"✓ Noise reduction: {noise_reduction:.1f}%")
            print(f"✓ SNR before: {snr_before:.2f}")
            print(f"✓ SNR after: {snr_after:.2f}")
            
        except Exception as e:
            print(f"⚠ Denoising failed completely: {e}")
            print("Using original data without denoising")
            
            # Use original data and estimate basic stats
            b0_mask = self.gtab.b0s_mask
            b0_data = self.dwi_data[..., b0_mask]
            noise_estimate = np.std(b0_data[self.mask]) * 0.1  # Rough estimate
            signal_estimate = np.mean(b0_data[self.mask])
            
            denoise_stats = {
                'noise_std': float(noise_estimate),
                'snr_before': float(signal_estimate / noise_estimate),
                'snr_after': float(signal_estimate / noise_estimate),
                'snr_improvement': 0.0,
                'denoising_applied': False,
                'error': str(e)
            }
        
        self.results['denoise_stats'] = denoise_stats
        return denoise_stats
    
    # ========================================================================
    # STEP 3: TENSOR ESTIMATION AND DTI METRICS
    # ========================================================================
    
    def fit_tensor_model(self) -> Dict:
        """
        STEP 3: Tensor Model Fitting and DTI Metric Extraction
        
        Fits the diffusion tensor model to DWI data and computes scalar metrics:
        
        PRIMARY METRICS:
        ----------------
        1. Fractional Anisotropy (FA) [0-1]
           - Measure of anisotropic diffusion
           - High FA (~0.7) = organized white matter tracts
           - Low FA (~0.2) = isotropic diffusion (gray matter, CSF)
           
        2. Mean Diffusivity (MD) [×10⁻³ mm²/s]
           - Average diffusion in all directions
           - High MD = loosely organized tissue
           - Sensitive to tissue microstructure changes
           
        3. Axial Diffusivity (AD) [×10⁻³ mm²/s]
           - Diffusion along primary fiber direction
           - Related to axonal density and integrity
           
        4. Radial Diffusivity (RD) [×10⁻³ mm²/s]
           - Diffusion perpendicular to fiber direction
           - Highly sensitive to myelin integrity
           - Increases with demyelination
        
        Returns
        -------
        Dict
            Dictionary containing DTI metrics and statistics
        """
        print("\n" + "="*70)
        print("STEP 3: TENSOR MODEL FITTING & DTI METRICS")
        print("="*70)
        
        # Initialize and fit tensor model
        print("\nFitting tensor model...")
        tensor_model = TensorModel(self.gtab, fit_method='WLS')  # Weighted least squares
        tensor_fit = tensor_model.fit(self.dwi_data, mask=self.mask)
        
        # Extract eigenvalues and eigenvectors
        evals = tensor_fit.evals  # Shape: (X, Y, Z, 3)
        evecs = tensor_fit.evecs  # Shape: (X, Y, Z, 3, 3)
        print(f"✓ Eigenvalues extracted: {evals.shape}")
        print(f"✓ Eigenvectors extracted: {evecs.shape}")
        
        # Compute scalar DTI metrics
        print("\nComputing DTI scalar metrics...")
        
        # 1. Fractional Anisotropy (FA)
        fa = fractional_anisotropy(evals)
        fa[np.isnan(fa)] = 0
        
        # 2. Mean Diffusivity (MD)
        md = mean_diffusivity(evals)
        md[np.isnan(md)] = 0
        
        # 3. Axial Diffusivity (AD)
        ad = axial_diffusivity(evals)
        ad[np.isnan(ad)] = 0
        
        # 4. Radial Diffusivity (RD)
        rd = radial_diffusivity(evals)
        rd[np.isnan(rd)] = 0
        
        # 5. Color-coded FA
        # Pass the full eigenvector array - color_fa expects shape (X, Y, Z, 3, 3)
        cfa = color_fa(fa, evecs)
        
        # Print statistics
        print(f"\n{'Metric':<10} {'Mean':<12} {'Std':<12} {'Min':<12} {'Max':<12}")
        print("-" * 50)
        print(f"{'FA':<10} {np.mean(fa[self.mask]):<12.4f} {np.std(fa[self.mask]):<12.4f} "
              f"{np.min(fa[self.mask]):<12.4f} {np.max(fa[self.mask]):<12.4f}")
        print(f"{'MD':<10} {np.mean(md[self.mask]):<12.4f} {np.std(md[self.mask]):<12.4f} "
              f"{np.min(md[self.mask]):<12.4f} {np.max(md[self.mask]):<12.4f}")
        print(f"{'AD':<10} {np.mean(ad[self.mask]):<12.4f} {np.std(ad[self.mask]):<12.4f} "
              f"{np.min(ad[self.mask]):<12.4f} {np.max(ad[self.mask]):<12.4f}")
        print(f"{'RD':<10} {np.mean(rd[self.mask]):<12.4f} {np.std(rd[self.mask]):<12.4f} "
              f"{np.min(rd[self.mask]):<12.4f} {np.max(rd[self.mask]):<12.4f}")
        
        # Save metrics
        print("\nSaving metrics to NIfTI files...")
        self._save_metric(fa, 'fa.nii.gz')
        self._save_metric(md, 'md.nii.gz')
        self._save_metric(ad, 'ad.nii.gz')
        self._save_metric(rd, 'rd.nii.gz')
        self._save_metric(cfa, 'color_fa.nii.gz')
        
        dti_dict = {
            'fa': fa,
            'md': md,
            'ad': ad,
            'rd': rd,
            'cfa': cfa,
            'evals': evals,
            'evecs': evecs,
            'tensor_fit': tensor_fit,
            'statistics': {
                'fa': {
                    'mean': float(np.mean(fa[self.mask])),
                    'std': float(np.std(fa[self.mask])),
                    'min': float(np.min(fa[self.mask])),
                    'max': float(np.max(fa[self.mask]))
                },
                'md': {
                    'mean': float(np.mean(md[self.mask])),
                    'std': float(np.std(md[self.mask]))
                },
                'ad': {
                    'mean': float(np.mean(ad[self.mask])),
                    'std': float(np.std(ad[self.mask]))
                },
                'rd': {
                    'mean': float(np.mean(rd[self.mask])),
                    'std': float(np.std(rd[self.mask]))
                }
            }
        }
        
        self.results['dti_metrics'] = dti_dict
        return dti_dict
    
    # ========================================================================
    # STEP 4: ADVANCED DIFFUSION MODELS
    # ========================================================================
    
    def fit_csd_model(self) -> Dict:
        """
        STEP 4: Constrained Spherical Deconvolution (CSD)
        
        Advanced fiber orientation estimation that handles fiber crossings
        
        Metrics Extracted:
        - Fiber Orientation Distribution Function (fODF)
        - Peak fiber directions
        - Generalized FA (GFA)
        - Number of crossing fibers per voxel
        
        Advantages:
        - Handles multiple fiber populations in single voxel
        - Better for crossing fiber regions
        - Foundation for advanced tractography
        
        Returns
        -------
        Dict
            CSD model results including peaks and statistics
        """
        print("\n" + "="*70)
        print("STEP 4: CONSTRAINED SPHERICAL DECONVOLUTION (CSD)")
        print("="*70)
        
        try:
            # Compute response function (single-fiber white matter signal)
            print("\nComputing white matter response function...")
            response, ratio = auto_response_ssst(self.gtab, self.dwi_data, 
                                            roi_radii=10, fa_thr=0.7)
            
            # Handle response function formatting - response might be a tuple or array
            if isinstance(response, tuple):
                # If response is a tuple, take the first element
                response_vals = response[0] if len(response) > 0 else response
            else:
                response_vals = response
                
            # Now handle the response values
            if isinstance(response_vals, np.ndarray) and len(response_vals) > 0:
                s0_value = float(response_vals[0])
            elif hasattr(response_vals, '__len__') and len(response_vals) > 0:
                s0_value = float(response_vals[0])
            else:
                s0_value = float(response_vals)
                
            # Handle ratio - it might also be a complex structure
            if hasattr(ratio, '__len__') and not isinstance(ratio, str):
                ratio_value = float(ratio[0]) if len(ratio) > 0 else 1.0
            else:
                ratio_value = float(ratio)
                
            print(f"✓ Response function: S0={s0_value:.1f}")
            print(f"✓ Anisotropy ratio: {ratio_value:.4f}")
            
            # Check if we have a valid response function
            if s0_value <= 0:
                raise ValueError("Invalid response function - S0 value is zero or negative")
            
            # Fit CSD model - use CSA instead of CSD for better compatibility
            print("Fitting CSA model (Constant Solid Angle ODF)...")
            try:
                # from dipy.reconst.shm import CsaOdfModel
                # For CSA, we don't need the response function - it's model-free
                csa_model = CsaOdfModel(self.gtab, sh_order=6)
                csa_fit = csa_model.fit(self.dwi_data, mask=self.mask)
                print(f"✓ CSA model fitted")
            except Exception as e:
                raise RuntimeError(f"CSA model fitting failed: {e}")
            
            # Extract peaks (fiber directions)
            print("Extracting fiber peaks...")
            sphere = default_sphere
            peaks = peaks_from_model(csa_model, self.dwi_data, 
                                     sphere, .5, 25, 
                                     mask=self.mask, normalize_peaks=True)
            
            print(f"✓ Peaks extracted")
            
            # Handle different attribute names for number of peaks
            if hasattr(peaks, 'npeaks'):
                npeaks_array = peaks.npeaks
            elif hasattr(peaks, 'peak_indices'):
                # Calculate number of peaks from peak_indices shape
                npeaks_array = np.sum(peaks.peak_indices >= 0, axis=-1)
            elif hasattr(peaks, 'peak_dirs'):
                # Calculate from peak_dirs shape 
                npeaks_array = np.sum(np.any(peaks.peak_dirs != 0, axis=-1), axis=-1)
            else:
                # Fallback: assume single peak per voxel
                print("⚠ Warning: Could not determine number of peaks, assuming 1 per voxel")
                npeaks_array = np.ones(self.mask.shape, dtype=int)
            
            print(f"  - Max fibers per voxel: {npeaks_array.max()}")
            print(f"  - Mean fibers: {npeaks_array[self.mask].mean():.2f}")
            
            # Check for crossing fibers
            crossings = np.sum(npeaks_array > 1) if npeaks_array is not None else 0
            
            csd_dict = {
                'csd_fit': csa_fit,  # Using CSA instead of CSD
                'peaks': peaks,
                'response_function': response,
                'anisotropy_ratio': ratio_value,
                'model_type': 'CSA',  # Note the model type
                'statistics': {
                    'max_fibers': int(npeaks_array.max()),
                    'mean_fibers': float(npeaks_array[self.mask].mean()),
                    'voxels_with_crossings': int(crossings)
                }
            }
            
            self.results['csd_result'] = csd_dict
            return csd_dict
            
        except Exception as e:
            print(f"⚠ CSD fitting failed (may need higher angular resolution): {e}")
            return {'error': str(e)}
    
    # ========================================================================
    # STEP 5: REGION OF INTEREST ANALYSIS
    # ========================================================================
    
    def extract_roi_metrics(self, roi_mask: np.ndarray, 
                           roi_name: str, dti_metrics: Dict) -> Dict:
        """
        STEP 5: Extract DTI Metrics within Regions of Interest
        
        Computes regional statistics for a given ROI
        
        Metrics Extracted (per ROI):
        - Mean FA, MD, AD, RD values
        - Standard deviation and range
        - Percentile distributions (5th, 25th, 75th, 95th)
        - ROI volume (in voxels and mm³)
        
        Parameters
        ----------
        roi_mask : np.ndarray
            Binary mask defining the ROI
        roi_name : str
            Name of the ROI (for output)
        dti_metrics : Dict
            Dictionary from fit_tensor_model()
        
        Returns
        -------
        Dict
            Regional statistics
        """
        print("\n" + "="*70)
        print(f"STEP 5: ROI ANALYSIS - {roi_name.upper()}")
        print("="*70)

        fa: np.ndarray = dti_metrics['fa']
        md: np.ndarray = dti_metrics['md']
        ad: np.ndarray = dti_metrics['ad']
        rd: np.ndarray = dti_metrics['rd']

        # Combine ROI with brain mask
        roi_mask_final: np.ndarray = roi_mask & self.mask
        num_voxels: int = np.sum(roi_mask_final)
        
        if num_voxels == 0:
            print(f"⚠ Warning: ROI '{roi_name}' has no valid voxels")
            return {'error': 'Empty ROI'}
        
        voxel_volume_mm3 = np.prod(self.dwi_affine.diagonal()[:3])
        roi_volume_mm3 = num_voxels * abs(voxel_volume_mm3)
        
        # Extract metrics within ROI
        fa_roi: np.ndarray = fa[roi_mask_final]
        md_roi: np.ndarray = md[roi_mask_final]
        ad_roi: np.ndarray = ad[roi_mask_final]
        rd_roi: np.ndarray = rd[roi_mask_final]

        roi_stats = {
            'roi_name': roi_name,
            'num_voxels': int(num_voxels),
            'volume_mm3': float(roi_volume_mm3),
            'fa': {
                'mean': float(np.mean(fa_roi)),
                'std': float(np.std(fa_roi)),
                'median': float(np.median(fa_roi)),
                'min': float(np.min(fa_roi)),
                'max': float(np.max(fa_roi)),
                'p5': float(np.percentile(fa_roi, 5)),
                'p25': float(np.percentile(fa_roi, 25)),
                'p75': float(np.percentile(fa_roi, 75)),
                'p95': float(np.percentile(fa_roi, 95))
            },
            'md': {
                'mean': float(np.mean(md_roi)),
                'std': float(np.std(md_roi)),
                'median': float(np.median(md_roi)),
                'min': float(np.min(md_roi)),
                'max': float(np.max(md_roi)),
                'p5': float(np.percentile(md_roi, 5)),
                'p25': float(np.percentile(md_roi, 25)),
                'p75': float(np.percentile(md_roi, 75)),
                'p95': float(np.percentile(md_roi, 95))
            },
            'ad': {
                'mean': float(np.mean(ad_roi)),
                'std': float(np.std(ad_roi))
            },
            'rd': {
                'mean': float(np.mean(rd_roi)),
                'std': float(np.std(rd_roi))
            }
        }
        
        print(f"\n{'ROI Name':<20} {roi_name}")
        print(f"{'Volume (mm³)':<20} {roi_volume_mm3:>15.1f}")
        print(f"{'Number of voxels':<20} {num_voxels:>15}")
        print(f"\n{'Metric':<10} {'Mean':<12} {'Std':<12} {'p5':<12} {'p95':<12}")
        print("-" * 50)
        print(f"{'FA':<10} {roi_stats['fa']['mean']:<12.4f} {roi_stats['fa']['std']:<12.4f} "
              f"{roi_stats['fa']['p5']:<12.4f} {roi_stats['fa']['p95']:<12.4f}")
        print(f"{'MD':<10} {roi_stats['md']['mean']:<12.4f} {roi_stats['md']['std']:<12.4f} "
              f"{roi_stats['md']['p5']:<12.4f} {roi_stats['md']['p95']:<12.4f}")
        
        return roi_stats
    
    # ========================================================================
    # STEP 6: FIBER TRACKING
    # ========================================================================
    
    def fiber_tracking(self, csd_result: Dict, 
                      num_seeds_per_voxel: int = 2,
                      max_angle: float = 30.0) -> Dict:
        """
        STEP 6: Deterministic Fiber Tractography
        
        Performs local fiber tracking from white matter seeds
        
        Metrics Extracted:
        - Number of streamlines tracked
        - Streamline length statistics
        - Curvature statistics
        - Connectivity patterns
        
        Parameters
        ----------
        csd_result : Dict
            Results from CSD model fitting
        num_seeds_per_voxel : int
            Seeds to initiate from each WM voxel
        max_angle : float
            Maximum turning angle in degrees
        
        Returns
        -------
        Dict
            Fiber tracking results
        """
        print("\n" + "="*70)
        print("STEP 6: FIBER TRACTOGRAPHY")
        print("="*70)
        
        peaks = csd_result.get('peaks')
        if peaks is None:
            print("⚠ CSD peaks not available, skipping tractography")
            return {'error': 'CSD peaks required'}
        
        print(f"\nTracking parameters:")
        print(f"  - Maximum angle: {max_angle}°")
        print(f"  - Seeds per voxel: {num_seeds_per_voxel}")
        
        # Create stopping criterion
        stopping_criterion = ThresholdStoppingCriterion(peaks.gfa, 0.1)
        
        # Create seeds in white matter
        print("\nGenerating seeds in white matter...")
        try:
            # Try the newer function name first
            seeds = tutils.seeds_from_mask(
                self.mask & (peaks.gfa > 0.1), 
                self.dwi_affine, 
                density=num_seeds_per_voxel
            )
        except AttributeError:
            try:
                # Fallback to older function name
                seeds = tutils.random_seeds_from_mask(
                    self.mask & (peaks.gfa > 0.1), 
                    self.dwi_affine, 
                    seeds_count=num_seeds_per_voxel
                )
            except AttributeError:
                # Manual seed generation as final fallback
                wm_mask = self.mask & (peaks.gfa > 0.1)
                indices = np.where(wm_mask)
                n_voxels = len(indices[0])
                n_seeds = n_voxels * num_seeds_per_voxel
                
                # Generate random offsets within voxels
                offsets = np.random.rand(n_seeds, 3) - 0.5
                
                # Repeat voxel coordinates
                voxel_coords = np.column_stack([
                    np.repeat(indices[0], num_seeds_per_voxel),
                    np.repeat(indices[1], num_seeds_per_voxel), 
                    np.repeat(indices[2], num_seeds_per_voxel)
                ])
                
                # Add offsets to get seed coordinates
                seed_coords = voxel_coords + offsets
                
                # Transform to world coordinates
                seeds = np.dot(self.dwi_affine, np.column_stack([seed_coords, np.ones(n_seeds)]).T)[:3].T
                
        print(f"✓ Generated {len(seeds)} seed points")
        
        # Perform tracking
        print("Performing fiber tracking...")
        streamlines_gen = LocalTracking(
            peaks, stopping_criterion, seeds,
            affine=self.dwi_affine, max_cross=1,
            step_size=0.5
        )
        streamlines = Streamlines(streamlines_gen)
        print(f"✓ Tracked {len(streamlines)} streamlines")
        
        # Compute streamline statistics
        tracking_stats = {}
        if len(streamlines) > 0:
            lengths = np.array([len(sl) for sl in streamlines])
            
            print(f"\nStreamline Statistics:")
            print(f"  - Length (in points):")
            print(f"    * Mean: {np.mean(lengths):.1f}")
            print(f"    * Median: {np.median(lengths):.1f}")
            print(f"    * Range: [{np.min(lengths)}, {np.max(lengths)}]")
            
            tracking_stats = {
                'num_streamlines': len(streamlines),
                'length_mean': float(np.mean(lengths)),
                'length_median': float(np.median(lengths)),
                'length_min': int(np.min(lengths)),
                'length_max': int(np.max(lengths))
            }
        
        # Save streamlines
        trk_file = self.output_dir / 'streamlines.trk'
        sft = StatefulTractogram(
            streamlines=streamlines,
            reference=nib.load(self.t1w_path),
            space=Space.RASMM
        )
        save_tractogram(sft, str(trk_file), bbox_valid_check=False)
        print(f"\n✓ Streamlines saved to: {trk_file}")
        
        tracking_dict = {
            'num_streamlines': len(streamlines),
            'streamlines': streamlines,
            'statistics': tracking_stats
        }
        
        self.results['tracking'] = tracking_dict
        return tracking_dict
    
    # ========================================================================
    # STEP 7: MULTIMODAL ANALYSIS
    # ========================================================================
    
    def multimodal_analysis(self, dti_metrics: Dict) -> Dict:
        """
        STEP 7: Integration of T1w and DTI Analysis
        
        Combines anatomical information with diffusion metrics
        
        Metrics Extracted:
        - Tissue-specific DTI values (GM vs WM)
        - FA and MD by tissue type
        - Tissue classification metrics
        
        Returns
        -------
        Dict
            Multimodal analysis results
        """
        print("\n" + "="*70)
        print("STEP 7: MULTIMODAL T1W + DTI INTEGRATION")
        print("="*70)
        
        # Check if T1w resampling is needed
        dwi_shape = self.dwi_data.shape[:3]
        t1w_shape = self.t1w_data.shape
        
        if dwi_shape != t1w_shape:
            print(f"\nDimension mismatch detected:")
            print(f"  - DWI: {dwi_shape}")
            print(f"  - T1w: {t1w_shape}")
            
            # Attempt to resample T1w to DWI space
            if not self._resample_t1w_to_dwi():
                # Fall back to FA-based tissue classification
                return self._fa_based_tissue_analysis(dti_metrics)
            
            t1w_data_for_analysis = self.t1w_resampled
        else:
            t1w_data_for_analysis = self.t1w_data
        
        print("\nPerforming tissue classification...")
        
        # Simple intensity-based tissue classification from T1w
        t1w_normalized = (t1w_data_for_analysis - t1w_data_for_analysis.min()) / \
                         (t1w_data_for_analysis.max() - t1w_data_for_analysis.min())
        
        # Approximate tissue types based on T1w intensity
        gm_mask = (t1w_normalized > 0.3) & (t1w_normalized < 0.6) & self.mask
        wm_mask = (t1w_normalized > 0.6) & self.mask
        
        fa = dti_metrics['fa']
        md = dti_metrics['md']
        
        # Extract metrics by tissue type
        gm_fa = fa[gm_mask]
        wm_fa = fa[wm_mask]
        gm_md = md[gm_mask]
        wm_md = md[wm_mask]
        
        multimodal_stats = {
            'gray_matter': {
                'num_voxels': int(np.sum(gm_mask)),
                'fa_mean': float(np.mean(gm_fa)) if len(gm_fa) > 0 else 0,
                'fa_std': float(np.std(gm_fa)) if len(gm_fa) > 0 else 0,
                'md_mean': float(np.mean(gm_md)) if len(gm_md) > 0 else 0
            },
            'white_matter': {
                'num_voxels': int(np.sum(wm_mask)),
                'fa_mean': float(np.mean(wm_fa)) if len(wm_fa) > 0 else 0,
                'fa_std': float(np.std(wm_fa)) if len(wm_fa) > 0 else 0,
                'md_mean': float(np.mean(wm_md)) if len(wm_md) > 0 else 0
            },
            'resampling_applied': dwi_shape != t1w_shape
        }
        
        # Compute tissue contrast
        fa_diff = np.mean(wm_fa) - np.mean(gm_fa) if (len(wm_fa) > 0 and len(gm_fa) > 0) else 0
        multimodal_stats['fa_wm_gm_diff'] = float(fa_diff)
        
        print(f"\n{'Tissue Type':<20} {'Voxels':<12} {'FA Mean':<12} {'MD Mean':<12}")
        print("-" * 56)
        print(f"{'Gray Matter':<20} {multimodal_stats['gray_matter']['num_voxels']:<12} "
              f"{multimodal_stats['gray_matter']['fa_mean']:<12.4f} "
              f"{multimodal_stats['gray_matter']['md_mean']:<12.4f}")
        print(f"{'White Matter':<20} {multimodal_stats['white_matter']['num_voxels']:<12} "
              f"{multimodal_stats['white_matter']['fa_mean']:<12.4f} "
              f"{multimodal_stats['white_matter']['md_mean']:<12.4f}")
        print(f"\nFA contrast (WM-GM): {fa_diff:.4f}")
        
        self.results['multimodal'] = multimodal_stats
        return multimodal_stats
    
    def _resample_t1w_to_dwi(self):
        """
        Resample T1w image to match DWI space
        
        This function handles the spatial alignment between T1w and DWI images
        by resampling the T1w to match the DWI dimensions and resolution.
        """
        print("\nResampling T1w to DWI space...")
        
        try:
            # Simple approach: resample T1w to DWI grid using affine information
            from scipy.ndimage import zoom
            
            # Calculate zoom factors for each dimension
            dwi_shape = self.dwi_data.shape[:3]  # (X, Y, Z)
            t1w_shape = self.t1w_data.shape      # (X, Y, Z)
            
            zoom_factors = [
                dwi_shape[0] / t1w_shape[0],
                dwi_shape[1] / t1w_shape[1], 
                dwi_shape[2] / t1w_shape[2]
            ]
            
            print(f"  - DWI shape: {dwi_shape}")
            print(f"  - T1w shape: {t1w_shape}")
            print(f"  - Zoom factors: {zoom_factors}")
            
            # Resample T1w to match DWI dimensions
            self.t1w_resampled = zoom(self.t1w_data, zoom_factors, order=1, prefilter=True)
            
            print(f"  - Resampled T1w shape: {self.t1w_resampled.shape}")
            print("✓ T1w resampled to DWI space")
            
            return True
            
        except Exception as e:
            print(f"⚠ T1w resampling failed: {e}")
            print("  Using DWI-only analysis (no multimodal integration)")
            self.t1w_resampled = None
            return False

    def _fa_based_tissue_analysis(self, dti_metrics: Dict) -> Dict:
        """
        Fallback tissue analysis using only DTI metrics
        
        When T1w is not available or registration fails, use FA thresholds
        to approximate tissue types.
        """
        print("\nUsing FA-based tissue classification (fallback)...")
        
        fa = dti_metrics['fa']
        md = dti_metrics['md']
        
        # FA-based tissue approximation
        # High FA (>0.4) likely represents WM
        # Low FA (<0.2) likely represents GM/CSF
        wm_mask_fa = (fa > 0.4) & self.mask
        gm_mask_fa = (fa < 0.2) & (fa > 0.05) & self.mask  # Exclude very low FA (CSF)
        
        # Extract metrics
        wm_fa = fa[wm_mask_fa]
        gm_fa = fa[gm_mask_fa]
        wm_md = md[wm_mask_fa]
        gm_md = md[gm_mask_fa]
        
        fallback_stats = {
            'method': 'fa_based_classification',
            'gray_matter_approx': {
                'num_voxels': int(np.sum(gm_mask_fa)),
                'fa_mean': float(np.mean(gm_fa)) if len(gm_fa) > 0 else 0,
                'fa_std': float(np.std(gm_fa)) if len(gm_fa) > 0 else 0,
                'md_mean': float(np.mean(gm_md)) if len(gm_md) > 0 else 0
            },
            'white_matter_approx': {
                'num_voxels': int(np.sum(wm_mask_fa)),
                'fa_mean': float(np.mean(wm_fa)) if len(wm_fa) > 0 else 0,
                'fa_std': float(np.std(wm_fa)) if len(wm_fa) > 0 else 0,
                'md_mean': float(np.mean(wm_md)) if len(wm_md) > 0 else 0
            },
            'resampling_applied': False,
            'fa_wm_gm_diff': float(np.mean(wm_fa) - np.mean(gm_fa)) if (len(wm_fa) > 0 and len(gm_fa) > 0) else 0
        }
        
        print(f"\n{'Tissue Type (FA-based)':<25} {'Voxels':<12} {'FA Mean':<12} {'MD Mean':<12}")
        print("-" * 61)
        print(f"{'Gray Matter (FA<0.2)':<25} {fallback_stats['gray_matter_approx']['num_voxels']:<12} "
              f"{fallback_stats['gray_matter_approx']['fa_mean']:<12.4f} "
              f"{fallback_stats['gray_matter_approx']['md_mean']:<12.4f}")
        print(f"{'White Matter (FA>0.4)':<25} {fallback_stats['white_matter_approx']['num_voxels']:<12} "
              f"{fallback_stats['white_matter_approx']['fa_mean']:<12.4f} "
              f"{fallback_stats['white_matter_approx']['md_mean']:<12.4f}")
        
        self.results['multimodal'] = fallback_stats
        return fallback_stats

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _save_metric(self, data: np.ndarray, filename: str):
        """Save metric as NIfTI file"""
        out_path = self.output_dir / filename
        save_nifti(out_path, data.astype(np.float32), self.dwi_affine)
        print(f"  ✓ {filename}")
    
    def save_results(self, filename: str = 'pipeline_results.json'):
        """Save all results to JSON file"""
        # Convert non-serializable objects
        results_copy = {}
        for key, val in self.results.items():
            if key not in ['dti_metrics', 'csd_result', 'tracking']:
                results_copy[key] = val
            elif key == 'dti_metrics':
                results_copy[key] = val.get('statistics', {})
            elif key == 'csd_result':
                results_copy[key] = val.get('statistics', {}) if 'error' not in val else {}
            elif key == 'tracking':
                results_copy[key] = val.get('statistics', {})
        
        out_file = self.output_dir / filename
        with open(out_file, 'w') as f:
            json.dump(results_copy, f, indent=2)
        print(f"\n✓ Results saved to: {out_file}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Example: Process a subject
    # Adjust paths to your actual data
    
    dwi_path = 'sub-01_dwi.nii.gz'
    bval_path = 'sub-01_dwi.bval'
    bvec_path = 'sub-01_dwi.bvec'
    t1w_path = 'sub-01_T1w.nii.gz'
    output_dir = 'dti_analysis_output'
    
    # Initialize pipeline
    pipeline = DTIAnalysisPipeline(dwi_path, bval_path, bvec_path, 
                                   t1w_path, output_dir)
    
    # Step 1: Load data
    load_info = pipeline.load_data()
    
    # Step 2: Denoise
    denoise_info = pipeline.denoise_data()
    
    # Step 3: Tensor fitting
    dti_metrics = pipeline.fit_tensor_model()
    
    # Step 4: CSD model
    csd_result = pipeline.fit_csd_model()
    
    # Step 5: ROI analysis
    wm_roi = dti_metrics['fa'] > 0.3
    roi_stats = pipeline.extract_roi_metrics(wm_roi, 'White Matter', dti_metrics)
    
    # Step 6: Fiber tracking (if CSD successful)
    if 'error' not in csd_result:
        tracking_result = pipeline.fiber_tracking(csd_result)
    
    # Step 7: Multimodal analysis
    multimodal = pipeline.multimodal_analysis(dti_metrics)
    
    # Save results
    pipeline.save_results()
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("="*70)
