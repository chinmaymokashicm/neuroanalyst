#!/usr/bin/env python3
"""
Test script to verify NeuroAnalyst constants and environment setup.

This script tests the constants module and ensures that all environment
variables are properly configured.
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from utils.constants import PATHS, CONFIG, validate_environment, ensure_directories
    
    def test_environment_validation():
        """Test environment validation."""
        print("Testing environment validation...")
        is_valid = validate_environment()
        print(f"Environment valid: {is_valid}")
        return is_valid
    
    def test_paths():
        """Test path configuration."""
        print("\nTesting path configuration...")
        
        paths_to_test = {
            'Home': PATHS.home,
            'Images': PATHS.images,
            'Base Images': PATHS.base_images,
            'Process Images': PATHS.process_images,
            'Pipeline Images': PATHS.pipeline_images,
            'Docs': PATHS.docs,
            'Working Directory': PATHS.workdir,
            'Reports': PATHS.reports,
            'Logs': PATHS.logs,
            'Datasets': PATHS.datasets
        }
        
        for name, path in paths_to_test.items():
            print(f"{name}: {path}")
        
        return True
    
    def test_directory_creation():
        """Test directory creation."""
        print("\nTesting directory creation...")
        try:
            ensure_directories()
            print("Directories created successfully!")
            
            # Verify some key directories exist
            key_dirs = [PATHS.home, PATHS.images, PATHS.workdir]
            for directory in key_dirs:
                if directory.exists():
                    print(f"✓ {directory} exists")
                else:
                    print(f"✗ {directory} does not exist")
            
            return True
        except Exception as e:
            print(f"Error creating directories: {e}")
            return False
    
    def test_config_constants():
        """Test configuration constants."""
        print("\nTesting configuration constants...")
        
        config_items = {
            'Singularity Extension': CONFIG.SINGULARITY_EXTENSION,
            'Python Extension': CONFIG.PYTHON_EXTENSION,
            'Main Script Name': CONFIG.MAIN_SCRIPT_NAME,
            'Install Script Name': CONFIG.INSTALL_SCRIPT_NAME,
            'Default Python Version': CONFIG.DEFAULT_PYTHON_VERSION,
            'Default Base Image': CONFIG.DEFAULT_BASE_IMAGE
        }
        
        for name, value in config_items.items():
            print(f"{name}: {value}")
        
        return True
    
    def test_helper_methods():
        """Test helper methods."""
        print("\nTesting helper methods...")
        
        # Test process workdir
        process_workdir = PATHS.get_process_workdir('test_process_123')
        print(f"Process workdir: {process_workdir}")
        
        # Test pipeline workdir
        pipeline_workdir = PATHS.get_pipeline_workdir('test_pipeline_456')
        print(f"Pipeline workdir: {pipeline_workdir}")
        
        # Test process image path
        process_image = PATHS.get_process_image_path('my_process', 'v1.0')
        print(f"Process image path: {process_image}")
        
        # Test base image path
        base_image = PATHS.get_base_image_path('ubuntu22.04')
        print(f"Base image path: {base_image}")
        
        # Test log file path
        log_file = PATHS.get_log_file_path('neuprocess', 'proc_123')
        print(f"Log file path: {log_file}")
        
        return True
    
    def main():
        """Main test function."""
        print("NeuroAnalyst Constants Test")
        print("=" * 50)
        
        tests = [
            test_environment_validation,
            test_paths,
            test_directory_creation,
            test_config_constants,
            test_helper_methods
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                    print("✓ PASSED\n")
                else:
                    print("✗ FAILED\n")
            except Exception as e:
                print(f"✗ ERROR: {e}\n")
        
        print("=" * 50)
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("All tests passed! ✓")
            return 0
        else:
            print("Some tests failed! ✗")
            return 1

    if __name__ == "__main__":
        sys.exit(main())

except ImportError as e:
    print(f"Error importing constants module: {e}")
    print("Make sure you have run setup.sh to configure the environment.")
    sys.exit(1)
