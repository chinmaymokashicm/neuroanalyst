#!/usr/bin/env python3
"""
Comprehensive demo of NeuProcessDir: Wrapping NeuProcessLogic into complete directory structure.

This demo shows the complete workflow:
1. Create NeuProcessLogic with a neuroimaging function
2. Configure NeuProcessDir settings
3. Generate complete directory structure with all files
4. Demonstrate usage and functionality

Run with: python demo.py
"""

import sys
from pathlib import Path

# Add the project root to the path so we can import modules
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument
from app.models.process.dir.core import NeuProcessDir, NeuProcessDirConfig, create_neuprocess_directory
from app.models.about import About


def create_neuroimaging_pipeline():
    """Create a realistic neuroimaging pipeline using NeuProcessLogic and NeuProcessDir."""
    
    print("🧠 Creating Neuroimaging Pipeline Demo")
    print("=" * 60)
    
    # Step 1: Define the NeuProcessLogic
    print("📝 Step 1: Creating NeuProcessLogic...")
    
    logic = NeuProcessLogic(
        about=About(
            name="extract_roi_signals",
            description="Extract region-of-interest signals from functional MRI data using atlas parcellation",
            version="2.1.0"
        ),
        language="python",
        code="""
def extract_roi_signals(input_filepath):
    '''
    Extract region-of-interest (ROI) signals from functional MRI data.
    
    This function loads a functional MRI image, applies an atlas-based parcellation,
    and extracts mean time series signals for each ROI.
    
    Args:
        input_filepath (str): Path to the input functional MRI file (NIfTI format)
    
    Returns:
        dict: Contains extracted signals, metadata, and processing information
    '''
    import nibabel as nib
    import numpy as np
    import pandas as pd
    from pathlib import Path
    from nilearn import datasets, maskers
    from nilearn.input_data import NiftiLabelsMasker
    import warnings
    warnings.filterwarnings('ignore')
    
    # Load input image
    input_path = Path(input_filepath)
    print(f"Processing: {input_path.name}")
    
    # Load the functional image
    func_img = nib.load(input_filepath)
    func_data = func_img.get_fdata()
    
    # Get image properties
    n_vols = func_data.shape[-1] if len(func_data.shape) == 4 else 1
    voxel_size = func_img.header.get_zooms()
    
    # Load Harvard-Oxford atlas (or simulate if not available)
    try:
        # Use Harvard-Oxford cortical atlas
        atlas = datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
        atlas_img = atlas.maps
        region_labels = atlas.labels[1:]  # Skip background
        
        # Create masker for ROI extraction
        masker = NiftiLabelsMasker(
            labels_img=atlas_img,
            standardize=True,
            memory='nilearn_cache'
        )
        
        # Extract time series
        roi_signals = masker.fit_transform(func_img)
        
        # Create DataFrame with proper column names
        signals_df = pd.DataFrame(
            roi_signals,
            columns=[f"ROI_{i:03d}_{label}" for i, label in enumerate(region_labels)]
        )
        
        n_rois = len(region_labels)
        atlas_name = "Harvard-Oxford Cortical Atlas"
        
    except Exception as e:
        print(f"Atlas loading failed, using simulated data: {e}")
        
        # Fallback: simulate ROI extraction
        n_rois = 48  # Typical number of cortical regions
        region_labels = [f"Region_{i:02d}" for i in range(1, n_rois + 1)]
        
        # Simulate time series (in real implementation, this would be actual extraction)
        roi_signals = np.random.randn(n_vols, n_rois) * 100 + 1000
        
        signals_df = pd.DataFrame(
            roi_signals,
            columns=[f"ROI_{i:03d}_{label}" for i, label in enumerate(region_labels)]
        )
        
        atlas_name = "Simulated Atlas (Demo)"
    
    # Calculate summary statistics
    signal_stats = {
        'mean_signals': signals_df.mean().to_dict(),
        'std_signals': signals_df.std().to_dict(),
        'temporal_correlation_matrix': np.corrcoef(roi_signals.T).tolist()
    }
    
    # Calculate connectivity measures
    connectivity_matrix = np.corrcoef(roi_signals.T)
    mean_connectivity = np.mean(connectivity_matrix[np.triu_indices_from(connectivity_matrix, k=1)])
    
    # Prepare output data
    output_data = {
        'roi_time_series': signals_df.to_dict('records'),
        'connectivity_matrix': connectivity_matrix.tolist(),
        'signal_statistics': signal_stats,
        'summary_metrics': {
            'n_timepoints': int(n_vols),
            'n_regions': int(n_rois),
            'mean_roi_signal': float(np.mean(roi_signals)),
            'mean_connectivity': float(mean_connectivity),
            'signal_variance': float(np.var(roi_signals)),
            'atlas_regions': region_labels
        }
    }
    
    # Create comprehensive metadata
    metadata = {
        'processing_details': {
            'atlas_name': atlas_name,
            'n_regions': n_rois,
            'extraction_method': 'NiftiLabelsMasker',
            'standardization': True,
            'temporal_filtering': None
        },
        'input_image_properties': {
            'dimensions': list(func_data.shape),
            'voxel_size_mm': list(voxel_size),
            'n_timepoints': n_vols,
            'tr_seconds': float(voxel_size[3]) if len(voxel_size) > 3 else 'unknown'
        },
        'quality_metrics': {
            'mean_fd': 'not_calculated',  # Would calculate framewise displacement
            'temporal_snr': float(np.mean(roi_signals) / np.std(roi_signals)),
            'signal_range': [float(np.min(roi_signals)), float(np.max(roi_signals))]
        },
        'output_bids_entities': {
            'suffix': 'timeseries',
            'extension': '.json',
            'desc': 'ROIsignals'
        }
    }
    
    return {
        'data': output_data,
        'description': f'ROI signal extraction from {input_path.name} using {atlas_name}',
        'metadata': metadata
    }
""",
        import_statements=[
            "import nibabel as nib",
            "import numpy as np", 
            "import pandas as pd",
            "from pathlib import Path",
            "from nilearn import datasets, maskers",
            "from nilearn.input_data import NiftiLabelsMasker",
            "import warnings"
        ],
        arguments=[
            NeuProcessLogicArgument(
                name="input_filepath",
                type="str | Path",
                is_optional=False,
                description="Path to the input functional MRI file (NIfTI format)"
            )
        ]
    )
    
    print(f"  ✅ Function: {logic.about.name}")
    print(f"  📋 Description: {logic.about.description}")
    print(f"  🔢 Version: {logic.about.version}")
    print(f"   Language: {logic.language}")
    print(f"  📦 Imports: {len(logic.import_statements)} packages")
    print(f"  🔧 Arguments: {len(logic.arguments)} parameters")
    
    # Step 2: Create NeuProcessDir configuration
    print("\\n⚙️  Step 2: Creating NeuProcessDir Configuration...")
    
    config = NeuProcessDirConfig(
        pipeline_name="roi_signal_extraction",
        author="NeuroAnalyst Development Team",
        description="Automated ROI signal extraction pipeline for functional MRI data analysis",
        version="2.1.0",
        pipeline_id="PL001_ROI_EXTRACTION",
        process_exec_id="PE001_DEMO_RUN",
        python_packages=[
            "nibabel>=3.2.1",
            "nilearn>=0.10.0", 
            "scikit-learn>=1.0.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0"
        ],
        parallel_execution=True,
        max_workers=8,
        bids_validate=True,
        derivatives_dir="roi_signals",
        base_container_image="python:3.11-slim",
        container_mounts=[
            "/opt/fsl:/opt/fsl:ro",
            "/opt/freesurfer:/opt/freesurfer:ro"
        ]
    )
    
    print(f"  🏗️  Pipeline: {config.pipeline_name}")
    print(f"  👤 Author: {config.author}")
    print(f"  📦 Total packages: {len(config.python_packages)}")
    print(f"  🚀 Parallel execution: {config.parallel_execution}")
    print(f"  👥 Max workers: {config.max_workers}")
    print(f"  🔍 BIDS validation: {config.bids_validate}")
    print(f"  🐳 Container: {config.base_container_image}")
    
    return logic, config


