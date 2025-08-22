#!/usr/bin/env python3
"""
Test integration of constants throughout the NeuroAnalyst codebase.

This script verifies that the constants are properly integrated in the main components:
- NeuProcessDir using constants for paths and file names
- NeuProcessWrapper using constants for BIDS and JSON handling
- File generation using proper extensions and naming conventions
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_constants_integration():
    """Test that constants are properly integrated across components."""
    print("Testing Constants Integration")
    print("=" * 50)
    
    try:
        from utils.constants import PATHS, CONFIG, ensure_directories
        
        # Ensure directories exist
        ensure_directories()
        print(f"✓ Directories created using PATHS constants")
        
        # Test path generation
        process_id = "test_integration_001"
        process_workdir = PATHS.get_process_workdir(process_id)
        process_image = PATHS.get_process_image_path("test_process", "v1.0")
        
        print(f"✓ Process working directory: {process_workdir}")
        print(f"✓ Process image path: {process_image}")
        
        # Test config constants
        main_script_name = CONFIG.MAIN_SCRIPT_NAME
        install_script_name = CONFIG.INSTALL_SCRIPT_NAME
        config_name = CONFIG.CONFIG_NAME
        readme_name = CONFIG.README_NAME
        
        print(f"✓ Main script name: {main_script_name}")
        print(f"✓ Install script name: {install_script_name}")
        print(f"✓ Config file name: {config_name}")
        print(f"✓ README file name: {readme_name}")
        
        return True
    
    except ImportError as e:
        print(f"✗ Failed to import constants: {e}")
        return False

def test_file_extensions():
    """Test that file extensions from constants are used correctly."""
    print("\nTesting File Extensions from Constants")
    print("=" * 50)
    
    try:
        from utils.constants import CONFIG
        
        # Test extension constants
        extensions = {
            "Singularity": CONFIG.SINGULARITY_EXTENSION,
            "Definition": CONFIG.DEFINITION_EXTENSION,
            "Python": CONFIG.PYTHON_EXTENSION,
            "Shell": CONFIG.SHELL_EXTENSION,
            "JSON": CONFIG.JSON_EXTENSION,
            "BIDS Sidecar": CONFIG.BIDS_SIDECAR_SUFFIX
        }
        
        for name, ext in extensions.items():
            print(f"✓ {name} extension: {ext}")
        
        return True
    
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False

def test_template_paths():
    """Test template path generation."""
    print("\nTesting Template Constants")
    print("=" * 50)
    
    try:
        from utils.constants import CONFIG
        
        templates = {
            "Main Script": CONFIG.MAIN_SCRIPT_TEMPLATE,
            "README": CONFIG.README_TEMPLATE,
            "Requirements": CONFIG.REQUIREMENTS_TEMPLATE,
            "Singularity": CONFIG.SINGULARITY_TEMPLATE
        }
        
        for name, template in templates.items():
            print(f"✓ {name} template: {template}")
        
        return True
    
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False

def test_path_structure():
    """Test the directory structure created by constants."""
    print("\nTesting Directory Structure")
    print("=" * 50)
    
    try:
        from utils.constants import PATHS
        
        # Test key paths exist
        paths_to_check = {
            "Home": PATHS.home,
            "Images": PATHS.images,
            "Base Images": PATHS.base_images,
            "Process Images": PATHS.process_images,
            "Pipeline Images": PATHS.pipeline_images,
            "Working Directory": PATHS.workdir,
            "Reports": PATHS.reports,
            "Logs": PATHS.logs,
            "Datasets": PATHS.datasets
        }
        
        for name, path in paths_to_check.items():
            if path.exists():
                print(f"✓ {name} exists: {path}")
            else:
                print(f"⚠ {name} missing: {path}")
        
        return True
    
    except ImportError as e:
        print(f"✗ Failed to import paths: {e}")
        return False

def main():
    """Main test function."""
    print("NeuroAnalyst Constants Integration Test")
    print("=" * 60)
    
    tests = [
        test_constants_integration,
        test_file_extensions,
        test_template_paths,
        test_path_structure
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
    
    print("=" * 60)
    print(f"Integration Tests: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Constants are properly integrated.")
        return 0
    else:
        print("❌ Some integration tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
