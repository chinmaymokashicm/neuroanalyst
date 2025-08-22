#!/usr/bin/env python3
"""
Simple test of NeuProcessDir functionality without complex wrapper dependencies.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument
from app.models.about import About


def test_basic_functionality():
    """Test the basic NeuProcessDir functionality."""
    
    print("🧪 Testing NeuProcessDir Basic Functionality")
    print("=" * 50)
    
    # Create a simple test logic
    logic = NeuProcessLogic(
        about=About(
            name="simple_test_function",
            description="A simple test function",
            version="1.0.0"
        ),
        language="python",
        code="""
def simple_test_function(input_filepath):
    '''Simple test function.'''
    return {
        'data': {'result': 'success'},
        'description': 'Test completed',
        'metadata': {'test': True}
    }
""",
        import_statements=[],
        arguments=[
            NeuProcessLogicArgument(
                name="input_filepath",
                type="str",
                is_optional=False,
                description="Input file path"
            )
        ]
    )
    
    print("✅ Created NeuProcessLogic")
    print(f"  Function: {logic.about.name}")
    print(f"  Description: {logic.about.description}")
    
    # Test that we can import the core module
    try:
        from app.models.process.dir.core import NeuProcessDirConfig
        print("✅ Successfully imported NeuProcessDirConfig")
        
        config = NeuProcessDirConfig(
            pipeline_name="test_pipeline",
            author="Test Author", 
            description="Test pipeline"
        )
        print("✅ Created NeuProcessDirConfig")
        
    except Exception as e:
        print(f"❌ Error with configuration: {e}")
        return False
    
    # Test creating the directory structure without wrapper dependencies
    try:
        from app.models.process.dir.core import NeuProcessDir
        print("✅ Successfully imported NeuProcessDir")
        
        neuprocess_dir = NeuProcessDir(logic=logic, config=config)
        print("✅ Created NeuProcessDir instance")
        
        # Create output directory 
        output_path = Path("./test_output")
        output_path.mkdir(exist_ok=True)
        
        # Test directory creation
        created_dir = neuprocess_dir.create_directory(output_path)
        print(f"✅ Created directory structure at: {created_dir}")
        
        # List created files
        if created_dir.exists():
            files = list(created_dir.iterdir())
            print(f"📁 Created {len(files)} files:")
            for file in sorted(files):
                print(f"  📄 {file.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating directory: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n🎉 Basic functionality test passed!")
    else:
        print("\n💥 Basic functionality test failed!")
    sys.exit(0 if success else 1)
