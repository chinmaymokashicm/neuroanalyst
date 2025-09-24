# NeuProcessDir Configuration Methods

This document describes the consolidated configuration methods available in the `NeuProcessDir` class for modifying various aspects of the process configuration.

## Environment Variables

Environment variables can be added and removed using the following methods:

```python
# Add environment variables
neu_dir.add_environment_variables("MY_VAR")  # Add a single variable
neu_dir.add_environment_variables(["VAR1", "VAR2"])  # Add multiple variables

# Remove environment variables
neu_dir.remove_environment_variables("MY_VAR")  # Remove a single variable
neu_dir.remove_environment_variables(["VAR1", "VAR2"])  # Remove multiple variables
```

The `remove_environment_variables` method returns a list of variables that were successfully removed.

## Bind Paths

Bind paths can be added and removed using the following methods:

```python
# Add bind paths
neu_dir.add_bind_paths("/path/to/bind")  # Add a single path
neu_dir.add_bind_paths(["/path1", "/path2"])  # Add multiple paths

# Remove bind paths
neu_dir.remove_bind_paths("/path/to/bind")  # Remove a single path
neu_dir.remove_bind_paths(["/path1", "/path2"])  # Remove multiple paths
```

The `remove_bind_paths` method returns a list of paths that were successfully removed.

Notes:
- Paths are automatically normalized (leading slash is added, trailing slash is removed)
- Duplicate paths are automatically filtered out

## Language Packages

Language-specific packages can be added and removed using the following methods:

```python
# Add language packages
neu_dir.add_language_packages("python", "numpy")  # Add a single package
neu_dir.add_language_packages("python", ["pandas", "scipy"])  # Add multiple packages
neu_dir.add_language_packages("R", ["dplyr", "ggplot2"])  # Add packages for a different language

# Remove language packages
neu_dir.remove_language_packages("python", "numpy")  # Remove a single package
neu_dir.remove_language_packages("python", ["pandas", "scipy"])  # Remove multiple packages
```

The `remove_language_packages` method returns a list of packages that were successfully removed.

Notes:
- Language names are case-insensitive (e.g., "python" and "Python" are treated the same)
- Duplicate packages are automatically filtered out

## System Packages

System packages can be added and removed using the following methods:

```python
# Add system packages
neu_dir.add_system_packages("curl")  # Add a single package
neu_dir.add_system_packages(["git", "wget"])  # Add multiple packages

# Remove system packages
neu_dir.remove_system_packages("curl")  # Remove a single package
neu_dir.remove_system_packages(["git", "wget"])  # Remove multiple packages
```

The `remove_system_packages` method returns a list of packages that were successfully removed.

Notes:
- Duplicate packages are automatically filtered out

## Examples

Here are some examples of how to use these methods in practice:

```python
from neuroanalyst.models.process.dir.core import NeuProcessDir
from neuroanalyst.models.process.logic.core import NeuProcessLogic

# Create or load a NeuProcessDir instance
logic = create_sample_logic()  # Your logic creation function
neu_dir = NeuProcessDir.from_logic(logic)

# Configure environment variables
neu_dir.add_environment_variables(["PATH", "LD_LIBRARY_PATH"])

# Configure bind paths
neu_dir.add_bind_paths(["/data", "/workspace", "/output"])

# Configure language packages
neu_dir.add_language_packages("python", ["numpy", "pandas", "scikit-learn"])
neu_dir.add_language_packages("r", ["dplyr", "ggplot2"])

# Configure system packages
neu_dir.add_system_packages(["curl", "git", "wget"])

# Remove some configurations if needed
removed_vars = neu_dir.remove_environment_variables(["OLD_VAR"])
removed_paths = neu_dir.remove_bind_paths(["/old/path"])
removed_packages = neu_dir.remove_language_packages("python", ["deprecated-package"])
removed_sys_packages = neu_dir.remove_system_packages(["obsolete-package"])
```

For a complete working example, see `test_neuprocess_dir_config.py` in the project root.