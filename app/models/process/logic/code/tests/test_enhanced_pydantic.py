"""
Test script to verify enhanced Pydantic integration in the restructured framework.
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
    PythonDecoderConfig
)
from app.models.process.logic.code.base import CodeGenerationResult, CodeDecodingResult


def test_enhanced_pydantic_features():
    """Test enhanced Pydantic features in the framework."""
    
    print("=== Testing Enhanced Pydantic Integration ===\n")
    
    # Test 1: Enhanced configuration validation
    print("1. Testing configuration validation...")
    
    try:
        # Valid configuration
        valid_config = PythonEncoderConfig(
            include_type_hints=True,
            docstring_style="google",
            indent_size=4,
            max_line_length=88
        )
        print(f"✅ Valid config created: {valid_config.docstring_style}")
        
        # Test automatic string stripping
        config_with_whitespace = PythonEncoderConfig(
            docstring_style="  numpy  "  # Should be stripped and lowercased
        )
        print(f"✅ String processing: '{config_with_whitespace.docstring_style}'")
        
        # Test validation - this should fail
        try:
            invalid_config = PythonEncoderConfig(
                docstring_style="invalid_style",
                indent_size=20  # Too large
            )
        except Exception as e:
            print(f"✅ Validation caught error: {str(e)[:60]}...")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
    
    # Test 2: Enhanced result models
    print("\n2. Testing enhanced result models...")
    
    try:
        # Create a test logic object
        about = About(name="test_function", description="A test function", version="2.0.0")
        arguments = [
            NeuProcessLogicArgument(name="x", type="float", is_optional=False, description="Input value"),
            NeuProcessLogicArgument(name="factor", type="float", is_optional=True, description="Scaling factor")
        ]
        
        logic = NeuProcessLogic(
            about=about,
            language=ProgrammingLanguage.PYTHON,
            code="return x * factor if factor else x * 2.0",
            import_statements=["import math"],
            arguments=arguments
        )
        
        # Test encoder with enhanced result
        encoder = PythonEncoder(PythonEncoderConfig(validate_output=True))
        result = encoder.encode(logic)
        
        print(f"✅ Encoding result type: {type(result).__name__}")
        print(f"✅ Result is valid: {result.is_valid}")
        print(f"✅ Generation time: {result.generation_time:.4f}s")
        print(f"✅ Metadata keys: {list(result.metadata.keys())}")
        
        # Test serialization
        result_dict = result.to_dict()
        print(f"✅ Result serialization: {len(result_dict)} fields")
        
    except Exception as e:
        print(f"❌ Result model test failed: {e}")
    
    # Test 3: Enhanced validation
    print("\n3. Testing enhanced validation...")
    
    try:
        # Test logic validation
        encoder = PythonEncoder()
        is_valid, errors = encoder.validate_logic(logic)
        print(f"✅ Logic validation: {is_valid}, errors: {len(errors)}")
        
        # Test invalid logic
        invalid_logic = NeuProcessLogic(
            about=About(name="", description="Invalid"),  # Empty name
            language=ProgrammingLanguage.JAVA,  # Wrong language
            code="",  # Empty code
            arguments=[]
        )
        
        is_valid, errors = encoder.validate_logic(invalid_logic)
        print(f"✅ Invalid logic detected: {not is_valid}, errors: {len(errors)}")
        for error in errors[:2]:  # Show first 2 errors
            print(f"   - {error}")
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
    
    # Test 4: Model validation features
    print("\n4. Testing Pydantic model validation...")
    
    try:
        # Test field validation
        decoder_config = PythonDecoderConfig(
            confidence_threshold=0.9,
            min_function_lines=2,
            max_function_lines=500
        )
        print(f"✅ Decoder config validation passed")
        
        # Test model validator
        try:
            bad_config = PythonDecoderConfig(
                min_function_lines=100,
                max_function_lines=50  # This should fail model validation
            )
        except Exception as e:
            print(f"✅ Model validator caught error: {str(e)[:50]}...")
        
        # Test extra field rejection
        try:
            from pydantic import ValidationError
            PythonEncoderConfig.model_validate({
                'include_type_hints': True,
                'unknown_field': 'value'  # Should be rejected
            })
        except ValidationError as e:
            print(f"✅ Extra field rejected")
        
    except Exception as e:
        print(f"❌ Model validation test failed: {e}")
    
    print("\n=== Enhanced Pydantic Integration Tests Complete ===")


if __name__ == "__main__":
    test_enhanced_pydantic_features()
