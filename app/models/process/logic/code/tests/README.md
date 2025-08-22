# Test Suite for NeuProcess Framework

This directory contains comprehensive tests for the NeuProcess framework with PyBIDS integration and enhanced Pydantic support.

## Test Files

### Core Framework Tests

#### `test_comprehensive.py` 
**Main Test Suite** - Complete testing of all framework features:
- ✅ Basic encoding/decoding functionality
- ✅ Configuration options and validation
- ✅ Error handling and edge cases
- ✅ Advanced features (metadata, performance tracking)
- ✅ Pydantic serialization capabilities

#### `test_enhanced_pydantic.py`
**Pydantic Integration Tests** - Focused testing of enhanced Pydantic features:
- ✅ Advanced validation (field validators, model validators)
- ✅ Enhanced result models with metadata
- ✅ Configuration validation and error handling
- ✅ Automatic type conversion and constraint enforcement

#### `test_python_restructured.py`
**Basic Functionality Test** - Simple round-trip encoding/decoding test:
- ✅ Basic encode/decode workflow
- ✅ Data preservation verification
- ✅ Import statement handling

### PyBIDS Integration Tests

**Note**: PyBIDS integration tests have been moved to `app/models/process/wrapper/tests/` since they test wrapper functionality, not core code generation.

See:
- `app/models/process/wrapper/tests/test_pybids_simple.py` - Simple PyBIDS integration
- `app/models/process/wrapper/tests/test_pybids_integration.py` - Advanced PyBIDS testing

## Running Tests

### Run All Tests
```bash
cd app/models/process/logic/code/tests/

# Core framework tests only (PyBIDS tests moved to wrapper/tests/)
python test_comprehensive.py
python test_enhanced_pydantic.py  
python test_python_restructured.py
```

### Run PyBIDS Integration Tests
```bash
cd app/models/process/wrapper/tests/

# PyBIDS integration tests
python -m app.models.process.wrapper.tests.test_pybids_simple
python -m app.models.process.wrapper.tests.test_pybids_integration
```

### Run Specific Test Categories
```bash
# Test PyBIDS integration only
python test_pybids_simple.py

# Test core functionality only
python test_comprehensive.py
```

## Test Coverage

The test suite covers:

- **Core Functionality**: Encoding NeuProcessLogic to Python code and vice versa
- **Configuration Management**: All encoder/decoder configuration options
- **Validation**: Field-level, model-level, and custom validation rules
- **Error Handling**: Invalid inputs, configuration errors, parsing failures
- **Performance**: Timing and metadata collection
- **Serialization**: JSON export/import capabilities
- **Type Safety**: Pydantic type checking and coercion

**Note**: PyBIDS integration testing has been moved to `app/models/process/wrapper/tests/` for better organization.

## Framework Status

✅ **Fully Functional** - All tests pass
✅ **Enhanced Pydantic Integration** - Advanced validation and serialization
✅ **Simplified Architecture** - Clean, maintainable codebase
✅ **Production Ready** - Comprehensive error handling and validation

**Note**: PyBIDS integration features are tested separately in `wrapper/tests/`

---

*Framework Version: Core Logic v3.0 (Simplified)*
