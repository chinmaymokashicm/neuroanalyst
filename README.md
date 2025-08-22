# NeuroAnalyst

NeuroAnalyst is a comprehensive framework for standardizing and automating neuroimaging data processing workflows. It transforms Python functions into complete, BIDS-compliant processing pipelines with containerized execution and rich metadata management.

## Key Features

- **Function-to-Pipeline**: Convert Python functions into complete processing workflows
- **BIDS Compliance**: Automatic dataset validation and metadata generation  
- **Containerization**: Generate Singularity containers with all dependencies
- **Generic ID Framework**: Unified identification system across all components
- **Template-Based Generation**: Standardized script and container creation
- **HPC Integration**: Optimized for high-performance computing environments

## Quick Start

### Environment Setup

First, set up the NeuroAnalyst environment:

```bash
# Clone the repository
git clone https://github.com/chinmaymokashicm/neuroanalyst.git
cd neuroanalyst

# Run setup script (creates virtual environment, installs dependencies, sets environment variables)
source setup.sh
```

This creates the following directory structure:

```
~/neuroanalyst/
├── apptainer/images/      # Singularity images (base, processes, pipelines)
├── working_dirs/          # Temporary processing directories
├── reports/              # Generated reports and outputs
├── logs/                 # Framework log files
└── datasets/             # BIDS datasets and derivatives
```

### Basic Usage

```python
from app.utils import PATHS, CONFIG, ensure_directories
from app.models.process.wrapper import neuprocess, NeuProcessDecoratorConfig
from app.models.process.dir.core import NeuProcessDir, NeuProcessDirConfig
from app.models.process.logic.core import NeuProcessLogic
from app.models.about import About

# Ensure all directories are set up
ensure_directories()

# 1. Define your analysis function
def brain_volume_analysis(input_file, output_dir):
    """Calculate brain volume from structural MRI."""
    # Your analysis logic here
    return results

# 2. Create NeuProcessLogic with metadata
logic = NeuProcessLogic(
    about=About(
        name="brain_volume_analysis",
        description="Brain volume calculation pipeline",
        author="Your Name"
    ),
    arguments=[],  # Define arguments as needed
    code="# Your function code here"
)

# 3. Generate complete directory structure
config = NeuProcessDirConfig()
neuprocess_dir = NeuProcessDir(logic=logic, config=config)

# 4. Create scripts and containers using the configured paths
output_path = neuprocess_dir.create_directory(PATHS.get_process_workdir("my_process"))
```

This generates:
- `main.py`: BIDS-compliant processing script
- `neuprocess.def`: Singularity container definition  
- `execute.sh`: HPC job submission script
- Complete documentation and metadata

For detailed information about paths and configuration, see [Constants Guide](docs/CONSTANTS_GUIDE.md).

## Component Architecture & Relationships

The following UML diagrams illustrate the detailed relationships between all the core components we've developed in NeuroAnalyst:

### Core Component Class Diagram

```mermaid
classDiagram
    class UserDefinedFunction {
        +String name
        +String description
        +Function logic
        +execute()
    }
    
    class NeuProcessLogic {
        +About metadata
        +List~Argument~ arguments
        +ProgrammingLanguage language
        +String code
        +validate()
        +encode()
    }
    
    class NeuProcessDir {
        +NeuProcessLogic logic
        +NeuProcessDirConfig config
        +String process_id
        +Path output_directory
        +create_directory()
        +generate_scripts()
    }
    
    class NeuProcess {
        +String image_id
        +String container_path
        +Dict environment
        +List~String~ dependencies
        +execute()
        +build_container()
    }
    
    class NeuProcessExec {
        +String exec_id
        +NeuProcess process
        +Dict parameters
        +ExecutionStatus status
        +Dict results
        +run()
        +monitor()
    }
    
    class NeuPipeline {
        +String pipeline_id
        +List~NeuProcessExec~ executions
        +Dict dependencies
        +PipelineStatus status
        +execute_pipeline()
        +manage_dag()
    }
    
    %% Core workflow relationships
    UserDefinedFunction --> NeuProcessLogic : "decorated by"
    NeuProcessLogic --> NeuProcessDir : "generates"
    NeuProcessDir --> NeuProcess : "creates"
    NeuProcess --> NeuProcessExec : "instantiated as"
    NeuProcessExec --> NeuPipeline : "orchestrated by"
    
    %% Supporting infrastructure
    class IDGenerationFramework {
        +Dict~String~ ID_CONFIGS
        +generate_id(type)
        +validate_id(id)
        +check_availability(id)
    }
    
    class TemplateSystem {
        +Dict templates
        +render_template(name, vars)
        +validate_template()
    }
    
    class ConfigurationManager {
        +validate_bids()
        +manage_parameters()
        +setup_environment()
    }
    
    %% Infrastructure relationships
    IDGenerationFramework --> NeuProcessDir : "provides IDs"
    IDGenerationFramework --> NeuProcess : "provides IDs"
    IDGenerationFramework --> NeuProcessExec : "provides IDs"
    IDGenerationFramework --> NeuPipeline : "provides IDs"
    
    TemplateSystem --> NeuProcessDir : "used by"
    ConfigurationManager --> NeuProcessLogic : "validates"
    ConfigurationManager --> NeuProcessDir : "configures"
```

