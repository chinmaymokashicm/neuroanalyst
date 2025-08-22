# NeuProcessDir: Template-Based Code Generation for NeuroAnalyst

## Overview

**NeuProcessDir** is a comprehensive template-based system for generating standardized neuroimaging processing scripts from **NeuProcessLogic**. It takes user-defined functions (UDFs) wrapped by the NeuroAnalyst decorator and generates two main types of scripts:

1. **Main Logic Script** - Executes the wrapped processing function
2. **Environment Setup Script** - Installs all required dependencies

These generated scripts form the foundation for creating **NeuProcess** instances, which are then containerized as Singularity images for deployment.

## Architecture Flow

```
User Function (UDF)
       ↓
NeuProcessLogic (wrapped with decorator)
       ↓
NeuProcessDir (template-based generation)
       ↓
Generated Scripts (main.py + install_requirements.sh)
       ↓
NeuProcess (Singularity container)
       ↓
NeuPipeline (orchestrated NeuProcessExec instances)
```

## Key Components

### NeuProcessLogic Integration
- Takes UDFs wrapped with the NeuroAnalyst decorator
- Generates standardized output format
- Ensures BIDS compliance and provenance tracking

### Template-Based Generation
- **main.py.template** - Main execution script with parallel processing capabilities
- **requirements_script.sh.template** - Environment setup and dependency installation
- **readme.md.template** - Comprehensive documentation
- **singularity.def.template** - Container definition for Singularity images

### Process Identification
- Unique Process IDs in format `PR-XXXXXX` (e.g., `PR-123456`)
- Clean separation between process definition and execution
- Supports future pipeline and execution ID integration

## Usage

### Basic Usage

```python
from app.models.about import About
from app.models.process.logic.core import NeuProcessLogic, NeuProcessLogicArgument
from app.models.process.dir.core import NeuProcessDir, NeuProcessDirConfig

# Create About information
about = About(
    name="brain_volume_calculator",
    description="Calculate brain volume from structural MRI",
    version="1.0.0",
    author="Dr. Researcher"
)

# Define processing logic with wrapped UDF
logic = NeuProcessLogic(
    about=about,
    code='''
# Your wrapped function code here
# Returns standardized output format
volume = calculate_brain_volume(input_file)
return output_data, metrics, output_entities
''',
    arguments=[
        NeuProcessLogicArgument(name="input_file", type="str", description="Input file path")
    ]
)

# Configure environment
config = NeuProcessDirConfig(
    python_packages=["nibabel", "numpy"],
    parallel_execution=True,
    max_workers=4
)

# Generate directory structure
neu_dir = NeuProcessDir(logic=logic, config=config)
output_path = neu_dir.create_directory(Path("./my_process"))
```

### Generated Directory Structure

```
PR-123456/
├── main.py                     # Main execution script
├── install_requirements.sh     # Environment setup script  
├── neuprocess_config.json      # Process configuration
├── README.md                   # Documentation
├── PR-123456.def              # Singularity definition
└── execute.sh                  # HPC execution helper
```

## Future Integration

### NeuProcess Creation
The generated scripts will be used to create **NeuProcess** instances:
- Singularity containerization using `PR-XXXXXX.def`
- Standardized execution interface
- BIDS-compliant processing pipeline

### NeuPipeline Orchestration
Multiple NeuProcess instances will be orchestrated through **NeuPipeline**:
- **NeuProcessExec** instances for each process execution
- Sequential or parallel arrangement
- Pipeline-level provenance and monitoring

## Configuration Options

### NeuProcessDirConfig
- `python_packages`: Additional Python packages to install
- `base_packages`: Core packages (pybids, nibabel, etc.)
- `parallel_execution`: Enable/disable parallel processing
- `max_workers`: Maximum parallel workers
- `bids_validate`: BIDS compliance validation
- `base_container_image`: Base container for Singularity

## Template Variables

Templates use the following variables from the NeuProcessLogic:
- `{pipeline_name}` - Process name from About.name
- `{author}` - Author from About.author
- `{description}` - Description from About.description
- `{version}` - Version from About.version
- `{process_id}` - Unique process identifier
- `{function_name}` - Name of the wrapped function

## Execution Requirements

Generated scripts require:
- `--pipeline-name`: Name of the processing pipeline
- `--pipeline-id`: Unique pipeline identifier
- `--process-exec-id`: Unique process execution identifier
- `--bids-filters`: BIDS filters for file selection
- `bids_root`: Path to BIDS dataset

## Dependencies

- **pydantic**: Data validation and modeling
- **pathlib**: Path manipulation
- **json**: Configuration file handling
- **datetime**: Timestamp generation
- **app.models.process.logic.core**: NeuProcessLogic integration
- **app.utils.id_generators**: Generic ID generation framework
