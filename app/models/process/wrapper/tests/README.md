# PyBIDS Integration Tests for NeuProcess Wrapper

This directory contains tests for the NeuProcess wrapper's PyBIDS integration functionality.

## Test Files

### `test_pybids_simple.py`
**Simple PyBIDS Integration** - Basic functionality testing:
- ✅ PyBIDS entity extraction and path construction
- ✅ BIDS-compliant derivatives organization
- ✅ Metadata generation with dataset information
- ✅ Text-based processing (simplified for testing)
- ✅ Direct PyBIDS integration without fallbacks

### `test_pybids_integration.py`
**Advanced PyBIDS Testing** - Comprehensive scenarios:
- ✅ Complex BIDS entity combinations (subject, session, task, acquisition, etc.)
- ✅ Multiple datatypes (func, anat) and file structures
- ✅ Advanced entity extraction from complex filenames
- ✅ Error handling and edge cases
- ✅ Comprehensive metadata validation

### `test_decorator_functionality.py`
**Core Decorator Testing** - Decorator functionality validation:
- ✅ Basic decorator configuration and setup
- ✅ Function wrapping and result handling
- ✅ BIDS path construction logic
- ✅ Metadata generation and validation
- ✅ Error handling and edge cases

### `test_debug_decorator.py`
**Debug Testing** - Debug and troubleshooting utilities:
- ✅ Path construction debugging
- ✅ Configuration validation testing
- ✅ Quick debugging scenarios
- ✅ Simplified test cases for troubleshooting

## Running Tests

### Run Individual Tests
```bash
# From project root
cd /Users/cmokashi/Documents/GitHub/neuroanalyst

# Simple PyBIDS integration
python -m app.models.process.wrapper.tests.test_pybids_simple

# Advanced PyBIDS integration  
python -m app.models.process.wrapper.tests.test_pybids_integration

# Core decorator functionality
python -m app.models.process.wrapper.tests.test_decorator_functionality

# Debug and troubleshooting
python -m app.models.process.wrapper.tests.test_debug_decorator
```

### Run All Wrapper Tests
```bash
# Run both PyBIDS tests
python -c "
import sys
sys.path.append('/Users/cmokashi/Documents/GitHub/neuroanalyst')
from app.models.process.wrapper.tests.test_pybids_simple import test_pybids_simple
from app.models.process.wrapper.tests.test_pybids_integration import test_pybids_integration_basic, test_pybids_advanced_functionality, test_pybids_entity_extraction

print('🧪 Running PyBIDS Wrapper Tests...')
test_pybids_simple()
test_pybids_integration_basic()
test_pybids_advanced_functionality() 
test_pybids_entity_extraction()
print('✅ All PyBIDS wrapper tests passed!')
"
```

## Test Coverage

These tests cover:

- **PyBIDS Integration**: Direct integration with PyBIDS library for BIDS compliance
- **Entity Extraction**: Extraction of BIDS entities (subject, session, task, etc.) from filenames
- **Path Construction**: BIDS-compliant output path generation in derivatives folder
- **Metadata Generation**: Automatic metadata collection including dataset information
- **Configuration Validation**: Wrapper configuration options and validation
- **Error Handling**: Graceful error handling for invalid inputs
- **Text Processing**: Simplified text-based data processing for testing

## Architecture Note

These tests are correctly located in `wrapper/tests/` because they test:
- The `neuprocess_decorator` functionality
- PyBIDS integration features
- BIDS path construction and entity extraction
- Wrapper configuration and metadata handling

The core code generation tests remain in `logic/code/tests/` as they test:
- Python code encoding/decoding
- Pydantic validation
- Core framework functionality

---

*Framework Version: PyBIDS Integration v3.0 (Simplified)*
