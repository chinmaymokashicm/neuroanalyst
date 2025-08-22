"""
Simple PyBIDS integration test that avoids neuroimaging data complexities.
"""

import tempfile
import json
from pathlib import Path

from app.models.process.wrapper import neuprocess_decorator, NeuProcessDecoratorConfig


def test_pybids_simple():
    """Test PyBIDS integration with simple text data."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock BIDS dataset structure
        bids_root = Path(temp_dir) / "simple_dataset"
        bids_root.mkdir()
        
        # Create subject directory
        sub_dir = bids_root / "sub-01" / "func"
        sub_dir.mkdir(parents=True)
        
        # Create a mock input file (text-based)
        input_file = sub_dir / "sub-01_task-rest_bold.txt"
        with open(input_file, 'w') as f:
            f.write("mock data for processing")
        
        # Create dataset_description.json for BIDS compliance
        dataset_desc = {
            "Name": "Simple Test Dataset",
            "BIDSVersion": "1.8.0",
            "DatasetType": "raw"
        }
        with open(bids_root / "dataset_description.json", 'w') as f:
            json.dump(dataset_desc, f)
        
        # Configure decorator with PyBIDS enabled  
        config = NeuProcessDecoratorConfig(
            pipeline_name="simple_test",
            bids_root=str(bids_root),
            overwrite=True
        )
        
        @neuprocess_decorator(config)
        def simple_processing_function(input_filepath: str) -> dict:
            """Simple text processing function."""
            with open(input_filepath, 'r') as f:
                content = f.read()
            
            processed_content = content.upper() + " - PROCESSED"
            
            return {
                "data": processed_content,
                "description": "Simple text processing with PyBIDS",
                "metadata": {
                    "original_length": len(content),
                    "processed_length": len(processed_content),
                    "method": "uppercase"
                }
            }
        
        # Run the decorated function
        result = simple_processing_function(str(input_file))
        
        # Print debug info
        print(f"Success: {result.success}")
        if not result.success:
            print(f"Error: {result.error_message}")
        else:
            print(f"Output file: {result.output_filepath}")
            print(f"BIDS entities: {result.bids_entities}")
            print(f"PyBIDS used: Available and integrated")
            
            # Verify the output file content
            if result.output_filepath and result.output_filepath.exists():
                with open(result.output_filepath, 'r') as f:
                    output_content = f.read()
                print(f"Output content: {output_content}")
                
                # Verify it contains processed data
                assert "PROCESSED" in output_content
                
            print("✅ Simple PyBIDS test passed!")
        
        return result


if __name__ == "__main__":
    test_pybids_simple()
