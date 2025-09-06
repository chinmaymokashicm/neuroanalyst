## Advanced Features

### Bulk Processing

NeuroAnalyst supports dataset-wide processing with the `BULK` processing kind:

```python
bulk_logic = NeuProcessLogic(
    about=About(
        name="dataset_summary",
        description="Generate dataset-wide statistics",
        author="Your Name",
        version="1.0.0"
    ),
    kind=NeuProcessKind.BULK,  # Enable dataset-wide processing
    code='''
import os
from pathlib import Path
from bids import BIDSLayout

def dataset_summary():
    """Generate dataset-wide summary statistics."""
    bids_root = Path(os.environ.get('BIDS_ROOT', '.'))
    layout = BIDSLayout(str(bids_root), validate=False)
    
    subjects = layout.get_subjects()
    sessions = layout.get_sessions()
    
    return {
        "total_subjects": len(subjects),
        "total_sessions": len(sessions) if sessions else 0,
        "total_files": len(layout.get()),
        "t1w_count": len(layout.get(suffix='T1w')),
        "bold_count": len(layout.get(suffix='bold'))
    }
''',
    import_statements=["import os", "from pathlib import Path", "from bids import BIDSLayout"]
)
```

### Parallel Processing

For file-level processing, NeuroAnalyst can automatically parallelize execution:

```python
file_config = NeuProcessDirConfig(
    python_packages=["nibabel", "numpy"],
    parallel_execution=True,  # Enable parallel processing
    max_workers=4             # Limit concurrent processes
)
```

### Custom HPC Resource Configurations

Fine-tune HPC resource allocation for your processing needs:

```python
hpc_script = process_exec.generate_hpc_script(
    job_name="volume_analysis",
    scheduler=HPCScheduler.SLURM,
    partition="compute",
    account="neuro_lab",
    memory="16GB",
    cpu_count=4,
    time_limit="02:00:00",
    queue="normal",
    additional_directives=[
        "#SBATCH --mail-type=ALL",
        "#SBATCH --mail-user=user@example.com"
    ]
)
```

## Contributing

We welcome contributions to NeuroAnalyst! Here's how you can help:

1. **Report bugs** by opening an issue
2. **Request features** through the issue tracker
3. **Submit pull requests** with improvements or bug fixes
4. **Improve documentation** by fixing errors or adding examples
5. **Share your use cases** to help others learn

### Development Setup

```bash
# Clone the repository
git clone https://github.com/chinmaymokashicm/neuroanalyst.git
cd neuroanalyst

# Create a development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies for development
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use NeuroAnalyst in your research, please cite:

```
Mokashi, C. (2023). NeuroAnalyst: A Framework for Standardized Neuroimaging Workflows.
GitHub repository: https://github.com/chinmaymokashicm/neuroanalyst
```
