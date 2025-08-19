"""
Test script to verify the restructured Python encoder/decoder functionality.
"""

import sys
import os

# Add the project root to the path for imports
# This works whether running from root dir or tests dir
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument, ProgrammingLanguage
from app.models.about import About
from app.models.process.logic.code.python import (
    PythonEncoder, 
    PythonDecoder, 
    PythonEncoderConfig, 
    PythonDecoderConfig,
    encode_logic,
    decode_from_string
)


def test_basic_functionality():
    """Test basic encoding and decoding functionality."""
    
    # Create a sample NeuProcessLogic object
    about = About(
        name="test_function",
        description="A simple test function that adds two numbers",
        version="1.0.0"
    )
    
    arguments = [
        NeuProcessLogicArgument(
            name="a",
            type="int",
            is_optional=False,
            description="First number to add"
        ),
        NeuProcessLogicArgument(
            name="b",
            type="int",
            is_optional=False,
            description="Second number to add"
        )
    ]
    
    logic = NeuProcessLogic(
        about=about,
        language=ProgrammingLanguage.PYTHON,
        code="return a + b",
        import_statements=["import math"],
        arguments=arguments
    )
    
    print("Original NeuProcessLogic object:")
    print(f"Name: {logic.about.name}")
    print(f"Language: {logic.language}")
    print(f"Arguments: {[arg.name for arg in logic.arguments]}")
    print(f"Import statements: {logic.import_statements}")
    print()
    
    # Test encoding
    print("Testing encoding...")
    encoded_result = encode_logic(logic)
    encoded_code = encoded_result.code  # Extract the code string from the result
    print("Encoded Python code:")
    print(encoded_code)
    print()
    
    # Test decoding
    print("Testing decoding...")
    decoded_logic = decode_from_string(encoded_code)  # This returns NeuProcessLogic directly
    print("Decoded NeuProcessLogic object:")
    print(f"Name: {decoded_logic.about.name}")
    print(f"Language: {decoded_logic.language}")
    print(f"Arguments: {[arg.name for arg in decoded_logic.arguments]}")
    print(f"Import statements: {decoded_logic.import_statements}")
    print()
    
    # Test that we can encode the decoded object again
    print("Testing round-trip encoding...")
    re_encoded_result = encode_logic(decoded_logic)
    re_encoded_code = re_encoded_result.code  # Extract the code string
    print("Re-encoded code:")
    print(re_encoded_code)
    
    print("\nTest completed successfully!")


if __name__ == "__main__":
    test_basic_functionality()