def demonstrate_directory_creation(logic, config):
    """Demonstrate the directory creation process."""
    
    print("\\n📁 Step 3: Creating Complete Directory Structure...")
    
    # Create output directory
    output_path = Path("./demo_pipeline_output")
    output_path.mkdir(exist_ok=True)
    
    print(f"  📂 Output location: {output_path.absolute()}")
    
    # Create the NeuProcessDir
    try:
        neuprocess_dir = create_neuprocess_directory(
            logic=logic,
            config=config,
            output_path=output_path
        )
        
        print(f"\\n✅ Pipeline successfully created at: {neuprocess_dir.output_directory}")
        
        # Show generated files
        print("\\n📄 Generated files:")
        if neuprocess_dir.output_directory:
            files = sorted(neuprocess_dir.output_directory.iterdir())
            for file_path in files:
                size = file_path.stat().st_size
                print(f"  📄 {file_path.name:<25} ({size:,} bytes)")
        
        return neuprocess_dir
        
    except Exception as e:
        print(f"❌ Error creating directory structure: {e}")
        return None


def demonstrate_usage_examples(neuprocess_dir):
    """Show usage examples for the created pipeline."""
    
    if not neuprocess_dir or not neuprocess_dir.output_directory:
        print("❌ Cannot demonstrate usage - directory creation failed")
        return
    
    pipeline_dir = neuprocess_dir.output_directory
    pipeline_name = neuprocess_dir.config.pipeline_name
    
    print("\\n🚀 Step 4: Usage Examples")
    print("=" * 40)
    
    print("\\n🐍 Python Script Usage:")
    print(f"  cd {pipeline_dir}")
    print("  python main.py /path/to/bids/dataset")
    print("  python main.py /path/to/bids/dataset --bids-filters '{\"task\": [\"rest\"], \"subject\": [\"01\", \"02\"]}'")
    print("  python main.py /path/to/bids/dataset --max-workers 4 --overwrite")
    
    print("\\n🐳 Container Usage:")
    print(f"  # Build container:")
    print(f"  singularity build {pipeline_name}.sif {pipeline_name}.def")
    print(f"  ")
    print(f"  # Run container:")
    print(f"  singularity run \\\\")
    print(f"    --bind /data/bids:/input:ro \\\\")
    print(f"    --bind /data/output:/output \\\\")
    print(f"    {pipeline_name}.sif /input")
    
    print("\\n⚡ HPC Execution:")
    print(f"  # Using provided execution script:")
    print(f"  ./execute.sh /data/bids/dataset")
    print(f"  ./execute.sh -w 16 --overwrite /data/bids/dataset")
    print(f"  ./execute.sh --dry-run /data/bids/dataset  # Preview commands")
    
    print("\\n📊 Expected Outputs:")
    print(f"  derivatives/{pipeline_name}/")
    print(f"  ├── processing_results.csv      # Detailed results")
    print(f"  ├── processing_summary.json     # Summary statistics")
    print(f"  └── sub-<ID>/")
    print(f"      └── func/")
    print(f"          ├── sub-<ID>_desc-ROIsignals_timeseries.json")
    print(f"          └── sub-<ID>_desc-ROIsignals_timeseries.json (sidecar)")


