"""
Example demonstrating how to use NeuProcessDir to wrap NeuProcessLogic 
into a complete directory structure with parallel execution capabilities.
"""

import sys
from pathlib import Path

# Add the project root to the path so we can import modules
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument
from app.models.process.dir.core import NeuProcessDir, NeuProcessDirConfig, create_neuprocess_directory
from app.models.about import About


def create_example_brain_analysis():
    """Create an example brain analysis NeuProcessLogic and wrap it with NeuProcessDir."""
    
    # Define the processing logic
    logic = NeuProcessLogic(
        about=About(
            name="brain_volume_analysis",
            description="Extract brain volume measurements from T1-weighted images using FSL",
            version="1.0.0",
            author="Example Author"
        ),
        language="python",
        code="""
def brain_volume_analysis(input_filepath):
    '''
    Extract brain volume measurements from T1-weighted images.
    
    This function performs brain extraction and volume calculation
    using FSL tools and returns volume metrics.
    '''
    # Load the input image
    img = nib.load(input_filepath)
    data = img.get_fdata()
    
    # Simple brain volume calculation (placeholder for actual FSL processing)
    # In a real implementation, this would use FSL bet and other tools
    non_zero_voxels = np.count_nonzero(data)
    voxel_volume = np.prod(img.header.get_zooms())
    brain_volume = non_zero_voxels * voxel_volume
    
    # Simulate additional metrics
    total_volume = np.prod(data.shape) * voxel_volume
    brain_fraction = brain_volume / total_volume
    
    # Create output data
    output_data = {
        'brain_volume_mm3': float(brain_volume),
        'total_volume_mm3': float(total_volume),
        'brain_fraction': float(brain_fraction),
        'non_zero_voxels': int(non_zero_voxels),
        'voxel_dimensions': img.header.get_zooms()[:3].tolist(),
        'image_shape': list(data.shape)
    }
    
    # Create metadata
    metadata = {
        'processing_method': 'FSL-based brain volume analysis',
        'software_version': '1.0.0',
        'voxel_volume_mm3': float(voxel_volume),
        'processing_parameters': {
            'brain_extraction': 'bet',
            'threshold': 0.5
        },
        'output_bids_entities': {
            'suffix': 'volumes',
            'extension': '.json'
        }
    }
    
    return {
        'data': output_data,
        'description': f'Brain volume analysis of {Path(input_filepath).name}',
        'metadata': metadata
    }
""",
        import_statements=[
            "import nibabel as nib",
            "import numpy as np",
            "from pathlib import Path",
            "import subprocess",
            "import tempfile",
            "import json"
        ],
        arguments=[
            NeuProcessLogicArgument(
                name="input_filepath",
                type="str | Path",
                is_optional=False,
                description="Path to the input T1-weighted image file"
            )
        ]
    )
    
    # Define the directory configuration
    config = NeuProcessDirConfig(
        pipeline_name="brain_volume_pipeline",
        author="NeuroAnalyst Team",
        description="Automated brain volume analysis pipeline using FSL tools",
        version="1.0.0",
        pipeline_id="PL001_BRAIN_VOLUME",
        process_exec_id="PE001_EXAMPLE_RUN",
        python_packages=[
            "nibabel",
            "nilearn", 
            "scipy",
            "matplotlib",
            "seaborn"
        ],
        parallel_execution=True,
        max_workers=4,
        bids_validate=False,
        base_container_image="python:3.12-slim"
    )
    
    return logic, config


def main():
    """Main example function."""
    print("🧠 Creating NeuProcessDir Example: Brain Volume Analysis")
    print("=" * 60)
    
    # Create the example logic and configuration
    logic, config = create_example_brain_analysis()
    
    print(f"📝 Logic Function: {logic.about.name}")
    print(f"📋 Description: {logic.about.description}")
    print(f"🐍 Language: {logic.language}")
    print(f"📦 Required packages: {', '.join(config.python_packages[:5])}...")
    print()
    
    # Create output directory
    output_path = Path("./example_pipelines")
    output_path.mkdir(exist_ok=True)
    
    print(f"📁 Creating pipeline directory in: {output_path}")
    
    # Create the NeuProcessDir
    try:
        neuprocess_dir = create_neuprocess_directory(
            logic=logic,
            config=config,
            output_path=output_path
        )
        
        print(f"\\n✅ Successfully created pipeline at: {neuprocess_dir.output_directory}")
        print()
        print("📄 Generated files:")
        
        if neuprocess_dir.output_directory:
            for file_path in sorted(neuprocess_dir.output_directory.iterdir()):
                print(f"  📄 {file_path.name}")
        
        print()
        print("🚀 Usage examples:")
        print(f"  cd {neuprocess_dir.output_directory}")
        print("  # Build container:")
        print(f"  singularity build {config.pipeline_name}.sif {config.pipeline_name}.def")
        print("  # Run pipeline:")
        print("  python main.py /path/to/bids/dataset")
        print("  # Or use execution script:")
        print("  ./execute.sh /path/to/bids/dataset")
        
    except Exception as e:
        print(f"❌ Error creating pipeline: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\\n🎉 Example completed successfully!")
    else:
        print("\\n💥 Example failed!")
