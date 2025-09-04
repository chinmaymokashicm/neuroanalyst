#!/usr/bin/env python3
"""
Simple demo of the NeuProcessLogic decorator for quick testing and understanding.
"""

import sys
from pathlib import Path
import tempfile
import json

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.process.wrapper import (
    NeuProcessDecoratorConfig,
    neuprocess_decorator,
)


def simple_demo():
    """Demonstrate the basic decorator functionality."""
    
    print("🧠 NeuroAnalyst Decorator Demo")
    print("=" * 40)
    
    # Create a temporary BIDS dataset
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir)
        print(f"📁 BIDS root: {bids_root}")
        
        # Create realistic BIDS structure
        (bids_root / "sub-pilot01" / "ses-baseline" / "anat").mkdir(parents=True)
        input_file = bids_root / "sub-pilot01" / "ses-baseline" / "anat" / "sub-pilot01_ses-baseline_T1w.txt"
        input_file.write_text("# Dummy T1w neuroimaging data")
        
        print(f"📄 Input file: {input_file.name}")
        
        # Configure the decorator
        config = NeuProcessDecoratorConfig(
            pipeline_name="demo_skull_strip",
            bids_root=bids_root,
            overwrite=True
        )
        
        # Create a simple processing function
        @neuprocess_decorator(config)
        def demo_skull_stripping(input_filepath):
            """
            Demo skull stripping function.
            
            This function simulates removing non-brain tissue from T1w images
            using advanced machine learning algorithms (totally simulated here).
            """
            
            print(f"🔬 Processing: {Path(input_filepath).name}")
            
            # Simulate processing with some realistic metrics
            brain_volume_ml = 1456.7  # Brain volume in milliliters
            skull_strip_quality = 0.94  # Quality score (0-1)
            processing_time_sec = 45.2  # Simulated processing time
            
            # Create output data (in real case, this would be the processed image)
            processed_data = f"""# Skull-stripped T1w data for {Path(input_filepath).name}
# Processing completed successfully
# Brain volume: {brain_volume_ml} ml
# Quality score: {skull_strip_quality}
# Processing time: {processing_time_sec} seconds
# Method: Deep learning-based skull stripping
PROCESSED_BRAIN_DATA"""
            
            # Return structured output (matching our wrapper's expected format)
            return {
                "data": processed_data,
                "description": "Skull-stripped T1w image using deep learning",
                "metadata": {
                    "brain_volume_ml": brain_volume_ml,
                    "skull_strip_quality": skull_strip_quality,
                    "processing_time_seconds": processing_time_sec,
                    "voxel_count": 2048576,  # Number of brain voxels
                    "artifact_level": "minimal",
                    "processing_method": "Deep learning-based skull stripping",
                    "original_file": Path(input_filepath).name
                }
            }
        
        # Execute the processing
        print("⚡ Starting processing...")
        result = demo_skull_stripping(str(input_file))
        
        # Display results
        if result.success:
            print("✅ Processing completed successfully!")
            print(f"⏱️  Execution time: {result.execution_time:.3f} seconds")
            print(f"📁 Output file: {result.output_filepath.name}")
            print(f"📋 Sidecar file: {result.sidecar_filepath.name}")
            
            # Show the output data
            with open(result.output_filepath, 'r') as f:
                output_content = f.read()
            
            print("\n📊 Output Data Preview:")
            print("   " + "\n   ".join(output_content.split('\n')[:5]))  # Show first 5 lines
            
            # Show the metadata
            with open(result.sidecar_filepath, 'r') as f:
                metadata = json.load(f)
            
            print("\n📈 Processing Metrics:")
            if 'brain_volume_ml' in metadata:
                print(f"   Brain Volume: {metadata['brain_volume_ml']} ml")
            if 'skull_strip_quality' in metadata:
                print(f"   Quality Score: {metadata['skull_strip_quality']}")
            if 'processing_time_seconds' in metadata:
                print(f"   Processing Time: {metadata['processing_time_seconds']} seconds")
            
            print(f"\n🏷️  Generated filename: {result.output_filepath.name}")
            print(f"📂 Full output path: {result.output_filepath}")
            
        else:
            print(f"❌ Processing failed: {result.error_message}")
    
    print("\n🎉 Demo completed!")


if __name__ == "__main__":
    simple_demo()