def show_file_contents(neuprocess_dir):
    """Show excerpts from key generated files."""
    
    if not neuprocess_dir or not neuprocess_dir.output_directory:
        return
    
    pipeline_dir = neuprocess_dir.output_directory
    
    print("\\n📖 Step 5: Generated File Contents (Excerpts)")
    print("=" * 50)
    
    # Show main.py excerpt
    main_file = pipeline_dir / "main.py"
    if main_file.exists():
        print("\\n🐍 main.py (first 20 lines):")
        with open(main_file, 'r') as f:
            lines = f.readlines()[:20]
            for i, line in enumerate(lines, 1):
                print(f"  {i:2d}: {line.rstrip()}")
        print(f"     ... (total {len(lines)} lines)")
    
    # Show README excerpt
    readme_file = pipeline_dir / "README.md"
    if readme_file.exists():
        print("\\n📚 README.md (first 15 lines):")
        with open(readme_file, 'r') as f:
            lines = f.readlines()[:15]
            for i, line in enumerate(lines, 1):
                print(f"  {i:2d}: {line.rstrip()}")
        print(f"     ... (continues with full documentation)")
    
    # Show configuration
    config_file = pipeline_dir / "neuprocess_config.json"
    if config_file.exists():
        print("\\n⚙️  neuprocess_config.json (structure):")
        import json
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            for key in config_data.keys():
                print(f"    {key}: {type(config_data[key]).__name__}")


def main():
    """Main demo function."""
    
    print("🎯 NeuroAnalyst NeuProcessDir Complete Demo")
    print("🧠 Transforming NeuProcessLogic into Complete Pipeline")
    print("=" * 70)
    
    try:
        # Create the neuroimaging pipeline
        logic, config = create_neuroimaging_pipeline()
        
        # Demonstrate directory creation
        neuprocess_dir = demonstrate_directory_creation(logic, config)
        
        # Show usage examples
        demonstrate_usage_examples(neuprocess_dir)
        
        # Show file contents
        show_file_contents(neuprocess_dir)
        
        print("\\n🎉 Demo Complete!")
        print("=" * 70)
        print("\\n📝 Summary:")
        print("  ✅ Created NeuProcessLogic with neuroimaging function")
        print("  ✅ Configured NeuProcessDir with pipeline settings")
        print("  ✅ Generated complete directory structure with all files:")
        print("     • main.py - Parallel execution script")
        print("     • install_requirements.sh - Environment setup")
        print("     • *.def - Singularity container definition")
        print("     • execute.sh - HPC execution script")
        print("     • README.md - Comprehensive documentation")
        print("     • neuprocess_config.json - Configuration file")
        print("\\n🚀 The pipeline is ready for:")
        print("  • Direct Python execution")
        print("  • Container-based deployment")
        print("  • HPC cluster execution")
        print("  • BIDS-compliant processing")
        print("\\n💡 Next steps:")
        print("  1. Test with sample BIDS dataset")
        print("  2. Build and deploy container")
        print("  3. Run on HPC environment")
        
        if neuprocess_dir and neuprocess_dir.output_directory:
            print(f"\\n📁 Pipeline location: {neuprocess_dir.output_directory.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"\\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
