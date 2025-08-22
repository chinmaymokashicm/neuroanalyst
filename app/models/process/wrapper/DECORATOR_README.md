# NeuProcessLogic Wrapper Documentation

## Overview

The NeuProcessLogic wrapper is a powerful decorator that automatically handles BIDS (Brain Imaging Data Structure) path construction, metadata management, and output organization for neuroimaging processing functions. It's designed to simplify the development of neuroimaging pipelines while ensuring BIDS compliance and proper metadata tracking.

## Key Features

- **Automatic BIDS Path Construction**: Generates proper BIDS-compliant output paths based on input file structure
- **Metadata Management**: Automatically creates sidecar JSON files with processing metadata, metrics, and provenance information
- **Error Handling**: Robust error handling with detailed error messages and execution tracking
- **Flexible Output Support**: Supports various output formats (JSON, text, neuroimaging files)
- **Integration with NeuProcessLogic**: Seamlessly works with the NeuProcessLogic system for automatic function generation
- **Dictionary-based Returns**: Functions return simple dictionaries, keeping processing logic clean and focused

## Core Components

### 1. Function Return Format

Processing functions should return a dictionary with the following structure:

```python
def my_function(input_filepath):
    # ... processing logic ...
    
    return {
        "output_data": processed_data,           # Main output data
        "metrics": {"accuracy": 0.95},           # Metrics dictionary
        "output_bids_entities": {                # BIDS entities for output filename
            "desc": "processed",
            "suffix": "data", 
            "extension": ".json"
        },
        "forced_output_filepaths": None          # Optional: paths written directly by function
    }
```

### 2. NeuProcessDecoratorConfig

Configuration for the decorator behavior:

```python
from app.models.process.wrapper import NeuProcessDecoratorConfig

config = NeuProcessDecoratorConfig(
    pipeline_name="my_pipeline",             # Required: Pipeline name
    bids_root="/path/to/bids/dataset",       # Required: BIDS root directory
    overwrite=False,                         # Whether to overwrite existing files
    create_sidecar=True,                     # Whether to create metadata sidecar files
    derivatives_dir=None                     # Custom derivatives directory name
)
```

### 3. NeuProcessResult

The result returned by decorated functions:

```python
# Decorated function returns NeuProcessResult
result = my_decorated_function(input_file)

print(f"Success: {result.success}")
print(f"Output file: {result.output_filepath}")
print(f"Sidecar file: {result.sidecar_filepath}")
print(f"Execution time: {result.execution_time}")
if not result.success:
    print(f"Error: {result.error_message}")
```

## Usage Patterns

### Pattern 1: Direct Decorator Usage

For simple processing functions:

```python
from app.models.process.wrapper import neuprocess_decorator, NeuProcessDecoratorConfig

config = NeuProcessDecoratorConfig(
    pipeline_name="skull_stripping",
    bids_root="/data/bids_dataset"
)

@neuprocess_decorator(config)
def skull_strip_t1w(input_filepath):
    """Remove skull from T1w images."""
    
    # Your processing logic here
    processed_data = perform_skull_stripping(input_filepath)
    
    return {
        "output_data": processed_data,
        "metrics": {"brain_volume": 1234567},
        "output_bids_entities": {
            "desc": "brain",
            "suffix": "T1w",
            "extension": ".nii.gz"
        }
    }

# Usage
result = skull_strip_t1w("/data/bids_dataset/sub-01/anat/sub-01_T1w.nii.gz")
```

### Pattern 2: NeuProcessLogic Integration

For automatic function generation from logic definitions:

```python
from app.models.process.logic.core import (
    NeuProcessLogic, NeuProcessLogicArgument, ProgrammingLanguage
)
from app.models.process.wrapper import (
    create_neuprocess_function, NeuProcessDecoratorConfig
)
from app.models.about import About

# Define the processing logic
logic = NeuProcessLogic(
    about=About(name="calculate_fa", description="Calculate FA from DTI"),
    language=ProgrammingLanguage.PYTHON,
    code="""
# DTI processing code
fa_map = calculate_fractional_anisotropy(input_filepath)
metrics = {"mean_fa": float(np.mean(fa_map))}
output_entities = {"suffix": "fa", "extension": ".nii.gz"}
return fa_map, metrics, output_entities
    """,
    import_statements=["import numpy as np"],  # Imports go here, not in code
    arguments=[
        NeuProcessLogicArgument(
            name="input_filepath", 
            type="str", 
            description="Path to DTI file"
        )
    ]
)

# Create decorated function
config = NeuProcessDecoratorConfig(
    pipeline_name="dti_analysis",
    bids_root="/data/bids_dataset"
)

fa_calculator = create_neuprocess_function(logic, config)

# Usage
result = fa_calculator("/data/bids_dataset/sub-01/dwi/sub-01_dwi.nii.gz")
```

### Pattern 3: Batch Processing

For processing multiple subjects:

```python
import glob
from pathlib import Path

# Find all T1w files
t1w_files = glob.glob("/data/bids_dataset/sub-*/anat/*_T1w.nii.gz")

results = []
for t1w_file in t1w_files:
    result = skull_strip_t1w(t1w_file)
    results.append(result)
    
    if result.success:
        print(f"✅ Processed {Path(t1w_file).name}")
    else:
        print(f"❌ Failed {Path(t1w_file).name}: {result.error_message}")

# Analyze results
successful = [r for r in results if r.success]
print(f"Successfully processed {len(successful)}/{len(results)} files")
```

