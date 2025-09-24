# Sync Module Documentation

The Sync module provides a comprehensive framework for synchronizing NeuroAnalyst components between HPC storage and MongoDB. This allows for data persistence, tracking changes, and maintaining consistency between computational environments and databases.

## Core Components

### SyncBase

The base class that provides common functionality for all sync components:

- Direction enums (HPC_TO_DB, DB_TO_HPC)
- Strategy enums (AD_HOC, PERIODIC)
- Common methods for comparing dictionaries and handling differences

### Component-Specific Sync Classes

The module provides specialized sync classes for each NeuroAnalyst component:

1. **NeuProcessSync**: Synchronize NeuProcess instances
2. **NeuProcessExecSync**: Synchronize NeuProcessExec instances
3. **NeuPipelineSync**: Synchronize NeuPipeline instances
4. **LogSync**: Synchronize log files for all components

## Key Functionality

Each sync component provides five core methods:

1. **load_from_hpc(component_id)**: Load component data from HPC storage
2. **load_from_db(component_id)**: Load component data from MongoDB
3. **compare_diff(component_id)**: Compare differences between HPC and DB data
4. **sync_to_db(component)**: Synchronize data from HPC to DB
5. **sync_from_db(component_id)**: Synchronize data from DB to HPC

## Usage Examples

### Comparing Differences

```python
from neuroanalyst.models.sync import NeuProcessSync

# Initialize sync object
process_sync = NeuProcessSync()

# Compare differences between HPC and DB for a process
diff = process_sync.compare_diff("process_001")
print(diff)
```

### Syncing from HPC to DB

```python
from neuroanalyst.models.sync import NeuPipelineSync

# Initialize sync object
pipeline_sync = NeuPipelineSync()

# Sync pipeline data from HPC to DB
doc_id = pipeline_sync.sync_to_db("pipeline_001")
print(f"MongoDB document ID: {doc_id}")
```

### Syncing from DB to HPC

```python
from neuroanalyst.models.sync import NeuProcessExecSync

# Initialize sync object
exec_sync = NeuProcessExecSync()

# Sync execution data from DB to HPC
success = exec_sync.sync_from_db("exec_001")
print(f"Sync successful: {success}")
```

### Syncing Logs

```python
from neuroanalyst.models.sync import LogSync

# Initialize sync object
log_sync = LogSync()

# Sync logs for a process
doc_id = log_sync.sync_to_db("process_001", "process")
print(f"MongoDB log document ID: {doc_id}")
```

## Integration with Other Components

The Sync module is designed to work seamlessly with other NeuroAnalyst components:

- **MongoDB Client**: Uses the MongoDB client for database operations
- **Constants**: Leverages path definitions for locating component files
- **Component Models**: Works with NeuProcess, NeuProcessExec, and NeuPipeline models

## Command-Line Interface

A demonstration script is provided to show how to use the sync module from the command line:

```bash
# Sync a process from HPC to DB
python src/neuroanalyst/scripts/sync_demo.py --component-type process --component-id process_001 --direction hpc_to_db

# Compare differences for a pipeline
python src/neuroanalyst/scripts/sync_demo.py --component-type pipeline --component-id pipeline_001 --direction compare

# Sync logs from DB to HPC
python src/neuroanalyst/scripts/sync_demo.py --component-type logs --component-id exec_001 --direction db_to_hpc
```

## Testing

A comprehensive test suite is provided to verify the functionality of the sync module:

```bash
# Run all sync tests
python test_sync_module.py

# Run specific test cases
python -m unittest test_sync_module.TestSyncModule.test_process_sync_to_db
```
