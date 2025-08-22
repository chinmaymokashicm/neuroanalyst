# NeuroAnalyst Constants and Environment Setup

This document explains the constants module and environment setup for the NeuroAnalyst framework.

## Overview

The NeuroAnalyst framework uses a centralized constants module (`app/utils/constants.py`) to manage all paths, configuration values, and environment variables. This ensures consistency across the entire codebase and makes the framework highly configurable.

## Environment Variables

The framework relies on the following environment variables, which are automatically set by running `setup.sh`:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `NEUROANALYST_HOME` | Base directory for NeuroAnalyst | `$HOME/neuroanalyst` |
| `NEUROANALYST_IMAGES` | Directory for Singularity images | `$NEUROANALYST_HOME/apptainer/images` |
| `NEUROANALYST_DOCS` | Directory for documentation and def files | `$NEUROANALYST_HOME/apptainer/docs` |
| `NEUROANALYST_WORKDIR` | Working directory for temporary files | `$NEUROANALYST_HOME/working_dirs` |
| `NEUROANALYST_REPORTS` | Directory for reports and outputs | `$NEUROANALYST_HOME/reports` |
| `NEUROANALYST_LOGS` | Directory for log files | `$NEUROANALYST_HOME/logs` |
| `NEUROANALYST_DATASETS` | Directory for BIDS datasets | `$NEUROANALYST_HOME/datasets` |

## Directory Structure

The framework creates the following directory structure:

```
~/neuroanalyst/
├── apptainer/
│   ├── images/
│   │   ├── base/          # Base Singularity images
│   │   ├── processes/     # NeuProcess images
│   │   └── pipelines/     # NeuPipeline images
│   └── docs/              # Singularity definition files
├── working_dirs/          # Temporary working directories
│   ├── [process_id]/      # Process-specific work dirs
│   └── pipelines/         # Pipeline work dirs
│       └── [pipeline_id]/
├── reports/               # Generated reports
├── logs/                  # Log files
└── datasets/              # BIDS datasets
    └── [dataset_name]/
        └── derivatives/   # Processing outputs
            └── [pipeline_name]/
```

## Usage

### Importing Constants

```python
from app.utils import PATHS, CONFIG, ensure_directories
```

### Path Management

```python
# Get standard paths
home_dir = PATHS.home
images_dir = PATHS.images
workdir = PATHS.workdir

# Get specific subdirectories
base_images = PATHS.base_images
process_images = PATHS.process_images

# Get process-specific paths
process_workdir = PATHS.get_process_workdir("my_process_123")
process_image = PATHS.get_process_image_path("fsl_bet", "v1.0")

# Get log file paths
log_file = PATHS.get_log_file_path("neuprocess", "proc_123")
```

### Configuration Constants

```python
# File extensions
singularity_ext = CONFIG.SINGULARITY_EXTENSION  # '.sif'
python_ext = CONFIG.PYTHON_EXTENSION           # '.py'

# Default file names
main_script = CONFIG.MAIN_SCRIPT_NAME          # 'main.py'
install_script = CONFIG.INSTALL_SCRIPT_NAME    # 'install_requirements.sh'

# BIDS constants
derivatives = CONFIG.DERIVATIVES_DIR            # 'derivatives'

# Default values
python_version = CONFIG.DEFAULT_PYTHON_VERSION  # '3.12'
base_image = CONFIG.DEFAULT_BASE_IMAGE          # 'ubuntu:22.04'
```

### Directory Setup

```python
# Ensure all directories exist
ensure_directories()

# Create process-specific working directory
process_id = "my_process_123"
process_workdir = PATHS.get_process_workdir(process_id)
process_workdir.mkdir(parents=True, exist_ok=True)
```

### Template Management

```python
from app.utils import get_template_path

# Get template file paths
main_template = get_template_path(CONFIG.MAIN_SCRIPT_TEMPLATE)
readme_template = get_template_path(CONFIG.README_TEMPLATE)
singularity_template = get_template_path(CONFIG.SINGULARITY_TEMPLATE)
```

### Environment Validation

```python
from app.utils import validate_environment

# Check if all required environment variables are set
if not validate_environment():
    print("Please run setup.sh to configure the environment")
```

## Integration Examples

### NeuProcess Setup

```python
from app.utils import PATHS, CONFIG, ensure_directories

def create_neuprocess(process_name: str, version: str = "v1.0"):
    # Ensure directories exist
    ensure_directories()
    
    # Generate process ID
    from app.utils import generate_available_process_id
    process_id = generate_available_process_id()
    
    # Get paths
    workdir = PATHS.get_process_workdir(process_id)
    image_path = PATHS.get_process_image_path(process_name, version)
    
    # Create working directory
    workdir.mkdir(parents=True, exist_ok=True)
    
    # Create process files
    main_script = workdir / CONFIG.MAIN_SCRIPT_NAME
    install_script = workdir / CONFIG.INSTALL_SCRIPT_NAME
    config_file = workdir / CONFIG.CONFIG_NAME
    
    return {
        'process_id': process_id,
        'workdir': workdir,
        'image_path': image_path,
        'main_script': main_script,
        'install_script': install_script,
        'config_file': config_file
    }
```

### BIDS Dataset Processing

```python
def setup_pipeline_output(dataset_name: str, pipeline_name: str):
    # Get dataset path
    dataset_path = PATHS.datasets / dataset_name
    
    # Create derivatives directory
    derivatives_path = dataset_path / CONFIG.DERIVATIVES_DIR
    pipeline_output = derivatives_path / pipeline_name
    
    # Ensure directories exist
    pipeline_output.mkdir(parents=True, exist_ok=True)
    
    return pipeline_output
```

### Logging Setup

```python
import logging
from app.utils import PATHS, CONFIG

def setup_logging(component: str, process_id: str = None):
    # Get log file path
    log_file = PATHS.get_log_file_path(component, process_id)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(f"neuroanalyst.{component}")
    
    # Set up file handler
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(CONFIG.LOG_FORMAT, CONFIG.LOG_DATE_FORMAT)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger
```

## Best Practices

1. **Always use constants**: Never hardcode paths or configuration values. Use the constants module.

2. **Check environment**: Call `validate_environment()` at the start of critical operations.

3. **Create directories**: Use `ensure_directories()` or create specific directories as needed.

4. **Use helper methods**: Leverage the helper methods like `get_process_workdir()` for consistent path generation.

5. **Template-based generation**: Use the template system for creating consistent process files.

## Testing

To test the constants setup:

```bash
# Run the test script
python test_constants.py

# Or run individual tests
python example_constants_usage.py
```

## Troubleshooting

### Environment Variables Not Set

If you get warnings about missing environment variables:

```bash
# Re-run the setup
source setup.sh

# Or just set the environment variables
source set_envs.sh
```

### Directory Permission Issues

If you encounter permission issues:

```bash
# Check directory permissions
ls -la ~/neuroanalyst/

# Fix permissions if needed
chmod -R 755 ~/neuroanalyst/
```

### Import Errors

If you get import errors:

```python
# Make sure to add the app directory to Python path
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))

# Then import the constants
from utils.constants import PATHS, CONFIG
```
