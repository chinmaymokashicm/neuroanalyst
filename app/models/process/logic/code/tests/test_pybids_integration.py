"""
Test PyBIDS integration with the NeuProcess wrapper system.

This test file validates the enhanced BIDS functionality provided by PyBIDS
integration in the wrapper system.
"""

import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from app.models.process.wrapper import neuprocess_decorator, NeuProcessDecoratorConfig


def test_pybids_integration_basic():
    """Test basic PyBIDS integration with the decorator."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock BIDS dataset structure
        bids_root = Path(temp_dir) / "bids_dataset"
        bids_root.mkdir()
        
        # Create subject directory
        sub_dir = bids_root / "sub-01" / "func"
        sub_dir.mkdir(parents=True)
        
        # Create a mock input file
        # Create a simple text file instead of nifti
        input_file = sub_dir / "sub-01_task-rest_bold.txt"
        with open(input_file, 'w') as f:
            f.write("mock BOLD data for processing")
        
        # Create dataset_description.json for BIDS compliance
        dataset_desc = {
            "Name": "Test Dataset",
            "BIDSVersion": "1.8.0",
            "DatasetType": "raw"
        }
        with open(bids_root / "dataset_description.json", 'w') as f:
            json.dump(dataset_desc, f)
        
        # Configure decorator with PyBIDS enabled
        config = NeuProcessDecoratorConfig(
            pipeline_name="test_pipeline",
            bids_root=str(bids_root),
            overwrite=True
        )
        
        @neuprocess_decorator(config)
        def test_processing_function(input_filepath: str) -> dict:
            """Test processing function that returns processed data."""
            return {
                "data": "PROCESSED_BOLD_DATA_ARRAY",
                "description": "Test processing with PyBIDS",
                "metadata": {
                    "parameters": {"smoothing": 6.0},
                    "software_version": "1.0.0"
                }
            }
        
        # Run the decorated function
        result = test_processing_function(str(input_file))
        
        # Verify results
        assert result.success, f"Processing failed: {result.error_message}"
        assert result.output_filepath is not None
        assert result.output_filepath.exists()
        
        # Check BIDS entities extraction
        assert 'subject' in result.bids_entities
        assert result.bids_entities['subject'] == '01'
        assert 'task' in result.bids_entities
        assert result.bids_entities['task'] == 'rest'
        
        # Check metadata includes PyBIDS information
        assert 'BIDSEntities' in result.metadata
        assert 'DatasetName' in result.metadata
        assert 'BIDSVersion' in result.metadata
        
        # Verify output path is in derivatives
        assert 'derivatives' in str(result.output_filepath)
        assert 'test_pipeline' in str(result.output_filepath)
        
        print("✅ PyBIDS integration test passed!")
        print(f"Output path: {result.output_filepath}")
        print(f"BIDS entities: {result.bids_entities}")


def test_pybids_advanced_functionality():
    """Test advanced PyBIDS integration with complex BIDS structure."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir) / "bids_dataset"
        bids_root.mkdir()
        
        # Create subject directory
        sub_dir = bids_root / "sub-02" / "anat"
        sub_dir.mkdir(parents=True)
        
        # Create a mock input file
        input_file = sub_dir / "sub-02_ses-1_T1w.txt"
        with open(input_file, 'w') as f:
            f.write("mock T1w data")
        
        # Configure decorator for advanced PyBIDS testing
        config = NeuProcessDecoratorConfig(
            pipeline_name="advanced_test",
            bids_root=str(bids_root),
            overwrite=True
        )
        
        @neuprocess_decorator(config)
        def advanced_processing_function(input_filepath: str) -> dict:
            """Test processing function for advanced PyBIDS testing."""
            return {
                "data": "processed_T1w_data",
                "description": "Advanced PyBIDS processing test",
                "metadata": {"method": "advanced_pybids"}
            }
        
        # Run the decorated function
        result = advanced_processing_function(str(input_file))
        
        # Verify results
        assert result.success, f"Processing failed: {result.error_message}"
        assert result.output_filepath is not None
        assert result.output_filepath.exists()
        
        # Check that BIDS entities were extracted using PyBIDS
        assert 'subject' in result.bids_entities
        assert result.bids_entities['subject'] == '02'
        assert 'session' in result.bids_entities
        assert result.bids_entities['session'] == '1'
        
        # Check that PyBIDS is integrated
        assert result.metadata is not None
        
        print("✅ PyBIDS advanced test passed!")
        print(f"Output path: {result.output_filepath}")
        print(f"BIDS entities (fallback): {result.bids_entities}")


def test_pybids_entity_extraction():
    """Test comprehensive BIDS entity extraction capabilities."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        bids_root = Path(temp_dir) / "complex_dataset"
        bids_root.mkdir()
        
        # Create complex subject structure
        sub_dir = bids_root / "sub-pilot01" / "ses-baseline" / "func"
        sub_dir.mkdir(parents=True)
        
        # Create a complex BIDS filename (using .txt for text-based processing)
        input_file = sub_dir / "sub-pilot01_ses-baseline_task-nback_acq-multiband_run-02_space-MNI152NLin2009cAsym_bold.txt"
        with open(input_file, 'w') as f:
            f.write("complex BIDS data")
        
        # Create dataset description
        dataset_desc = {
            "Name": "Complex Test Dataset",
            "BIDSVersion": "1.8.0"
        }
        with open(bids_root / "dataset_description.json", 'w') as f:
            json.dump(dataset_desc, f)
        
        config = NeuProcessDecoratorConfig(
            pipeline_name="complex_pipeline",
            bids_root=str(bids_root),
            overwrite=True
        )
        
        @neuprocess_decorator(config)
        def complex_processing_function(input_filepath: str) -> dict:
            """Process complex BIDS data."""
            return {
                "data": "PROCESSED_COMPLEX_FMRI_DATA",
                "description": "Complex BIDS processing",
                "metadata": {
                    "preprocessing_steps": ["motion_correction", "spatial_smoothing"],
                    "software": "PyBIDS-enhanced NeuProcess"
                }
            }
        
        # Run processing
        result = complex_processing_function(str(input_file))
        
        # Verify comprehensive entity extraction
        expected_entities = {
            'subject': 'pilot01',
            'session': 'baseline', 
            'task': 'nback',
            'acquisition': 'multiband',
            'run': '02',
            'space': 'MNI152NLin2009cAsym'
        }
        
        for entity, expected_value in expected_entities.items():
            assert entity in result.bids_entities, f"Missing entity: {entity}"
            assert result.bids_entities[entity] == expected_value, \
                f"Entity {entity}: expected {expected_value}, got {result.bids_entities[entity]}"
        
        # Verify output path structure
        output_parts = str(result.output_filepath).split('/')
        assert 'derivatives' in output_parts
        assert 'complex_pipeline' in output_parts
        assert 'sub-pilot01' in output_parts
        assert 'ses-baseline' in output_parts
        
        print("✅ Complex entity extraction test passed!")
        print(f"Extracted entities: {result.bids_entities}")
        print(f"Output path: {result.output_filepath}")


if __name__ == "__main__":
    print("Running PyBIDS integration tests...\n")
    
    try:
        test_pybids_integration_basic()
        print()
        test_pybids_advanced_functionality()
        print()
        test_pybids_entity_extraction()
        print()
        print("🎉 All PyBIDS integration tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
