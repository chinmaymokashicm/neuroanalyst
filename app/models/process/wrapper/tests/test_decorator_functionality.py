#!/usr/bin/env python3
"""
Test script for the NeuProcessLogic decorator functionality.

This script demonstrates how to use the decorator to wrap user-defined functions
and automatically handle BIDS path construction, metadata writing, and output organization.
"""

import sys
import os
import json
from pathlib import Path
import tempfile
import shutil

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
    NeuProcessResult,
    neuprocess_decorator,
    create_neuprocess_function,
)
from app.models.about import About


def test_decorator_basic_usage():
    """Test basic decorator usage with a simple function."""
    print("=== Testing Basic Decorator Usage ===\n")
    
    # Create a temporary BIDS directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir)
        
        # Create basic BIDS structure
        (bids_root / "sub-01" / "anat").mkdir(parents=True)
        input_file = bids_root / "sub-01" / "anat" / "sub-01_T1w.nii.gz"
        input_file.write_text("dummy input data")  # Create dummy input file
        
        # Configure decorator
        config = NeuProcessDecoratorConfig(
            pipeline_name="test_pipeline",
            bids_root=bids_root,
            overwrite=True
        )
        
        # Define a test function using the decorator
        @neuprocess_decorator(config)
        def simple_processing(input_filepath):
            """Simple processing function that doubles the input."""
            # Simulate some processing
            processed_data = f"Processed: {Path(input_filepath).name}"
            
            return {
                "data": processed_data,
                "description": "Simple text processing with doubling effect",
                "metadata": {
                    "metrics": {"processing_factor": 2.0, "success_rate": 1.0},
                    "output_bids_entities": {"suffix": "processed", "extension": ".txt"}
                }
            }
        
        # Execute the function
        print(f"Processing file: {input_file}")
        result = simple_processing(str(input_file))
        
        print(f"✅ Success: {result.success}")
        print(f"✅ Output file: {result.output_filepath}")
        print(f"✅ Sidecar file: {result.sidecar_filepath}")
        print(f"✅ Execution time: {result.execution_time:.4f}s")
        
        # Verify files were created
        assert result.output_filepath.exists(), f"Output file not created: {result.output_filepath}"
        assert result.sidecar_filepath.exists(), f"Sidecar file not created: {result.sidecar_filepath}"
        
        # Check output content
        with open(result.output_filepath, 'r') as f:
            content = f.read()
            print(f"✅ Output content: {content}")
        
        print()


def test_neuprocess_logic_integration():
    """Test integration with NeuProcessLogic for automatic function generation."""
    print("=== Testing NeuProcessLogic Integration ===\n")
    
    # Create a temporary BIDS directory
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir)
        
        # Create BIDS structure
        (bids_root / "sub-02" / "func").mkdir(parents=True)
        input_file = bids_root / "sub-02" / "func" / "sub-02_task-rest_bold.nii.gz"
        input_file.write_text("dummy BOLD data")
        
        # Define NeuProcessLogic
        logic = NeuProcessLogic(
            about=About(
                name="calculate_mean_signal",
                description="Calculate mean signal from BOLD data",
                version="1.0.0"
            ),
            language=ProgrammingLanguage.PYTHON,
            code="""
# Simulate BOLD signal processing
from pathlib import Path

# Read input file (simulation)
input_path = Path(input_filepath)
print(f"Processing {input_path.name}")

# Simulate calculating mean signal
mean_signal = 42.5
std_signal = 12.3

# Prepare output data
output_data = {
    "mean_signal": mean_signal,
    "std_signal": std_signal,
    "input_file": str(input_path.name)
}

# Prepare metrics
metrics = {
    "mean_signal": mean_signal,
    "std_signal": std_signal,
    "snr": mean_signal / std_signal
}

# Prepare BIDS entities for output
output_entities = {
    "suffix": "meansignal",
    "extension": ".json"
}

return output_data, metrics, output_entities
            """,
            import_statements=["from pathlib import Path"],
            arguments=[
                NeuProcessLogicArgument(
                    name="input_filepath",
                    type="str",
                    is_optional=False,
                    description="Path to input BOLD file"
                )
            ]
        )
        
        # Configure decorator
        config = NeuProcessDecoratorConfig(
            pipeline_name="bold_analysis",
            bids_root=bids_root,
            overwrite=True
        )
        
        # Create the decorated function
        print("Creating function from NeuProcessLogic...")
        decorated_func = create_neuprocess_function(logic, config)
        
        # Execute the function
        print(f"Processing file: {input_file}")
        result = decorated_func(str(input_file))
        
        print(f"✅ Success: {result.success}")
        print(f"✅ Output file: {result.output_filepath}")
        print(f"✅ Execution time: {result.execution_time:.4f}s")
        
        # Verify output
        if result.success:
            with open(result.output_filepath, 'r') as f:
                content = f.read()
                print(f"✅ Output file content: {content}")
                try:
                    output_data = json.loads(content)
                    print(f"✅ Mean signal: {output_data['mean_signal']}")
                except json.JSONDecodeError as e:
                    print(f"⚠️  Could not parse JSON: {e}")
                except KeyError as e:
                    print(f"⚠️  Key not found: {e}")
                    print(f"Available keys: {list(output_data.keys()) if isinstance(output_data, dict) else 'Not a dict'}")
        else:
            print(f"❌ Processing failed: {result.error_message}")
        
        print()


