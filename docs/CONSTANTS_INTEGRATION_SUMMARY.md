# Constants Integration Summary

## Overview
Successfully integrated the NeuroAnalyst constants system throughout the codebase, providing centralized configuration management for all paths, file names, extensions, and default values.

## Changes Made

### 1. Constants Module (`app/utils/constants.py`)
- **`NeuroAnalystPaths` class**: Centralized path management with environment variable support
- **`NeuroAnalystConfig` class**: Configuration constants for extensions, defaults, and naming conventions
- **Helper functions**: `ensure_directories()`, `get_template_path()`, `validate_environment()`
- **Global instances**: `PATHS` and `CONFIG` for easy access throughout the framework

### 2. Environment Setup (`set_envs.sh`)
- Added missing directories (`logs`, `datasets`)
- Uncommented `NEUROANALYST_DOCS` environment variable
- Complete directory structure creation

### 3. NeuProcessDir Integration (`app/models/process/dir/core.py`)
#### Imports Updated
```python
from ....utils import PATHS, CONFIG, generate_available_process_id
```

#### Configuration Defaults
- `max_workers`: Uses `CONFIG.DEFAULT_N_PROCS` (4)
- `derivatives_dir`: Uses `CONFIG.DERIVATIVES_DIR` ("derivatives")
- `base_container_image`: Uses `CONFIG.DEFAULT_BASE_IMAGE` ("ubuntu:22.04")

#### Path Management
- `create_directory()`: Uses `PATHS.workdir` as default if no path provided
- Process ID generation: Uses constants-based `generate_available_process_id()`

#### File Creation
- Template loading: Uses `CONFIG.MAIN_SCRIPT_TEMPLATE`, `CONFIG.README_TEMPLATE`, etc.
- File naming: Uses `CONFIG.MAIN_SCRIPT_NAME`, `CONFIG.INSTALL_SCRIPT_NAME`, etc.
- Extensions: Uses `CONFIG.DEFINITION_EXTENSION`, `CONFIG.SINGULARITY_EXTENSION`

#### Generated Files (with constant-based names)
- `main.py` (`CONFIG.MAIN_SCRIPT_NAME`)
- `install_requirements.sh` (`CONFIG.INSTALL_SCRIPT_NAME`)
- `neuprocess_config.json` (`CONFIG.CONFIG_NAME`)
- `README.md` (`CONFIG.README_NAME`)
- `execute.sh` (`CONFIG.EXECUTE_SCRIPT_NAME`)
- `{process_id}.def` (`CONFIG.DEFINITION_EXTENSION`)

### 4. NeuProcessWrapper Integration (`app/models/process/wrapper/core.py`)
#### Imports Updated
```python
from ....utils import PATHS, CONFIG
```

#### Configuration Updates
- `derivatives_dir`: Default changed from `None` to `CONFIG.DERIVATIVES_DIR`
- Sidecar file creation: Uses `CONFIG.JSON_EXTENSION` and `CONFIG.BIDS_SIDECAR_SUFFIX`

### 5. ID Generators Integration (`app/utils/id_generators.py`)
- `generate_available_process_id()`: Now accepts optional `base_path`, defaults to `PATHS.workdir`

### 6. Updated README.md
- Added constants import in examples
- Shows proper directory structure
- References Constants Guide documentation

## Directory Structure Created

```
~/neuroanalyst/
├── apptainer/
│   ├── images/
│   │   ├── base/          # Base Singularity images
│   │   ├── processes/     # NeuProcess images
│   │   └── pipelines/     # NeuPipeline images
│   └── docs/              # Definition files
├── working_dirs/          # Temporary processing
├── reports/               # Generated outputs
├── logs/                  # Framework logs
└── datasets/              # BIDS datasets
```

## Key Constants Defined

### Path Constants (from environment variables)
- `PATHS.home`: `~/neuroanalyst`
- `PATHS.images`: `~/neuroanalyst/apptainer/images`
- `PATHS.base_images`: `~/neuroanalyst/apptainer/images/base`
- `PATHS.process_images`: `~/neuroanalyst/apptainer/images/processes`
- `PATHS.pipeline_images`: `~/neuroanalyst/apptainer/images/pipelines`
- `PATHS.workdir`: `~/neuroanalyst/working_dirs`
- `PATHS.reports`: `~/neuroanalyst/reports`
- `PATHS.logs`: `~/neuroanalyst/logs`
- `PATHS.datasets`: `~/neuroanalyst/datasets`

