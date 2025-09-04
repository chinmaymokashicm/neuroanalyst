#!/usr/bin/env python3
"""
Example usage of the NeuProcessLogic decorator for NeuroAnalyst.

This example demonstrates various ways to use the decorator that wraps around
NeuProcessLogic to automatically handle BIDS path construction, metadata writing,
and output organization.
"""

import sys
from pathlib import Path
import tempfile
import json

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.process.logic.core import (
    NeuProcessLogic,
    NeuProcessLogicArgument,
    ProgrammingLanguage
)
from app.models.process.wrapper import (
    NeuProcessDecoratorConfig,
    neuprocess_decorator,
    create_neuprocess_function,
)
from app.models.about import About


def example_1_direct_decorator_usage():
    """Example 1: Direct decorator usage with a simple function."""
    print("=== Example 1: Direct Decorator Usage ===\n")
    
    # Create a temporary BIDS directory for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir)
        
        # Create a realistic BIDS structure
        (bids_root / "sub-01" / "ses-01" / "anat").mkdir(parents=True)
        input_file = bids_root / "sub-01" / "ses-01" / "anat" / "sub-01_ses-01_T1w.nii.gz"
        input_file.write_text("dummy T1w data")  # Simulate input file
        
        # Configure the decorator
        config = NeuProcessDecoratorConfig(
            pipeline_name="skull_stripping",
            bids_root=bids_root,
            overwrite=True,
            create_sidecar=True
        )
        
        # Define a processing function using the decorator
        @neuprocess_decorator(config)
        def skull_strip_t1w(input_filepath):
            """
            Perform skull stripping on T1w images.
            
            This function simulates a skull stripping pipeline that removes
            non-brain tissue from T1w images.
            """
            print(f"Processing {Path(input_filepath).name}")
            
            # Simulate skull stripping processing
            brain_volume = 1234567  # mm³
            brain_mask_ratio = 0.78
            
            # Create output data (in real scenario, this would be processed image data)
            output_data = f"Skull-stripped version of {Path(input_filepath).name}"
            
            # Return the required format
            return {
                "data": output_data,
                "description": "Skull stripping of T1w anatomical image",
                "metadata": {
                    "metrics": {
                        "brain_volume_mm3": brain_volume,
                        "brain_mask_ratio": brain_mask_ratio,
                        "processing_software": "custom_skull_stripper_v1.0"
                    },
                    "output_bids_entities": {
                        "desc": "brain",
                        "suffix": "T1w",
                        "extension": ".nii.gz"
                    }
                }
            }
        
        # Execute the function
        print(f"Input file: {input_file}")
        result = skull_strip_t1w(str(input_file))
        
        print(f"✅ Processing successful: {result.success}")
        print(f"✅ Output file: {result.output_filepath}")
        print(f"✅ Sidecar file: {result.sidecar_filepath}")
        print(f"✅ Execution time: {result.execution_time:.4f} seconds")
        print()


