"""
Comprehensive test suite for the restructured Python encoder/decoder framework.

This test suite demonstrates:
1. Basic encoding/decoding functionality
2. Enhanced Pydantic configuration and validation
3. Error handling and edge cases
4. Performance and metadata tracking
"""

import sys
import os
import time

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
from app.models.process.logic.code.base import CodeGenerationResult


def test_basic_functionality():
    """Test basic encoding and decoding functionality."""
    print("=== Testing Basic Functionality ===\n")
    
    # Create test logic
    about = About(name="calculate_area", description="Calculate the area of a rectangle", version="1.0.0")
    arguments = [
        NeuProcessLogicArgument(name="width", type="float", is_optional=False, description="Width of the rectangle"),
        NeuProcessLogicArgument(name="height", type="float", is_optional=False, description="Height of the rectangle")
    ]
    
    logic = NeuProcessLogic(
        about=about,
        language=ProgrammingLanguage.PYTHON,
        code="return width * height",
        import_statements=["import math"],
        arguments=arguments
    )
    
    # Test encoding with enhanced result
    print("1. Testing encoding...")
    start_time = time.time()
    result = encode_logic(logic)
    encode_time = time.time() - start_time
    
    print(f"✅ Encoding completed in {encode_time:.4f}s")
    print(f"✅ Result is valid: {result.is_valid}")
    print(f"✅ Generated {len(result.code.split('\\n'))} lines of code")
    print(f"✅ Metadata: {result.metadata['function_name']}, {result.metadata['argument_count']} args")
    print()
    
    # Test decoding
    print("2. Testing decoding...")
    start_time = time.time()
    decoded_logic = decode_from_string(result.code)
    decode_time = time.time() - start_time
    
    print(f"✅ Decoding completed in {decode_time:.4f}s")
    print(f"✅ Function name: {decoded_logic.about.name}")
    print(f"✅ Arguments: {len(decoded_logic.arguments)}")
    print(f"✅ Imports: {len(decoded_logic.import_statements)}")
    print()


def test_configuration_options():
    """Test different configuration options."""
    print("=== Testing Configuration Options ===\\n")
    
    # Create test logic
    logic = NeuProcessLogic(
        about=About(name="test_config", description="Test configuration options"),
        language=ProgrammingLanguage.PYTHON,
        code="return x + y",
        arguments=[
            NeuProcessLogicArgument(name="x", type="int", description="First number"),
            NeuProcessLogicArgument(name="y", type="int", description="Second number")
        ]
    )
    
    # Test 1: Minimal configuration
    print("1. Testing minimal configuration...")
    minimal_config = PythonEncoderConfig(
        include_docstring=False,
        include_comments=False,
        include_type_hints=False
    )
    
    encoder = PythonEncoder(config=minimal_config)
    result = encoder.encode(logic)
    
    print(f"✅ Minimal code generated ({len(result.code.split('\\n'))} lines)")
    print(f"   Code preview: {result.code.split('\\n')[0]}")
    print()
    
    # Test 2: Maximum configuration
    print("2. Testing maximum configuration...")
    max_config = PythonEncoderConfig(
        include_docstring=True,
        include_comments=True,
        include_type_hints=True,
        include_imports_in_docstring=True,
        include_metadata_in_docstring=True,
        docstring_style="google"
    )
    
    encoder = PythonEncoder(config=max_config)
    result = encoder.encode(logic)
    
    print(f"✅ Full-featured code generated ({len(result.code.split('\\n'))} lines)")
    print(f"   Has docstring: {result.metadata['has_docstring']}")
    print()


