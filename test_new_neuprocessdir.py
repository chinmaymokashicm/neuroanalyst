#!/usr/bin/env python3
"""
Test script for the updated NeuProcessDir with process ID-based architecture.
"""

import tempfile
from pathlib import Path

# Add project root to path
import sys
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.models.about import About
from app.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument, ProgrammingLanguage
from app.models.process.dir.core import NeuProcessDir, NeuProcessDirConfig

def test_neuprocessdir_creation():
    """Test creating a NeuProcessDir with the new architecture."""
    
    print("🧪 Testing NeuProcessDir with Process ID Architecture")
    print("=" * 60)
    
    # Create About model with author field
    about = About(
        name="brain_volume_analysis",
        description="Calculate brain volume from structural images",
        version="2.0.0",
        author="Dr. Neuro Scientist",  # Using the new author field
        tag="volume"
    )
    
    # Create arguments
    arguments = [
        NeuProcessLogicArgument(
            name="input_file",
            type="str",
            description="Path to input structural image",
            is_optional=False
        ),
        NeuProcessLogicArgument(
            name="output_dir", 
            type="str",
            description="Output directory for results",
            is_optional=False
        )
    ]
    
    # Create NeuProcessLogic 
    logic = NeuProcessLogic(
        about=about,
        language=ProgrammingLanguage.PYTHON,
        code='''import json
from pathlib import Path

# Simple brain volume calculation  
input_path = Path(input_file)
output_path = Path(output_dir)

# Mock calculation
volume = 1234567

# Create output file
result_file = output_path / "brain_volume.json"
result_file.parent.mkdir(parents=True, exist_ok=True)

# Write output
f = open(result_file, 'w')
json.dump({"volume_mm3": volume}, f)
f.close()

# Return required values
output_data = {"volume_mm3": volume}
metrics = {"brain_volume": volume}
output_entities = {"desc": "volume", "suffix": "brain", "extension": ".json"}

return output_data, metrics, output_entities''',
        import_statements=[],
        arguments=arguments
    )
    
    # Create configuration
    config = NeuProcessDirConfig(
        python_packages=["nibabel", "scikit-image"],
        parallel_execution=True,
        max_workers=4,
        bids_validate=True
    )
    
    # Create NeuProcessDir (process_id should be auto-generated)
    print(f"✅ Creating NeuProcessDir...")
    neu_dir = NeuProcessDir(logic=logic, config=config)
    
    print(f"✅ Process ID: {neu_dir.process_id}")
    print(f"✅ Process Name: {neu_dir.process_name}")
    print(f"✅ Author: {neu_dir.author}")
    print(f"✅ Description: {neu_dir.description}")
    print(f"✅ Version: {neu_dir.version}")
    
    # Verify process ID format
    assert neu_dir.process_id.startswith("PR-"), f"Process ID should start with 'PR-', got: {neu_dir.process_id}"
    assert len(neu_dir.process_id) == 9, f"Process ID should be 9 characters, got: {len(neu_dir.process_id)}"
    
    # Test directory creation
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_process"
        print(f"✅ Creating directory structure at: {output_path}")
        
        # Create the directory structure
        actual_dir = neu_dir.create_directory(output_path)
        print(f"✅ Actual directory created at: {actual_dir}")
        
        # Verify files were created in the actual directory (subdirectory with process ID)
        expected_files = [
            "main.py",
            "install_requirements.sh", 
            "neuprocess_config.json",
            "README.md",
            f"{neu_dir.process_id}.def",  # Should use process ID for filename
            "execute.sh"
        ]
        
        for filename in expected_files:
            file_path = actual_dir / filename
            assert file_path.exists(), f"Expected file not found: {filename}"
            print(f"✅ Found: {filename}")
        
        # Check that config file contains process info instead of pipeline info
        import json
        config_path = actual_dir / "neuprocess_config.json"
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Verify the new structure
        assert "process_info" in config_data, "Config should have 'process_info' section"
        assert "process_id" in config_data["process_info"], "Config should have process_id"
        assert "process_name" in config_data["process_info"], "Config should have process_name"
        
        # Should NOT have old pipeline fields
        assert "pipeline_info" not in config_data, "Config should not have 'pipeline_info' section"
        
        print(f"✅ Process ID in config: {config_data['process_info']['process_id']}")
        print(f"✅ Process name in config: {config_data['process_info']['process_name']}")
        print(f"✅ Author in config: {config_data['process_info']['author']}")
        
        # Check README content
        readme_path = actual_dir / "README.md"
        with open(readme_path, 'r') as f:
            readme_content = f.read()
        
        # Should contain process-related text, not pipeline
        assert neu_dir.process_name in readme_content, "README should contain process name"
        assert neu_dir.process_id in readme_content, "README should contain process ID"
        assert "pipeline" not in readme_content.lower() or "process" in readme_content.lower(), "README should use process terminology"
        
        print("✅ README.md contains correct process information")
        
        # Check Singularity definition file naming
        singularity_file = actual_dir / f"{neu_dir.process_id}.def"
        assert singularity_file.exists(), f"Singularity file should be named {neu_dir.process_id}.def"
        print(f"✅ Singularity definition file correctly named: {neu_dir.process_id}.def")

if __name__ == "__main__":
    test_neuprocessdir_creation()
    print("\n🎉 All tests passed! NeuProcessDir with Process ID architecture is working correctly.")