## Output Structure

The decorator automatically creates a BIDS-compliant derivatives structure:

```
bids_root/
├── derivatives/
│   └── pipeline_name/
│       └── sub-{subject}/
│           └── [ses-{session}/]
│               └── {datatype}/
│                   ├── {bids_filename}.{ext}      # Main output file
│                   └── {bids_filename}.json       # Sidecar metadata
│                       # OR {bids_filename}.meta.json if output is already JSON
```

### Example Output Structure

```
/data/bids_dataset/
├── derivatives/
│   └── skull_stripping/
│       └── sub-01/
│           └── anat/
│               ├── sub-01_desc-brain_T1w.nii.gz    # Processed brain image
│               └── sub-01_desc-brain_T1w.json      # Metadata sidecar
```

## Sidecar Metadata Format

The automatically generated sidecar JSON files follow this structure:

```json
{
  "GeneratedBy": {
    "Name": "pipeline_name",
    "Version": "1.0.0",
    "Description": "Function docstring",
    "CodeURL": "module_name"
  },
  "SourceDatasets": [
    {
      "URL": "/path/to/input/file",
      "Version": "unknown"
    }
  ],
  "ProcessingDetails": {
    "FunctionName": "function_name",
    "ExecutionTime": 0.1234,
    "Timestamp": "2025-08-20T17:38:23",
    "Configuration": {
      "pipeline_name": "skull_stripping",
      "overwrite": true,
      "create_sidecar": true
    }
  },
  "Metrics": {
    "brain_volume": 1234567,
    "processing_quality": 0.95
  },
  "OutputFiles": ["/path/to/output/file"],
  "ForcedOutputFiles": []
}
```

## BIDS Entity Mapping

The decorator automatically extracts and preserves BIDS entities from input files:

| Input Entity | Description | Preserved in Output |
|--------------|-------------|-------------------|
| `sub-{label}` | Subject identifier | ✅ Always |
| `ses-{label}` | Session identifier | ✅ If present |
| `task-{label}` | Task name | ✅ If present |
| `run-{index}` | Run number | ✅ If present |
| `acq-{label}` | Acquisition parameters | ✅ If present |
| `dir-{label}` | Phase encoding direction | ✅ If present |

Additional entities can be added through the `output_bids_entities` parameter.

## Error Handling

The decorator provides comprehensive error handling:

```python
result = my_decorated_function(input_file)

if not result.success:
    print(f"Processing failed: {result.error_message}")
    print(f"Execution time: {result.execution_time}")
    # Handle error appropriately
```

Common error scenarios:
- File already exists (when `overwrite=False`)
- Invalid BIDS structure
- Processing function exceptions
- File I/O errors

## Best Practices

1. **Function Documentation**: Always include docstrings in your processing functions - they become part of the metadata.

2. **Meaningful Metrics**: Include relevant quality metrics and processing parameters in the metrics dictionary.

3. **Proper BIDS Entities**: Use appropriate BIDS entities for your output files to maintain dataset organization.

4. **Error Handling**: Always check the `success` field of results before proceeding.

5. **Resource Management**: For large datasets, consider processing in batches to manage memory usage.

## Advanced Configuration

### Custom Derivatives Directory

```python
config = NeuProcessDecoratorConfig(
    pipeline_name="my_pipeline",
    bids_root="/data/bids_dataset",
    derivatives_dir="custom_analysis_v2"  # Creates derivatives/custom_analysis_v2/
)
```

### Disabling Sidecar Creation

```python
config = NeuProcessDecoratorConfig(
    pipeline_name="my_pipeline",
    bids_root="/data/bids_dataset",
    create_sidecar=False  # No metadata files created
)
```

### Output File Type Handling

The decorator automatically handles different output types:

- **JSON files**: Automatically serialized with proper formatting
- **Text files**: String data written directly
- **Neuroimaging files**: Objects with `.to_filename()` method (e.g., nibabel)
- **Binary data**: Pickled for complex Python objects

## Integration with HPC/Containerization

The decorator is designed to work seamlessly with containerized environments:

1. **Path Mounting**: Ensure BIDS root is properly mounted in containers
2. **Permissions**: Set appropriate write permissions for derivatives directory
3. **Environment Variables**: BIDS root can be set via environment variables
4. **Parallel Processing**: Each decorated function call is independent and thread-safe

## Troubleshooting

### Common Issues

1. **Path Construction Errors**
   - Ensure input files follow BIDS naming conventions
   - Check that `bids_root` is correctly specified
   - Verify file permissions

2. **Overwrite Errors**
   - Set `overwrite=True` if you want to replace existing files
   - Or manually remove existing output files

3. **Sidecar Conflicts**
   - When output files are JSON, sidecar files use `.meta.json` extension
   - Ensure sufficient disk space for metadata files

### Debug Mode

For debugging path construction and metadata generation:

```python
# Enable debug logging (if implemented)
import logging
logging.basicConfig(level=logging.DEBUG)

# Or inspect the result manually
result = my_function(input_file)
print(f"Output path: {result.output_filepath}")
print(f"Parent directory: {result.output_filepath.parent}")
print(f"Directory exists: {result.output_filepath.parent.exists()}")
```

## Examples Repository

See the complete examples in:
- `app/models/process/logic/test_decorator.py` - Basic functionality tests
- `app/models/process/logic/examples_decorator.py` - Comprehensive usage examples

These files demonstrate all the features and usage patterns described in this documentation.