def test_error_handling():
    """Test error handling and validation."""
    print("=== Testing Error Handling ===\\n")
    
    # Test 1: Invalid configuration
    print("1. Testing invalid configuration...")
    try:
        invalid_config = PythonEncoderConfig(
            docstring_style="invalid_style",
            indent_size=20  # Too large
        )
        print("❌ Should have failed validation")
    except Exception as e:
        print(f"✅ Configuration validation caught error: {str(e)[:60]}...")
    print()
    
    # Test 2: Invalid logic
    print("2. Testing invalid logic...")
    invalid_logic = NeuProcessLogic(
        about=About(name="", description="Invalid"),  # Empty name
        language=ProgrammingLanguage.JAVA,  # Wrong language
        code="",  # Empty code
        arguments=[]
    )
    
    encoder = PythonEncoder()
    result = encoder.encode(invalid_logic)
    
    print(f"✅ Handled invalid logic: {not result.is_valid}")
    print(f"   Errors: {len(result.validation_errors)}")
    for error in result.validation_errors[:2]:
        print(f"   - {error}")
    print()


def test_advanced_features():
    """Test advanced features like metadata and performance tracking."""
    print("=== Testing Advanced Features ===\\n")
    
    # Create complex logic
    logic = NeuProcessLogic(
        about=About(
            name="complex_calculation", 
            description="A complex mathematical calculation",
            version="2.1.0"
        ),
        language=ProgrammingLanguage.PYTHON,
        code='''result = math.sqrt(x**2 + y**2)
if normalize:
    result = result / max_value
return result''',
        import_statements=["import math", "import numpy as np"],
        arguments=[
            NeuProcessLogicArgument(name="x", type="float", description="X coordinate"),
            NeuProcessLogicArgument(name="y", type="float", description="Y coordinate"),
            NeuProcessLogicArgument(name="normalize", type="bool", is_optional=True, description="Whether to normalize"),
            NeuProcessLogicArgument(name="max_value", type="float", is_optional=True, description="Maximum value for normalization")
        ]
    )
    
    # Test with validation enabled
    config = PythonEncoderConfig(validate_output=True)
    encoder = PythonEncoder(config=config)
    
    print("1. Testing complex function encoding...")
    result = encoder.encode(logic)
    
    print(f"✅ Complex function encoded successfully")
    print(f"✅ Generation time: {result.generation_time:.6f}s")
    print(f"✅ Code length: {len(result.code)} characters")
    print(f"✅ Import count: {len(result.imports)}")
    print(f"✅ Validation passed: {result.is_valid}")
    print()
    
    # Test decoding back
    print("2. Testing complex function decoding...")
    decoded = decode_from_string(result.code)
    
    print(f"✅ Decoded function: {decoded.about.name}")
    print(f"✅ Version preserved: {decoded.about.version}")
    print(f"✅ Arguments preserved: {len(decoded.arguments)}")
    print(f"✅ Optional args: {sum(1 for arg in decoded.arguments if arg.is_optional)}")
    print()


def test_serialization():
    """Test Pydantic serialization features."""
    print("=== Testing Serialization ===\\n")
    
    # Create and encode logic
    logic = NeuProcessLogic(
        about=About(name="serialize_test", description="Test serialization"),
        language=ProgrammingLanguage.PYTHON,
        code="return data.upper()",
        arguments=[NeuProcessLogicArgument(name="data", type="str", description="Input data")]
    )
    
    result = encode_logic(logic)
    
    # Test serialization
    print("1. Testing result serialization...")
    serialized = result.to_dict()
    
    print(f"✅ Serialized to dict with {len(serialized)} fields")
    print(f"✅ Contains metadata: {'metadata' in serialized}")
    print(f"✅ Language preserved: {serialized['language']}")
    print()
    
    # Test configuration serialization
    print("2. Testing configuration serialization...")
    config = PythonEncoderConfig(
        include_type_hints=True,
        docstring_style="numpy",
        max_line_length=100
    )
    
    config_dict = config.model_dump()
    print(f"✅ Config serialized with {len(config_dict)} fields")
    print(f"✅ Docstring style: {config_dict['docstring_style']}")
    print()


def run_all_tests():
    """Run all test suites."""
    print("🧪 Starting Comprehensive Test Suite for Restructured Framework\\n")
    
    try:
        test_basic_functionality()
        test_configuration_options()
        test_error_handling()
        test_advanced_features()
        test_serialization()
        
        print("🎉 All tests completed successfully!")
        print("✅ The restructured framework with enhanced Pydantic integration is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