### File Extension Constants
- `CONFIG.SINGULARITY_EXTENSION`: `.sif`
- `CONFIG.DEFINITION_EXTENSION`: `.def`
- `CONFIG.PYTHON_EXTENSION`: `.py`
- `CONFIG.SHELL_EXTENSION`: `.sh`
- `CONFIG.JSON_EXTENSION`: `.json`
- `CONFIG.BIDS_SIDECAR_SUFFIX`: `.json`

### Default File Names
- `CONFIG.MAIN_SCRIPT_NAME`: `main.py`
- `CONFIG.INSTALL_SCRIPT_NAME`: `install_requirements.sh`
- `CONFIG.EXECUTE_SCRIPT_NAME`: `execute.sh`
- `CONFIG.README_NAME`: `README.md`
- `CONFIG.CONFIG_NAME`: `neuprocess_config.json`

### Template Names
- `CONFIG.MAIN_SCRIPT_TEMPLATE`: `main_script.py.template`
- `CONFIG.README_TEMPLATE`: `readme.md.template`
- `CONFIG.REQUIREMENTS_TEMPLATE`: `requirements_script.sh.template`
- `CONFIG.SINGULARITY_TEMPLATE`: `singularity.def.template`

### Default Values
- `CONFIG.DEFAULT_PYTHON_VERSION`: `3.12`
- `CONFIG.DEFAULT_BASE_IMAGE`: `ubuntu:22.04`
- `CONFIG.DEFAULT_N_PROCS`: `4`
- `CONFIG.DERIVATIVES_DIR`: `derivatives`

## Testing

### Integration Tests Created
1. **`test_constants.py`**: Basic constants functionality
2. **`test_constants_integration.py`**: End-to-end integration testing
3. **`example_constants_usage.py`**: Practical usage examples

### Test Results
All integration tests pass:
- ✅ Constants module imports and validates environment
- ✅ Directory structure created correctly
- ✅ File extensions and naming conventions work
- ✅ Template constants are accessible
- ✅ Path generation functions correctly

## Benefits

### 1. Centralized Configuration
- Single source of truth for all paths and constants
- Easy to modify default values across the entire framework
- Environment-based configuration with fallbacks

### 2. Consistency
- Standardized file naming across all components
- Uniform directory structure
- Consistent extension usage

### 3. Maintainability
- Changes to paths/names only need to be made in one place
- Clear separation between configuration and logic
- Type-safe path operations using `pathlib.Path`

### 4. Flexibility
- Environment variable override support
- Configurable through setup scripts
- Easy to extend with new constants

### 5. Robustness
- Environment validation on import
- Automatic directory creation
- Error handling for missing paths

## Usage Examples

### Basic Usage
```python
from app.utils import PATHS, CONFIG, ensure_directories

# Ensure directories exist
ensure_directories()

# Get paths
workdir = PATHS.get_process_workdir("my_process")
image_path = PATHS.get_process_image_path("fsl_bet", "v1.0")

# Use file names
main_script = workdir / CONFIG.MAIN_SCRIPT_NAME
```

### NeuProcessDir with Constants
```python
from app.utils import PATHS, CONFIG
from app.models.process.dir.core import NeuProcessDir, NeuProcessDirConfig

config = NeuProcessDirConfig(
    base_container_image=CONFIG.DEFAULT_BASE_IMAGE,
    max_workers=CONFIG.DEFAULT_N_PROCS
)

neuprocess_dir = NeuProcessDir(logic=logic, config=config)
output_path = neuprocess_dir.create_directory()  # Uses PATHS.workdir by default
```

## Next Steps

1. **Extend to Other Modules**: Apply constants integration to remaining modules (pipeline, execution, etc.)
2. **Template System**: Implement template loading and processing using the template constants
3. **Configuration Files**: Add support for user configuration files that can override defaults
4. **Documentation**: Complete the Constants Guide with more examples and best practices

## Files Modified

1. `app/utils/constants.py` - **NEW**: Complete constants module
2. `app/utils/__init__.py` - Updated exports
3. `app/utils/id_generators.py` - Integrated with constants
4. `app/models/process/dir/core.py` - Full constants integration
5. `app/models/process/wrapper/core.py` - Basic constants integration
6. `set_envs.sh` - Added missing directories and variables
7. `README.md` - Updated examples to show constants usage
8. `docs/CONSTANTS_GUIDE.md` - **NEW**: Comprehensive documentation
9. `test_constants.py` - **NEW**: Basic testing
10. `test_constants_integration.py` - **NEW**: Integration testing
11. `example_constants_usage.py` - **NEW**: Usage examples

The constants integration provides a solid foundation for the entire NeuroAnalyst framework, ensuring consistency, maintainability, and ease of configuration across all components.
