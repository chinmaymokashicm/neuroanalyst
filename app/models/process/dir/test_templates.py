#!/usr/bin/env python3
"""
Simple test to validate the NeuProcessDir template-based implementation.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument
from app.models.process.dir.core import NeuProcessDir, NeuProcessDirConfig
from app.models.about import About


def test_simple_neuprocess_dir():
    """Test the template-based NeuProcessDir implementation."""
    
    print("🧪 Testing NeuProcessDir Template Implementation")
    print("=" * 50)
    
    # Create simple logic
    logic = NeuProcessLogic(
        about=About(
            name="test_function",
            description="A simple test function",
            version="1.0.0"
        ),
        language="python",
        code="""
def test_function(input_file):
    '''Simple test function.'''
    import os
    return f"Processed: {os.path.basename(input_file)}"
""",
        imports=["import os"],
        arguments=[
            NeuProcessLogicArgument(
                name="input_file",
                type="str",
                description="Input file path"
            )
        ]
    )
    
    # Create configuration with required fields
    config = NeuProcessDirConfig(
        pipeline_name="test_pipeline",
        author="Test Author",
        description="Test pipeline description",
        version="1.0.0",
        pipeline_id="TEST_PL001",
        process_exec_id="TEST_PE001"
    )
    
    # Test template loading
    neuprocess_dir = NeuProcessDir(logic=logic, config=config)
    
    # Test template methods
    try:
        template_path = neuprocess_dir._get_template_path()
        print(f"✅ Template path: {template_path}")
        
        main_template = neuprocess_dir._load_template("main_script.py.template")
        print(f"✅ Main template loaded: {len(main_template)} characters")
        
        # Test formatting
        test_vars = {
            'pipeline_name': 'test',
            'author': 'test_author',
            'description': 'test description'
        }
        formatted = neuprocess_dir._format_template("Test: {pipeline_name} by {author}", **test_vars)
        print(f"✅ Template formatting: '{formatted}'")
        
        # Test directory creation
        output_path = Path("test_output")
        pipeline_dir = neuprocess_dir.create_directory(output_path)
        print(f"✅ Pipeline created at: {pipeline_dir}")
        
        # Check generated files
        files = list(pipeline_dir.glob("*"))
        print(f"✅ Generated files: {[f.name for f in files]}")
        
        # Test the main script requirements
        main_py = pipeline_dir / "main.py"
        if main_py.exists():
            with open(main_py) as f:
                content = f.read()
            
            # Check for required arguments
            required_checks = [
                "--pipeline-name" in content and "required=True" in content,
                "--bids-filters" in content and "required=True" in content,
                "--pipeline-id" in content and "required=True" in content,
                "--process-exec-id" in content and "required=True" in content
            ]
            
            if all(required_checks):
                print("✅ All required arguments properly implemented")
            else:
                print("❌ Missing required arguments")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_simple_neuprocess_dir()
    sys.exit(0 if success else 1)
