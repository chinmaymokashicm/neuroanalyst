# NeuroAnalyst NeuProcessExec Class

This document provides an overview of the NeuProcessExec class, which is used to execute NeuProcess instances with specific runtime configuration.

## Overview

The NeuProcessExec class serves as a bridge between the abstract NeuProcess definition and the actual execution in a specific environment (local, HPC) and mode (script, container). It handles:

1. Execution of a NeuProcess with specific runtime configuration
2. Generation of execution commands based on environment and mode
3. Validation of bind paths and environment variables
4. Execution of the generated commands

## Class Structure

### Main Components

- **Basic Information**
  - `exec_id`: Unique identifier for the execution instance
  
- **Input Source**
  - `process`: NeuProcess to execute
  
- **Runtime Configuration**
  - `bind_path_values`: Values for bind paths, keyed by bind path name
  - `env_var_values`: Values for environment variables, keyed by variable name
  
- **Execution Options**
  - `execution_mode`: Mode of execution (script, container, auto)
  - `scheduler`: HPC scheduler to use (lsf, slurm, pbs, none)

### Class Methods

- **Creation Methods**
  - `from_process(process, **kwargs)`: Create from a NeuProcess instance
  - `from_process_id(process_id, **kwargs)`: Create from a process ID
  - `from_dir_path(dir_path, **kwargs)`: Create from a path to a process directory
  
- **Configuration Methods**
  - `set_bind_path_value(bind_path, value)`: Set the value for a bind path
  - `set_env_var_value(env_var, value)`: Set the value for an environment variable
  - `get_configuration_status()`: Get details about required, provided, and missing configuration values
  - `print_configuration_status()`: Print a user-friendly report of configuration status
  - `check_configuration_complete()`: Check if all required values are provided
  
- **Execution Methods**
  - `determine_execution_mode()`: Determine the execution mode based on current configuration
  - `generate_command()`: Generate the execution command
  - `execute()`: Execute the generated command
  - `dry_run()`: Perform a dry run of the execution

## Usage Examples

### Basic Usage

```python
from src.neuroanalyst.models.process import NeuProcess, NeuProcessExec

# Create a NeuProcessExec from a NeuProcess without providing all required values
process = NeuProcess.from_process_id("PR-123456")
process_exec = NeuProcessExec(process=process)

# Check what values are missing
process_exec.print_configuration_status()

# Set required values
process_exec.set_bind_path_value("/data", "/path/to/data")
process_exec.set_bind_path_value("/output", "/path/to/output")
process_exec.set_env_var_value("BIDS_ROOT", "/path/to/bids")
process_exec.set_env_var_value("PIPELINE_NAME", "test_pipeline")

# Check that all values are now provided
process_exec.print_configuration_status()

# Generate and execute the command
cmd = process_exec.generate_command()
result = process_exec.execute()
```

### Using Different Schedulers

```python
from src.neuroanalyst.models.process import NeuProcessExec, HPCScheduler

# LSF Scheduler
process_exec_lsf = NeuProcessExec(
    process=process,
    bind_path_values={"...": "..."},
    env_var_values={"...": "..."},
    scheduler=HPCScheduler.LSF
)

# SLURM Scheduler
process_exec_slurm = NeuProcessExec(
    process=process,
    bind_path_values={"...": "..."},
    env_var_values={"...": "..."},
    scheduler=HPCScheduler.SLURM
)
```

### Dry Run for Testing

```python
process_exec = NeuProcessExec(
    process=process,
    bind_path_values={"...": "..."},
    env_var_values={"...": "..."}
)

# Get information about what would be executed
dry_run_info = process_exec.dry_run()
print(dry_run_info)
```

### Configuration Status

```python
# Create with partial configuration
process_exec = NeuProcessExec(
    process=process,
    bind_path_values={"/data": "/path/to/data"},  # Missing other paths
    env_var_values={"BIDS_ROOT": "/path/to/bids"}  # Missing other vars
)

# Print a user-friendly report of what's provided and what's missing
process_exec.print_configuration_status()

# Get programmatic access to configuration status
status = process_exec.get_configuration_status()
print(f"Missing bind paths: {status['bind_paths']['missing']}")
print(f"Missing env vars: {status['environment_variables']['missing']}")

# Check if configuration is complete
if process_exec.check_configuration_complete():
    print("Ready to execute!")
else:
    print("Configuration incomplete")
```

### Path Normalization

```python
# Path normalization automatically handles trailing slashes
process_exec = NeuProcessExec(process=process)

# These are treated as the same path
process_exec.set_bind_path_value("/data", "/path/to/data")  # Original path
process_exec.set_bind_path_value("/data/", "/updated/path") # With trailing slash

# The value will be stored using the original required path name from the process
print(process_exec.bind_path_values)  # Shows {"/data": "/updated/path"}

# Configuration status will correctly show this path as provided
status = process_exec.get_configuration_status()
print(status["bind_paths"]["missing"])  # Won't include "/data"
```
