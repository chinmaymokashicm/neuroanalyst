# NeuProcess Wrapper System - Complete Implementation Guide

## Overview

The NeuProcess wrapper system provides a comprehensive decorator framework for neuroimaging data processing with integrated PyBIDS support for BIDS compliance. This system handles output path construction, metadata generation, and error management automatically.

## ✅ System Features

### 🧠 **PyBIDS Integration**
- **Automatic entity extraction** from BIDS filenames using PyBIDS
- **Standards-compliant path construction** for derivatives 
- **Dataset-level metadata** integration
- **BIDSLayout integration** for efficient dataset operations

### 🔧 **Decorator Framework**
- **Clean function signatures** - users focus on processing logic
- **Automatic I/O handling** - input/output path management
- **Comprehensive metadata** - processing provenance and parameters
- **Error handling** - robust exception management and logging

### 📁 **BIDS Compliance**
- **Derivatives organization** following BIDS specification
- **Entity preservation** from input to output filenames
- **Sidecar JSON files** with processing metadata
- **Flexible configuration** for different pipeline needs

## 🚀 Quick Start

### Basic Usage

```python
from app.models.process.wrapper import neuprocess_decorator, NeuProcessDecoratorConfig

# Configure the decorator
config = NeuProcessDecoratorConfig(
    pipeline_name="my_analysis",
    bids_root="/path/to/bids/dataset",
    overwrite=True
)

# Decorate your processing function
@neuprocess_decorator(config)
def process_fmri_data(input_filepath: str) -> dict:
    """Process fMRI data with motion correction."""
    
    # Your processing logic here
    corrected_data = apply_motion_correction(input_filepath)
    
    return {
        "data": corrected_data,
        "description": "Motion-corrected fMRI data",
        "metadata": {
            "motion_parameters": {"framewise_displacement": 0.2},
            "software_version": "1.0.0"
        }
    }

# Run processing
result = process_fmri_data("/data/sub-01/func/sub-01_task-rest_bold.nii.gz")

# Check results
if result.success:
    print(f"✅ Processing completed: {result.output_filepath}")
    print(f"📋 Metadata: {result.sidecar_filepath}")
else:
    print(f"❌ Processing failed: {result.error_message}")
```

### Advanced Configuration

```python
from bids import BIDSLayout

# Pre-initialize BIDSLayout for performance
layout = BIDSLayout("/data/my_study", derivatives=True)

config = NeuProcessDecoratorConfig(
    pipeline_name="advanced_pipeline",
    bids_root="/data/my_study", 
    bids_layout=layout,  # Reuse layout
    derivatives_dir="custom_derivatives",
    bids_validate=True,  # Enable validation
    create_sidecar=True
)
```

## 📋 Configuration Options

### NeuProcessDecoratorConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pipeline_name` | `str` | Required | Name of the processing pipeline |
| `bids_root` | `str/Path` | Required | Root directory of BIDS dataset |
| `overwrite` | `bool` | `False` | Whether to overwrite existing output files |
| `create_sidecar` | `bool` | `True` | Whether to create JSON sidecar files |
| `derivatives_dir` | `str` | `None` | Custom derivatives directory name |
| `bids_layout` | `BIDSLayout` | `None` | Pre-initialized BIDSLayout object |
| `bids_validate` | `bool` | `False` | Whether to validate BIDS compliance |

## 🔄 Function Return Format

Your decorated functions should return a dictionary with these keys:

```python
return {
    "data": processed_data,           # Required: Main output data
    "description": "Description",     # Required: Processing description  
    "metadata": {                     # Required: Additional metadata
        "parameters": {...},          # Processing parameters
        "software_version": "1.0.0",  # Software version
        "custom_fields": {...}        # Any additional metadata
    }
}
```

### Legacy Tuple Format (Still Supported)

```python
# Legacy format still works
return (output_data, metrics, output_entities, forced_outputs)
```

## 🗂️ Output Structure

The decorator automatically creates BIDS-compliant output structure:

```
derivatives/
└── {pipeline_name}/
    └── sub-{subject}/
        ├── [ses-{session}/]
        └── {datatype}/
            ├── sub-{subject}_[entities]_desc-{pipeline}_{suffix}.ext
            └── sub-{subject}_[entities]_desc-{pipeline}_{suffix}.json
```

