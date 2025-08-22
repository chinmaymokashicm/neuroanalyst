#!/usr/bin/env python3
"""
Simple debug test for the decorator path construction.
"""

import sys
from pathlib import Path
import tempfile

# Add project root to path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.process.wrapper import (
    NeuProcessDecoratorConfig,
    neuprocess_decorator,
)


def debug_path_construction():
    """Debug the path construction issue."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir)
        print(f"BIDS root: {bids_root}")
        
        # Create BIDS structure
        (bids_root / "sub-01" / "anat").mkdir(parents=True)
        input_file = bids_root / "sub-01" / "anat" / "sub-01_T1w.nii.gz"
        input_file.write_text("dummy data")
        print(f"Input file: {input_file}")
        print(f"Input file exists: {input_file.exists()}")
        
        config = NeuProcessDecoratorConfig(
            pipeline_name="test_pipeline",
            bids_root=bids_root,
            overwrite=True
        )
        
        @neuprocess_decorator(config)
        def simple_function(input_filepath):
            print(f"Inside function, received: {input_filepath}")
            print(f"Type: {type(input_filepath)}")
            
            return {
                "data": "test output",
                "description": "Simple test processing function",
                "metadata": {
                    "metrics": {"test": 1},
                    "output_bids_entities": {"suffix": "processed", "extension": ".txt"}
                }
            }
        
        print(f"Calling function with: {str(input_file)}")
        result = simple_function(str(input_file))
        
        print(f"Result success: {result.success}")
        print(f"Result output path: {result.output_filepath}")
        print(f"Result error: {result.error_message}")


if __name__ == "__main__":
    debug_path_construction()