### Component Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant UDF as User-Defined Function
    participant NPL as NeuProcessLogic
    participant NPD as NeuProcessDir
    participant NP as NeuProcess
    participant NPE as NeuProcessExec
    participant Pipeline as NeuPipeline
    participant IDGen as ID Framework
    participant Templates as Template System
    
    User->>UDF: Write analysis function
    UDF->>NPL: Apply @neuprocess decorator
    NPL->>NPL: Add metadata & validation
    
    NPL->>NPD: Create directory structure
    NPD->>IDGen: Request process_id
    IDGen-->>NPD: Return PR-XXXXXX
    
    NPD->>Templates: Request script templates
    Templates-->>NPD: Python/Docker/Singularity templates
    NPD->>NPD: Generate scripts with parameters
    
    NPD->>NP: Build Singularity container
    NP->>NP: Package dependencies
    
    Pipeline->>NPE: Create execution instance
    NPE->>IDGen: Request exec_id
    IDGen-->>NPE: Return PE-XXXXXX
    
    Pipeline->>NPE: Execute with parameters
    NPE->>NP: Run containerized process
    NP-->>NPE: Return results
    NPE-->>Pipeline: Execution complete
```

### System Architecture Overview

```mermaid
graph TB
    subgraph "User Layer"
        UDF[User-Defined Function<br/>Raw Python Logic]
    end
    
    subgraph "Processing Layer"
        NPL[NeuProcessLogic<br/>Decorated Function]
        NPD[NeuProcessDir<br/>Script Generator]
        NP[NeuProcess<br/>Singularity Container]
        NPE[NeuProcessExec<br/>Runtime Instance]
        Pipeline[NeuPipeline<br/>Orchestrator]
    end
    
    subgraph "Infrastructure Layer"
        IDGen[ID Generation Framework<br/>• process_id: PR-XXXXXX<br/>• pipeline_id: PL-XXXXXX<br/>• exec_id: PE-XXXXXX]
        Templates[Template System<br/>• Python scripts<br/>• Dockerfiles<br/>• Singularity definitions]
        Config[Configuration Management<br/>• BIDS validation<br/>• Parameter handling<br/>• Environment setup]
    end
    
    subgraph "Execution Parameters"
        Params[Container Parameters<br/>--pipeline-name<br/>--pipeline-id<br/>--process-exec-id<br/>--bids-filters<br/>--bids-root]
    end
    
    %% Main flow
    UDF --> NPL
    NPL --> NPD
    NPD --> NP
    NP --> NPE
    NPE --> Pipeline
    
    %% Infrastructure connections
    IDGen -.-> NPD
    IDGen -.-> NP
    IDGen -.-> NPE
    IDGen -.-> Pipeline
    
    Templates -.-> NPD
    Config -.-> NPL
    Config -.-> NPD
    
    Params -.-> NP
    Params -.-> NPE
    
    classDef userLayer fill:#e1f5fe
    classDef processingLayer fill:#f3e5f5
    classDef infraLayer fill:#e8f5e8
    classDef paramLayer fill:#fff3e0
    
    class UDF userLayer
    class NPL,NPD,NP,NPE,Pipeline processingLayer
    class IDGen,Templates,Config infraLayer
    class Params paramLayer
