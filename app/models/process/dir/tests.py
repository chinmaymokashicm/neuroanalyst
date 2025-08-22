"""
Test suite for NeuProcessDir functionality.
Tests the complete workflow from NeuProcessLogic to directory structure creation.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from app.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument
from app.models.process.dir.core import NeuProcessDir, NeuProcessDirConfig, create_neuprocess_directory
from app.models.about import About


class TestNeuProcessDir(unittest.TestCase):
    """Test cases for NeuProcessDir functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test logic
        self.test_logic = NeuProcessLogic(
            about=About(
                name="test_processing_function",
                description="A test processing function for unit testing",
                version="1.0.0",
                author="Test Author"
            ),
            language="python",
            code="""
def test_processing_function(input_filepath):
    '''Test processing function for unit testing.'''
    from pathlib import Path
    import json
    
    # Simple processing simulation
    input_path = Path(input_filepath)
    
    output_data = {
        'processed_file': str(input_path.name),
        'file_size': input_path.stat().st_size if input_path.exists() else 0,
        'processing_status': 'completed'
    }
    
    metadata = {
        'processing_method': 'test_processing',
        'output_bids_entities': {
            'suffix': 'processed',
            'extension': '.json'
        }
    }
    
    return {
        'data': output_data,
        'description': f'Test processing of {input_path.name}',
        'metadata': metadata
    }
""",
            import_statements=["from pathlib import Path", "import json"],
            arguments=[
                NeuProcessLogicArgument(
                    name="input_filepath",
                    type="str | Path",
                    is_optional=False,
                    description="Path to the input file"
                )
            ]
        )
        
        # Create test configuration
        self.test_config = NeuProcessDirConfig(
            pipeline_name="test_pipeline",
            author="Test Author",
            description="Test pipeline for unit testing",
            version="1.0.0",
            python_packages=["numpy", "pandas"],
            parallel_execution=True,
            max_workers=2,
            base_container_image="python:3.12-slim"
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)
    
    def test_neuprocess_dir_creation(self):
        """Test creating a NeuProcessDir instance."""
        neuprocess_dir = NeuProcessDir(
            logic=self.test_logic,
            config=self.test_config
        )
        
        self.assertEqual(neuprocess_dir.logic.about.name, "test_processing_function")
        self.assertEqual(neuprocess_dir.config.pipeline_name, "test_pipeline")
        self.assertIsNone(neuprocess_dir.output_directory)
    
    def test_directory_structure_creation(self):
        """Test creating the complete directory structure."""
        neuprocess_dir = NeuProcessDir(
            logic=self.test_logic,
            config=self.test_config
        )
        
        # Create the directory structure
        created_dir = neuprocess_dir.create_directory(self.temp_path)
        
        # Verify the directory was created
        self.assertTrue(created_dir.exists())
        self.assertEqual(created_dir.name, "test_pipeline")
        self.assertEqual(neuprocess_dir.output_directory, created_dir)
        
        # Verify required files were created
        expected_files = [
            "main.py",
            "install_requirements.sh", 
            "neuprocess_config.json",
            "README.md",
            "test_pipeline.def",
            "execute.sh"
        ]
        
        for filename in expected_files:
            file_path = created_dir / filename
            self.assertTrue(file_path.exists(), f"File {filename} not created")
            self.assertGreater(file_path.stat().st_size, 0, f"File {filename} is empty")
    
    def test_main_script_content(self):
        """Test that the main.py script contains expected content."""
        neuprocess_dir = NeuProcessDir(
            logic=self.test_logic,
            config=self.test_config
        )
        created_dir = neuprocess_dir.create_directory(self.temp_path)
        
        main_script = created_dir / "main.py"
        content = main_script.read_text()
        
        # Verify key components are present
        self.assertIn("test_processing_function", content)
        self.assertIn("Test processing function for unit testing", content)
        self.assertIn("import argparse", content)
        self.assertIn("from bids import BIDSLayout", content)
        self.assertIn("ProcessPoolExecutor", content)
        self.assertIn("test_pipeline", content)
    
    def test_requirements_script_content(self):
        """Test that the install_requirements.sh script contains expected packages."""
        neuprocess_dir = NeuProcessDir(
            logic=self.test_logic,
            config=self.test_config
        )
        created_dir = neuprocess_dir.create_directory(self.temp_path)
        
        requirements_script = created_dir / "install_requirements.sh"
        content = requirements_script.read_text()
        
        # Verify packages are included
        self.assertIn("numpy", content)
        self.assertIn("pandas", content)
        self.assertIn("pybids", content)
        self.assertIn("#!/bin/bash", content)
        self.assertIn("python3 -m pip install", content)
        
        # Verify script is executable
        self.assertTrue(os.access(requirements_script, os.X_OK))
    
    def test_config_file_content(self):
        """Test that the configuration file contains correct information."""
        neuprocess_dir = NeuProcessDir(
            logic=self.test_logic,
            config=self.test_config
        )
        created_dir = neuprocess_dir.create_directory(self.temp_path)
        
        config_file = created_dir / "neuprocess_config.json"
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        # Verify configuration structure
        self.assertIn("pipeline_info", config_data)
        self.assertIn("processing_logic", config_data)
        self.assertIn("execution_config", config_data)
        self.assertIn("environment", config_data)
        
        # Verify specific values
        self.assertEqual(config_data["pipeline_info"]["name"], "test_pipeline")
        self.assertEqual(config_data["processing_logic"]["function_name"], "test_processing_function")
        self.assertEqual(config_data["execution_config"]["parallel_execution"], True)
        self.assertIn("numpy", config_data["environment"]["python_packages"])
    
    def test_singularity_def_content(self):
        """Test that the Singularity definition file contains expected content."""
        neuprocess_dir = NeuProcessDir(
            logic=self.test_logic,
            config=self.test_config
        )
        created_dir = neuprocess_dir.create_directory(self.temp_path)
        
        def_file = created_dir / "test_pipeline.def"
        content = def_file.read_text()
        
        # Verify key components
        self.assertIn("Bootstrap: docker", content)
        self.assertIn("From: python:3.12-slim", content)
        self.assertIn("Author Test Author", content)
        self.assertIn("Pipeline test_pipeline", content)
        self.assertIn("%post", content)
        self.assertIn("%runscript", content)
        self.assertIn("/opt/neuprocess/main.py", content)
    
    def test_execute_script_content(self):
        """Test that the execute.sh script contains expected functionality."""
        neuprocess_dir = NeuProcessDir(
            logic=self.test_logic,
            config=self.test_config
        )
        created_dir = neuprocess_dir.create_directory(self.temp_path)
        
        execute_script = created_dir / "execute.sh"
        content = execute_script.read_text()
        
        # Verify key components
        self.assertIn("#!/bin/bash", content)
        self.assertIn("singularity run", content)
        self.assertIn("test_pipeline", content)
        self.assertIn("--bind", content)
        self.assertIn("show_help()", content)
        
        # Verify script is executable
        self.assertTrue(os.access(execute_script, os.X_OK))
    
    def test_readme_content(self):
        """Test that the README.md file contains comprehensive documentation."""
        neuprocess_dir = NeuProcessDir(
            logic=self.test_logic,
            config=self.test_config
        )
        created_dir = neuprocess_dir.create_directory(self.temp_path)
        
        readme_file = created_dir / "README.md"
        content = readme_file.read_text()
        
        # Verify key sections
        self.assertIn("# test_pipeline", content)
        self.assertIn("Test Author", content)
        self.assertIn("## Usage", content)
        self.assertIn("## Arguments", content)
        self.assertIn("## Function Arguments", content)
        self.assertIn("## Environment", content)
        self.assertIn("test_processing_function", content)
        self.assertIn("python main.py", content)
    
    def test_convenience_function(self):
        """Test the convenience function for creating NeuProcessDir."""
        created_dir_path = create_neuprocess_directory(
            logic=self.test_logic,
            config=self.test_config,
            output_path=self.temp_path
        ).output_directory
        
        self.assertTrue(created_dir_path.exists())
        self.assertEqual(created_dir_path.name, "test_pipeline")
        
        # Verify files were created
        self.assertTrue((created_dir_path / "main.py").exists())
        self.assertTrue((created_dir_path / "README.md").exists())
    
    def test_config_validation(self):
        """Test configuration validation and package merging."""
        config = NeuProcessDirConfig(
            pipeline_name="validation_test",
            author="Test",
            description="Test",
            python_packages=["custom_package"]
        )
        
        # Base packages should be automatically included
        self.assertIn("pybids", config.python_packages)
        self.assertIn("custom_package", config.python_packages)
        
        # Should not have duplicates
        package_counts = {}
        for pkg in config.python_packages:
            package_counts[pkg] = package_counts.get(pkg, 0) + 1
        
        for pkg, count in package_counts.items():
            self.assertEqual(count, 1, f"Package {pkg} appears {count} times")


class TestNeuProcessDirEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures.""" 
        import shutil
        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)
    
    def test_invalid_logic_encoding(self):
        """Test handling of invalid NeuProcessLogic."""
        # Create logic with invalid code
        invalid_logic = NeuProcessLogic(
            about=About(
                name="invalid_function",
                description="Invalid function for testing",
                version="1.0.0",
                author="Test"
            ),
            language="python",
            code="def invalid_function(: # Syntax error",
            import_statements=[],
            arguments=[]
        )
        
        config = NeuProcessDirConfig(
            pipeline_name="invalid_test",
            author="Test",
            description="Test invalid logic"
        )
        
        neuprocess_dir = NeuProcessDir(logic=invalid_logic, config=config)
        
        # Should raise an error during directory creation
        with self.assertRaises(ValueError):
            neuprocess_dir.create_directory(self.temp_path)
    
    def test_empty_package_list(self):
        """Test handling of empty package lists."""
        config = NeuProcessDirConfig(
            pipeline_name="empty_packages_test",
            author="Test", 
            description="Test empty packages",
            python_packages=[],
            base_packages=[]
        )
        
        # Should still include base packages due to validation
        self.assertGreater(len(config.python_packages), 0)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestNeuProcessDir))
    test_suite.addTest(unittest.makeSuite(TestNeuProcessDirEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Running NeuProcessDir Tests")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\\n✅ All tests passed!")
    else:
        print("\\n❌ Some tests failed!")
        exit(1)