def test_error_handling():
    """Test error handling in the decorator."""
    print("=== Testing Error Handling ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir)
        
        config = NeuProcessDecoratorConfig(
            pipeline_name="error_test",
            bids_root=bids_root,
            overwrite=True
        )
        
        @neuprocess_decorator(config)
        def failing_function(input_filepath):
            """Function that always fails."""
            raise ValueError("This function always fails!")
        
        # Execute the failing function
        result = failing_function("dummy_path.txt")
        
        print(f"✅ Success: {result.success}")
        print(f"✅ Error message: {result.error_message}")
        print(f"✅ Execution time: {result.execution_time:.4f}s")
        
        assert not result.success, "Function should have failed"
        assert "always fails" in result.error_message, "Error message should contain expected text"
        
        print()


def test_overwrite_behavior():
    """Test overwrite behavior."""
    print("=== Testing Overwrite Behavior ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir)
        
        # Create input structure
        (bids_root / "sub-03" / "anat").mkdir(parents=True)
        input_file = bids_root / "sub-03" / "anat" / "sub-03_T1w.nii.gz"
        input_file.write_text("dummy data")
        
        # Configure without overwrite
        config_no_overwrite = NeuProcessDecoratorConfig(
            pipeline_name="overwrite_test",
            bids_root=bids_root,
            overwrite=False
        )
        
        @neuprocess_decorator(config_no_overwrite)
        def test_function(input_filepath):
            return {
                "data": "test data",
                "description": "Test function for overwrite behavior",
                "metadata": {
                    "metrics": {},
                    "output_bids_entities": {"suffix": "test", "extension": ".txt"}
                }
            }
        
        # First execution should succeed
        result1 = test_function(str(input_file))
        print(f"✅ First execution success: {result1.success}")
        
        # Second execution should fail (file exists, overwrite=False)
        result2 = test_function(str(input_file))
        print(f"✅ Second execution success: {result2.success}")
        print(f"✅ Error message: {result2.error_message}")
        
        assert result1.success, "First execution should succeed"
        assert not result2.success, "Second execution should fail due to existing file"
        assert "already exists" in result2.error_message, "Error should mention file exists"
        
        print()


if __name__ == "__main__":
    print("NeuroAnalyst NeuProcessLogic Decorator Tests")
    print("=" * 50)
    print()
    
    try:
        test_decorator_basic_usage()
        test_neuprocess_logic_integration()
        test_error_handling()
        test_overwrite_behavior()
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