```

### Component Relationships

#### **Core Processing Flow**
1. **UserDefinedFunction** → **NeuProcessLogic**: Raw functions are decorated with metadata and validation
2. **NeuProcessLogic** → **NeuProcessDir**: Decorated functions generate complete directory structures
3. **NeuProcessDir** → **NeuProcess**: Directory structures become Singularity containers
4. **NeuProcess** → **NeuProcessExec**: Containers are instantiated for specific executions
5. **NeuProcessExec** → **NeuPipeline**: Executions are orchestrated in workflows

#### **Infrastructure Support**
- **ID Generation Framework**: Provides unique identifiers for all components using configurable prefixes
- **Template System**: Standardizes script and container generation with proper parameter handling
- **Configuration Management**: Ensures BIDS compliance and validates execution parameters

#### **Key Features**
- **Generic ID System**: Supports `process_id`, `pipeline_id`, `process_exec_id`, `neuprocess_id`, `neuprocess_exec_id`
- **Corrected Parameters**: All containers use `--pipeline-name`, `--pipeline-id`, `--process-exec-id`, `--bids-filters`, `--bids-root`
- **Template-Based Generation**: Consistent script and container creation across all components
- **Metadata Preservation**: Rich metadata flows through the entire processing chain

## Architecture

NeuroAnalyst follows a structured component hierarchy that transforms user functions into executable pipelines:

**Core Processing Flow:**
1. **User-Defined Function** → **NeuProcessLogic** (decorator with metadata)
2. **NeuProcessLogic** → **NeuProcessDir** (script and container generation)  
3. **NeuProcessDir** → **NeuProcess** (Singularity containers)
4. **NeuProcess** → **NeuProcessExec** (runtime instances)
5. **NeuProcessExec** → **NeuPipeline** (workflow orchestration)

**Supporting Infrastructure:**
- **ID Generation Framework**: Unified system for unique component identification
- **Template System**: Standardized script and container generation
- **Configuration Management**: BIDS validation and parameter handling

## Current Implementation Status

### Core Framework ✅ **Implemented**
- **NeuProcessLogic**: Function decoration with metadata and validation
- **NeuProcessDir**: Complete script and container generation system  
- **Generic ID Framework**: Supports `process_id`, `pipeline_id`, `process_exec_id`, `neuprocess_id`, `neuprocess_exec_id`
- **Template System**: Python scripts, Dockerfiles, and Singularity definitions
- **BIDS Integration**: PyBIDS-based validation and path construction

### Container Parameters ✅ **Corrected**
All generated containers use the standardized parameter set:
- `--pipeline-name`: Processing pipeline identifier
- `--pipeline-id`: Unique pipeline ID  
- `--process-exec-id`: Execution instance ID
- `--bids-filters`: Dataset filtering criteria
- `--bids-root`: BIDS dataset root directory

### In Development 🚧
- **NeuProcess**: Singularity container management and execution
- **NeuPipeline**: Multi-process workflow orchestration and DAG management
- **NeuProcessExec**: Runtime execution instances with parameter tracking

### Future Development 📋
- **Enhanced TUI**: Form-based input and interactive pipeline visualization
- **Insight API**: LLM-powered knowledge discovery and result contextualization
- **HPC Integration**: Advanced job scheduling and resource management
- **Collaborative Features**: Pipeline sharing and version control

## Examples

Working examples are available in:
- `app/models/process/wrapper/examples/` - Decorator usage examples
- `app/models/process/wrapper/tests/` - Integration tests
- `app/models/process/dir/tests/` - Directory generation tests

## What Makes NeuroAnalyst Different

### 1. Function-Centric Development
Transform Python functions directly into complete processing pipelines without complex container definitions or deployment scripts.

### 2. BIDS-First Architecture  
Built-in BIDS compliance ensures datasets are structured correctly and metadata is preserved throughout processing.

### 3. Generic Infrastructure
Unified ID generation, template system, and configuration management support any neuroimaging workflow.

### 4. Container-Ready Output
Automatic generation of Singularity containers optimized for HPC environments with proper security controls.

### 5. Metadata Preservation
Rich metadata flows through the entire processing chain, enabling reproducibility and provenance tracking.