def example_2_functional_analysis():
    """Example 2: More complex functional MRI analysis."""
    print("=== Example 2: Functional MRI Analysis ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir)
        
        # Create functional MRI BIDS structure
        (bids_root / "sub-02" / "ses-02" / "func").mkdir(parents=True)
        input_file = bids_root / "sub-02" / "ses-02" / "func" / "sub-02_ses-02_task-rest_run-01_bold.nii.gz"
        input_file.write_text("dummy BOLD data")
        
        config = NeuProcessDecoratorConfig(
            pipeline_name="functional_connectivity",
            bids_root=bids_root,
            overwrite=True
        )
        
        @neuprocess_decorator(config)
        def calculate_connectivity_matrix(input_filepath):
            """
            Calculate functional connectivity matrix from BOLD data.
            
            This function computes the correlation matrix between different
            brain regions using BOLD time series data.
            """
            import numpy as np
            
            print(f"Calculating connectivity for {Path(input_filepath).name}")
            
            # Simulate connectivity analysis
            n_regions = 100
            connectivity_matrix = np.random.rand(n_regions, n_regions)
            connectivity_matrix = (connectivity_matrix + connectivity_matrix.T) / 2  # Make symmetric
            np.fill_diagonal(connectivity_matrix, 1.0)  # Set diagonal to 1
            
            # Calculate summary metrics
            mean_connectivity = float(np.mean(connectivity_matrix[np.triu_indices(n_regions, k=1)]))
            max_connectivity = float(np.max(connectivity_matrix[np.triu_indices(n_regions, k=1)]))
            
            # Prepare output data (connectivity matrix as JSON for this example)
            output_data = {
                "connectivity_matrix": connectivity_matrix.tolist(),
                "n_regions": n_regions,
                "analysis_type": "pearson_correlation"
            }
            
            return {
                "data": output_data,
                "description": "Functional connectivity analysis using Pearson correlation",
                "metadata": {
                    "metrics": {
                        "mean_connectivity": mean_connectivity,
                        "max_connectivity": max_connectivity,
                        "n_regions": n_regions,
                        "matrix_density": float(np.count_nonzero(connectivity_matrix > 0.5) / (n_regions * n_regions))
                    },
                    "output_bids_entities": {
                        "desc": "connectivity",
                        "suffix": "matrix",
                        "extension": ".json"
                    }
                }
            }
        
        # Execute the analysis
        result = calculate_connectivity_matrix(str(input_file))
        
        if result.success:
            # Load and examine the output
            with open(result.output_filepath, 'r') as f:
                connectivity_data = json.load(f)
            
            print(f"✅ Analysis completed successfully")
            print(f"✅ Output file: {result.output_filepath}")
            print(f"✅ Number of regions: {connectivity_data['n_regions']}")
            print(f"✅ Matrix shape: {len(connectivity_data['connectivity_matrix'])}x{len(connectivity_data['connectivity_matrix'][0])}")
            
            # Check sidecar metadata
            with open(result.sidecar_filepath, 'r') as f:
                metadata = json.load(f)
            
            print(f"✅ Mean connectivity: {metadata['metrics']['mean_connectivity']:.4f}")
            print(f"✅ Max connectivity: {metadata['metrics']['max_connectivity']:.4f}")
        else:
            print(f"❌ Analysis failed: {result.error_message}")
        
        print()


def example_3_neuprocesslogic_integration():
    """Example 3: Using NeuProcessLogic for automatic function generation."""
    print("=== Example 3: NeuProcessLogic Integration ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir)
        
        # Create diffusion MRI BIDS structure
        (bids_root / "sub-03" / "dwi").mkdir(parents=True)
        input_file = bids_root / "sub-03" / "dwi" / "sub-03_dwi.nii.gz"
        input_file.write_text("dummy DWI data")
        
        # Define the processing logic using NeuProcessLogic
        diffusion_logic = NeuProcessLogic(
            about=About(
                name="calculate_fa_map",
                description="Calculate Fractional Anisotropy (FA) map from diffusion tensor imaging",
                version="2.0.0",
                tag="dti-analysis"
            ),
            language=ProgrammingLanguage.PYTHON,
            code='''
# Simulate DTI processing and FA calculation
from pathlib import Path

input_path = Path(input_filepath)
print(f"Processing DTI data: {input_path.name}")

# Simulate DTI tensor calculation
# In real scenario, this would use libraries like dipy
fa_values = np.random.uniform(0, 1, size=(100, 100, 60))  # Simulated FA map
mean_fa = float(np.mean(fa_values))
std_fa = float(np.std(fa_values))

# Calculate additional DTI metrics
md_values = np.random.uniform(0.5e-3, 2.0e-3, size=(100, 100, 60))  # Mean diffusivity
mean_md = float(np.mean(md_values))

# Prepare output data
output_data = {
    "fa_map_shape": fa_values.shape,
    "fa_statistics": {
        "mean": mean_fa,
        "std": std_fa,
        "min": float(np.min(fa_values)),
        "max": float(np.max(fa_values))
    },
    "md_statistics": {
        "mean": mean_md,
        "unit": "mm2/s"
    },
    "processing_info": {
        "input_file": input_path.name,
        "tensor_model": "linear_least_squares"
    }
}

# Metrics for quality assessment
metrics = {
    "mean_fa": mean_fa,
    "std_fa": std_fa,
    "mean_md": mean_md,
    "fa_histogram_entropy": float(np.random.uniform(2.0, 4.0)),  # Simulated entropy
    "processing_success": True
}

# BIDS entities for output file
output_entities = {
    "model": "tensor",
    "suffix": "fa",
    "extension": ".json"
}

return output_data, metrics, output_entities
            ''',
            import_statements=[
                "import numpy as np",
                "from pathlib import Path"
            ],
            arguments=[
                NeuProcessLogicArgument(
                    name="input_filepath",
                    type="str",
                    is_optional=False,
                    description="Path to the input DWI file"
                )
            ]
        )
        
        # Configure the decorator
        config = NeuProcessDecoratorConfig(
            pipeline_name="dti_analysis",
            bids_root=bids_root,
            overwrite=True,
            derivatives_dir="custom_dti_pipeline"  # Custom derivatives directory
        )
        
        # Create the decorated function from NeuProcessLogic
        fa_calculator = create_neuprocess_function(diffusion_logic, config)
        
        # Execute the function
        print(f"Input DWI file: {input_file}")
        result = fa_calculator(str(input_file))
        
        if result.success:
            # Examine the results
            with open(result.output_filepath, 'r') as f:
                fa_data = json.load(f)
            
            print(f"✅ DTI analysis completed")
            print(f"✅ Output file: {result.output_filepath}")
            print(f"✅ FA map shape: {fa_data['fa_map_shape']}")
            print(f"✅ Mean FA: {fa_data['fa_statistics']['mean']:.4f}")
            print(f"✅ Mean MD: {fa_data['md_statistics']['mean']:.6f} {fa_data['md_statistics']['unit']}")
            
            # Check metadata
            with open(result.sidecar_filepath, 'r') as f:
                metadata = json.load(f)
            
            print(f"✅ Function: {metadata['FunctionName']}")
            print(f"✅ Pipeline: {metadata['ProcessingPipeline']}")
            print(f"✅ Processing time: {metadata['ProcessingTime']:.4f}s")
        else:
            print(f"❌ DTI analysis failed: {result.error_message}")
        
        print()


def example_4_batch_processing():
    """Example 4: Batch processing multiple subjects."""
    print("=== Example 4: Batch Processing ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir)
        
        # Create multi-subject BIDS structure
        subjects = ["sub-01", "sub-02", "sub-03"]
        input_files = []
        
        for subject in subjects:
            (bids_root / subject / "anat").mkdir(parents=True)
            input_file = bids_root / subject / "anat" / f"{subject}_T1w.nii.gz"
            input_file.write_text(f"dummy T1w data for {subject}")
            input_files.append(input_file)
        
        config = NeuProcessDecoratorConfig(
            pipeline_name="volume_calculation",
            bids_root=bids_root,
            overwrite=True
        )
        
        @neuprocess_decorator(config)
        def calculate_brain_volume(input_filepath):
            """Calculate total brain volume from T1w images."""
            import random
            
            subject_id = Path(input_filepath).name.split('_')[0]
            print(f"Calculating brain volume for {subject_id}")
            
            # Simulate volume calculation with some subject-specific variation
            base_volume = 1200000  # Base volume in mm³
            variation = random.uniform(-100000, 100000)
            total_volume = base_volume + variation
            
            # Simulate tissue segmentation
            gray_matter = total_volume * random.uniform(0.40, 0.45)
            white_matter = total_volume * random.uniform(0.35, 0.40)
            csf = total_volume - gray_matter - white_matter
            
            output_data = {
                "subject_id": subject_id,
                "total_brain_volume_mm3": total_volume,
                "tissue_volumes": {
                    "gray_matter_mm3": gray_matter,
                    "white_matter_mm3": white_matter,
                    "csf_mm3": csf
                },
                "tissue_ratios": {
                    "gray_matter_ratio": gray_matter / total_volume,
                    "white_matter_ratio": white_matter / total_volume,
                    "csf_ratio": csf / total_volume
                }
            }
            
            return {
                "data": output_data,
                "description": "Brain volume measurements from segmented T1w image",
                "metadata": {
                    "metrics": {
                        "total_volume": total_volume,
                        "gray_matter_volume": gray_matter,
                        "white_matter_volume": white_matter,
                        "csf_volume": csf,
                        "gray_white_ratio": gray_matter / white_matter
                    },
                    "output_bids_entities": {
                        "desc": "volume",
                        "suffix": "measurements",
                        "extension": ".json"
                    }
                }
            }
        
        # Process all subjects
        results = []
        for input_file in input_files:
            result = calculate_brain_volume(str(input_file))
            results.append(result)
        
        # Summarize results
        successful_results = [r for r in results if r.success]
        print(f"✅ Successfully processed {len(successful_results)}/{len(input_files)} subjects")
        
        # Calculate group statistics
        if successful_results:
            total_volumes = []
            for result in successful_results:
                with open(result.output_filepath, 'r') as f:
                    data = json.load(f)
                    total_volumes.append(data['total_brain_volume_mm3'])
            
            import statistics
            mean_volume = statistics.mean(total_volumes)
            std_volume = statistics.stdev(total_volumes) if len(total_volumes) > 1 else 0
            
            print(f"✅ Group mean volume: {mean_volume:.0f} ± {std_volume:.0f} mm³")
            print(f"✅ Volume range: {min(total_volumes):.0f} - {max(total_volumes):.0f} mm³")
        
        print()


if __name__ == "__main__":
    print("NeuroAnalyst NeuProcessLogic Decorator Examples")
    print("=" * 60)
    print()
    
    try:
        example_1_direct_decorator_usage()
        example_2_functional_analysis()
        example_3_neuprocesslogic_integration()
        example_4_batch_processing()
        
        print("🎉 All examples completed successfully!")
        print()
        print("Key Features Demonstrated:")
        print("• Automatic BIDS path construction")
        print("• Metadata and metrics collection")
        print("• Sidecar JSON file creation")
        print("• Error handling and validation")
        print("• Support for different data types")
        print("• Integration with NeuProcessLogic")
        print("• Batch processing capabilities")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