### Example Output

```
derivatives/
└── motion_correction/
    └── sub-01/
        └── func/
            ├── sub-01_task-rest_desc-motion_correction_bold.nii.gz
            └── sub-01_task-rest_desc-motion_correction_bold.json
```

## 🧩 Entity Extraction

The system automatically extracts BIDS entities from input filenames:

### Supported Entities
- `sub` - Subject ID
- `ses` - Session ID  
- `task` - Task name
- `acq` - Acquisition parameters
- `run` - Run number
- `space` - Coordinate space
- `desc` - Description

### Example Entity Extraction

```python
# Input: sub-pilot01_ses-baseline_task-nback_acq-multiband_run-02_bold.nii.gz
# Extracted entities: {
#     'subject': 'pilot01',
#     'session': 'baseline', 
#     'task': 'nback',
#     'acquisition': 'multiband',
#     'run': '02'
# }
```

## 📊 Metadata Generation

Each output includes comprehensive metadata in the sidecar JSON:

```json
{
  "Description": "Motion-corrected fMRI data",
  "ProcessingPipeline": "motion_correction",
  "InputFile": "/data/sub-01/func/sub-01_task-rest_bold.nii.gz",
  "OutputFile": "/derivatives/motion_correction/sub-01/func/...",
  "ProcessingTime": 45.123,
  "ProcessingDate": "2024-12-20T10:30:45.123456",
  "BIDSEntities": {"subject": "01", "task": "rest"},
  "DatasetName": "My Study",
  "BIDSVersion": "1.8.0",
  "FunctionName": "process_fmri_data",
  "FunctionModule": "__main__",
  "motion_parameters": {"framewise_displacement": 0.2},
  "software_version": "1.0.0"
}
```

## 🔧 Advanced Features

### Custom Output Paths

```python
# Custom suffix and extension
@neuprocess_decorator(config)
def custom_processing(input_filepath: str) -> dict:
    return {
        "data": processed_data,
        "description": "Custom processing",
        "metadata": {
            "output_bids_entities": {
                "suffix": "custom",
                "extension": ".txt"
            }
        }
    }
```

### Error Handling

```python
result = process_data(input_file)

if not result.success:
    print(f"Error: {result.error_message}")
    print(f"Processing time: {result.execution_time}s")
    # Error metadata available in result.metadata
```

### Batch Processing

```python
input_files = [
    "/data/sub-01/func/sub-01_task-rest_bold.nii.gz",
    "/data/sub-02/func/sub-02_task-rest_bold.nii.gz"
]

results = []
for input_file in input_files:
    result = process_fmri_data(input_file)
    results.append(result)
    
# Check all results
all_successful = all(r.success for r in results)
```

## 🧪 Testing

### Run Tests

```bash
cd app/models/process/logic/code/tests/

# Run basic tests
python test_comprehensive.py

# Run PyBIDS integration tests
python test_pybids_simple.py
```

### Test Your Own Function

```python
import tempfile
from pathlib import Path

# Create test environment
with tempfile.TemporaryDirectory() as temp_dir:
    bids_root = Path(temp_dir) / "test_dataset"
    bids_root.mkdir()
    
    # Create test input
    input_dir = bids_root / "sub-test" / "func"
    input_dir.mkdir(parents=True)
    input_file = input_dir / "sub-test_task-test_bold.txt"
    
    with open(input_file, 'w') as f:
        f.write("test data")
    
    # Configure and test
    config = NeuProcessDecoratorConfig(
        pipeline_name="test_pipeline",
        bids_root=str(bids_root),
        overwrite=True
    )
    
    @neuprocess_decorator(config)
    def test_function(input_filepath: str) -> dict:
        return {
            "data": "processed test data",
            "description": "Test processing",
            "metadata": {"test": True}
        }
    
    result = test_function(str(input_file))
    assert result.success
    print(f"✅ Test passed: {result.output_filepath}")
```

## 🔄 Migration Guide

### From Previous Versions

The system is backward compatible, but you can migrate to the new format:

