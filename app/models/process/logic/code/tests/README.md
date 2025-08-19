# Test Suite for NeuProcessLogic Code Framework

This directory contains comprehensive tests for the restructured NeuProcessLogic code framework with enhanced Pydantic integration.

## Test Files

### `test_comprehensive.py` 
**Main Test Suite** - Complete testing of all framework features:
- ✅ Basic encoding/decoding functionality
- ✅ Configuration options and validation
- ✅ Error handling and edge cases
- ✅ Advanced features (metadata, performance tracking)
- ✅ Pydantic serialization capabilities

### `test_enhanced_pydantic.py`
**Pydantic Integration Tests** - Focused testing of enhanced Pydantic features:
- ✅ Advanced validation (field validators, model validators)
- ✅ Enhanced result models with metadata
- ✅ Configuration validation and error handling
- ✅ Automatic type conversion and constraint enforcement

### `test_python_restructured.py`
**Basic Functionality Test** - Simple round-trip encoding/decoding test:
- ✅ Basic encode/decode workflow
- ✅ Data preservation verification
- ✅ Import statement handling

## Running Tests

### Run All Tests
```bash
# From project root
cd /Users/cmokashi/Documents/GitHub/neuroanalyst

# Run comprehensive test suite (recommended)
python -m app.models.process.logic.code.tests.test_comprehensive

# Run enhanced Pydantic tests
python -m app.models.process.logic.code.tests.test_enhanced_pydantic

# Run basic functionality test
python -m app.models.process.logic.code.tests.test_python_restructured
```

### Expected Output
All tests should pass with output showing:
- ✅ Encoding/decoding success
- ✅ Configuration validation working
- ✅ Error handling functioning
- ✅ Performance metrics collected
- ✅ Pydantic features operating correctly

## Test Coverage

The test suite covers:

- **Core Functionality**: Encoding NeuProcessLogic to Python code and vice versa
- **Configuration Management**: All encoder/decoder configuration options
- **Validation**: Field-level, model-level, and custom validation rules
- **Error Handling**: Invalid inputs, configuration errors, parsing failures
- **Performance**: Timing and metadata collection
- **Serialization**: JSON export/import capabilities
- **Type Safety**: Pydantic type checking and coercion

## Framework Status

✅ **Fully Functional** - All tests pass
✅ **Enhanced Pydantic Integration** - Advanced validation and serialization
✅ **Multi-Language Ready** - Extensible architecture for additional languages
✅ **Production Ready** - Comprehensive error handling and validation

---

*Last Updated: August 19, 2025*
*Framework Version: Enhanced Pydantic Integration v2.0*
