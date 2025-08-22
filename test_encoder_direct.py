#!/usr/bin/env python3
"""
Simplified test to isolate the syntax error issue.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.models.about import About
from app.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument, ProgrammingLanguage
from app.models.process.logic.code.python.encoder import PythonEncoder

def test_encoder_directly():
    """Test the encoder with our problematic code."""
    
    print("🧪 Testing Encoder Directly")
    print("=" * 40)
    
    # Create the same logic that's failing
    logic = NeuProcessLogic(
        about=About(
            name="brain_volume_analysis",
            description="Calculate brain volume from structural images",
            version="2.0.0",
            author="Dr. Neuro Scientist",
            tag="volume"
        ),
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
        arguments=[
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
    )
    
    # Test encoding
    encoder = PythonEncoder()
    result = encoder.encode(logic)
    
    print(f"✅ Encoding valid: {result.is_valid}")
    print(f"✅ Errors: {result.validation_errors}")
    print("\n📄 Generated Code:")
    print("-" * 40)
    print(result.code)
    print("-" * 40)
    
    # Try to compile the code to check for syntax errors
    try:
        compile(result.code, '<string>', 'exec')
        print("✅ Code compiles successfully")
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")

if __name__ == "__main__":
    test_encoder_directly()