```python
# Old tuple format
def old_function(input_filepath):
    return (output_data, metrics, entities)

# New dictionary format (recommended)  
def new_function(input_filepath):
    return {
        "data": output_data,
        "description": "Processing description", 
        "metadata": {"metrics": metrics, "parameters": {...}}
    }
```

### Enable PyBIDS Features

```python
# Add PyBIDS to your configuration
config = NeuProcessDecoratorConfig(
    pipeline_name="my_pipeline",
    bids_root="/path/to/bids",
    # PyBIDS is automatically enabled
)
```

## 📁 Code Organization

```
app/models/process/
├── wrapper/
│   ├── __init__.py              # Public API exports
│   ├── core.py                  # Main implementation
│   └── IMPLEMENTATION_SUMMARY.md # This documentation
├── logic/
│   ├── core.py                  # NeuProcessLogic models only
│   └── code/
│       └── tests/               # Test suite
└── ...
```

## 🎯 Next Steps

This wrapper system is ready for:

1. **Production Neuroimaging Pipelines** - Process real fMRI, structural, and diffusion data
2. **HPC Deployment** - Scale to compute clusters with clean function interfaces  
3. **Container Integration** - Package functions into Singularity/Docker containers
4. **Workflow Systems** - Integrate with Nipype, Snakemake, or custom workflows
5. **BIDS-Apps Development** - Create standardized neuroimaging applications

---

**Ready for production use with complete PyBIDS integration and BIDS compliance!** 🧠✨
- **Before**: Import statements were duplicated in both `import_statements` field AND within the `code` field
- **After**: Clean separation:
  - `import_statements` field contains the imports
  - `code` field contains only the processing logic
  - No duplication

## 📁 Updated File Structure

```
app/models/process/
├── logic/
│   ├── core.py                    # NeuProcessLogic models only
│   ├── code/                      # Encoder/decoder functionality
│   ├── test_decorator.py          # Updated tests
│   ├── examples_decorator.py      # Updated examples
│   ├── simple_demo.py             # Updated demo
│   ├── debug_decorator.py         # Updated debug script
│   └── DECORATOR_README.md        # Updated documentation
└── wrapper/
    ├── __init__.py                # Clean imports
    └── core.py                    # All wrapper/decorator functionality
```

## 🔧 Import Changes

### Before:
```python
from app.models.process.logic.core import (
    NeuProcessOutput,
    NeuProcessDecoratorConfig,
    neuprocess_decorator,
    create_neuprocess_function,
)
```

### After:
```python
# For logic-related imports
from app.models.process.logic.core import (
    NeuProcessLogic,
    NeuProcessLogicArgument,
    ProgrammingLanguage
)

# For wrapper-related imports  
from app.models.process.wrapper import (
    NeuProcessDecoratorConfig,
    neuprocess_decorator,
    create_neuprocess_function,
)
```

## 🎯 Key Improvements

### 1. **Cleaner Processing Functions**
```python
# Before - Required NeuroAnalyst imports
from app.models.process.logic.core import NeuProcessOutput

@neuprocess_decorator(config)
def my_function(input_filepath):
    processed_data = do_processing(input_filepath)
    return NeuProcessOutput(
        output_data=processed_data,
        metrics={"score": 0.95},
        output_bids_entities={"suffix": "processed", "extension": ".json"}
    )

# After - Pure computation focus
@neuprocess_decorator(config)
def my_function(input_filepath):
    processed_data = do_processing(input_filepath)
    return {
        "output_data": processed_data,
        "metrics": {"score": 0.95},
        "output_bids_entities": {"suffix": "processed", "extension": ".json"}
    }
```

### 2. **Improved NeuProcessLogic Definitions**
```python
# Before - Duplicated imports
logic = NeuProcessLogic(
    code="""
import numpy as np
from pathlib import Path
# processing code here...
    """,
    import_statements=["import numpy as np", "from pathlib import Path"]  # Duplicate!
)

# After - Clean separation
logic = NeuProcessLogic(
    code="""
# processing code here (no imports)...
    """,
    import_statements=["import numpy as np", "from pathlib import Path"]  # Only here
)
```

