# NeuProcess Wrapper Examples

This directory contains example scripts demonstrating how to use the NeuProcess wrapper functionality.

## Example Files

### `examples_decorator.py`
**Comprehensive Examples** - Complete usage demonstrations:
- ✅ Basic decorator configuration and usage
- ✅ Advanced PyBIDS integration scenarios
- ✅ Multiple processing pipeline examples
- ✅ Error handling and validation examples
- ✅ Metadata generation and customization

### `simple_demo.py`
**Quick Demo** - Simple, easy-to-understand example:
- ✅ Basic decorator setup and usage
- ✅ Simple BIDS dataset processing
- ✅ Minimal configuration for quick testing
- ✅ Clear output demonstration

## Running Examples

### Run Simple Demo
```bash
# From project root
cd /Users/cmokashi/Documents/GitHub/neuroanalyst

# Simple demonstration
python app/models/process/wrapper/examples/simple_demo.py
```

### Run Comprehensive Examples
```bash
# Comprehensive examples with multiple scenarios
python app/models/process/wrapper/examples/examples_decorator.py
```

## What These Examples Show

- **Decorator Configuration**: How to set up `NeuProcessDecoratorConfig`
- **PyBIDS Integration**: BIDS-compliant path construction and entity extraction
- **Metadata Handling**: Automatic metadata generation and custom additions
- **Error Handling**: Graceful error handling and validation
- **Output Organization**: BIDS derivatives structure creation
- **Real-world Usage**: Practical examples for neuroimaging workflows

## Example Output

The examples will create temporary BIDS datasets and demonstrate:
- BIDS entity extraction from filenames
- Derivatives path construction
- Metadata JSON file generation
- Processing result validation

---

*These examples complement the formal tests in `../tests/` by providing practical usage demonstrations.*