### 3. **Validation Inside Decorator**
- The `NeuProcessOutput` pydantic model is now used **internally** by the decorator for validation
- User functions don't need to know about it - they just return dictionaries
- Decorator validates the dictionary structure automatically

## 🧪 Testing Results

All tests and examples pass successfully:

- ✅ **Basic Decorator Usage**: Functions returning dictionaries work correctly
- ✅ **NeuProcessLogic Integration**: Automatic function generation works with clean import handling
- ✅ **Error Handling**: Robust error catching and reporting
- ✅ **BIDS Path Construction**: Proper derivatives structure creation
- ✅ **Metadata Generation**: Comprehensive sidecar JSON files
- ✅ **Batch Processing**: Multiple file processing workflows

## 🎯 Benefits Achieved

1. **Separation of Concerns**: Processing logic is completely separate from NeuroAnalyst infrastructure
2. **Cleaner User Experience**: Users write pure computational functions without framework imports
3. **Better Code Organization**: Wrapper functionality is properly isolated
4. **Easier Maintenance**: Clear boundaries between logic and wrapper components
5. **No Duplication**: Import statements are specified once, not repeated in code
6. **Validation Safety**: Dictionary returns are validated internally for correctness

## 📚 Updated Documentation

- Updated `DECORATOR_README.md` with new usage patterns
- All examples demonstrate dictionary-based returns
- Clear import guidance for different use cases
- Comprehensive documentation of the new structure

---

## 🧠 PyBIDS Integration Implementation (Latest Update)

### Mission: Enhanced BIDS Compliance
We have successfully integrated **PyBIDS** (Python Brain Imaging Data Structure) into the existing NeuProcess wrapper system, enhancing BIDS compliance and neuroimaging data handling capabilities while maintaining full backward compatibility.

### ✅ PyBIDS Features Implemented

#### 1. **PyBIDS Package Integration**
- ✅ Successfully installed `pybids` package
- ✅ Added graceful import handling with fallback support
- ✅ Created availability checking mechanism (`PYBIDS_AVAILABLE` flag)

#### 2. **Enhanced Configuration System**
```python
class NeuProcessDecoratorConfig(BaseModel):
    # Existing fields...
    use_pybids: bool = Field(default=True, description="Whether to use PyBIDS")
    bids_layout: Optional[Any] = Field(default=None, description="Pre-initialized BIDSLayout")
    bids_validate: bool = Field(default=False, description="Whether to validate BIDS compliance")
```

#### 3. **Advanced Entity Extraction**
- **PyBIDS Method (Preferred):** Uses `parse_file_entities()` and `BIDSLayout.get_file().get_entities()`
- **Fallback Method (Robust):** Regex-based extraction supporting common BIDS entities
- **Smart Entity Mapping:** Handles PyBIDS vs fallback entity naming differences

#### 4. **Intelligent Path Construction**
- **PyBIDS Build Path:** Attempts `BIDSLayout.build_path()` with BIDS-compliant patterns
- **Fallback Construction:** Manual BIDS-compliant path building when PyBIDS fails
- **Enhanced Metadata:** Includes PyBIDS dataset information when available

### � PyBIDS Test Results
```
🧠 Comprehensive PyBIDS Integration Tests: ✅ PASSED
============================================================
✅ Simple PyBIDS Integration - Entities: {'subject': '01', 'task': 'rest'}
✅ Fallback Functionality - Manual extraction when PyBIDS disabled  
✅ System Integration - Full backward compatibility maintained
```

### 🎯 PyBIDS Integration Status: **COMPLETE**
Enhanced BIDS compliance achieved while maintaining full backward compatibility.

## �🚀 Next Steps

The wrapper implementation with PyBIDS integration is now complete and ready for:
1. **Integration with NeuProcessDir**: For script generation and containerization
2. **HPC Deployment**: The clean function signatures are perfect for distributed processing
3. **Pipeline Development**: Users can focus on algorithms while the wrapper handles infrastructure
4. **Container Packaging**: Functions can be easily packaged into Singularity/Docker images
5. **Enhanced BIDS Workflows**: Full PyBIDS support for neuroimaging data processing

The implementation successfully fulfills all the requirements from the original instructions while improving code organization, user experience, and BIDS compliance.
