"""
NeuProcessDir Module

This module defines the NeuProcessDir class, which is responsible for:
1. Generating working directories for NeuProcess instances
2. Creating all necessary files for process execution (scripts, configs, etc.)
3. Supporting both script-based and container-based execution
4. Providing metadata for downstream NeuProcess instances

The NeuProcessDir object serves as a self-contained representation of a neuroimaging
process that can be executed in various environments (local, HPC) and modes
(script, container).
"""

import os
import json
import shutil
import datetime
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, ClassVar
import tempfile
import string
from pydantic import BaseModel, Field, field_validator, model_validator, validator, root_validator

from ....utils.constants import NeuroAnalystPaths
from ....utils.id_generators import generate_process_id
from ...about import About
from ..logic.core import NeuProcessLogic, ProgrammingLanguage, NeuProcessKind
from ..logic.code.python.encoder import PythonEncoder


class ExecutionMode(str, Enum):
    """Enum for execution modes."""
    VENV = "venv"
    CONTAINER = "container"


class NeuProcessDirConfig(BaseModel):
    """Configuration model for NeuProcessDir."""
    
    # Execution-related configuration
    language_packages: Dict[str, List[str]] = Field(default_factory=dict, 
                                                  description="Packages required for execution, by language (e.g., {'python': ['numpy'], 'R': ['dplyr']})")
    system_packages: List[str] = Field(default_factory=list,
                                     description="System packages required for execution")
    parallel_execution: bool = Field(default=True, 
                                   description="Whether to enable parallel execution")
    max_workers: int = Field(default=1, description="Maximum number of parallel workers")
    
    bids_validate: bool = Field(default=True, 
                              description="Whether to validate BIDS data")
    
    # Container-related configuration
    base_image: str = Field(default="python:3.12-slim", 
                          description="Base image for Singularity container")
    bootstrap_method: str = Field(default="docker", 
                                description="Singularity bootstrap method")
    
    # Environment variables
    environment_variables: List[str] = Field(default_factory=list, 
                                           description="Names of environment variables required by the process")
    
    # Bind paths
    bind_paths: List[str] = Field(default_factory=list,
                                description="Internal paths that need to be mounted/aliased at runtime")
    
    # Command flags
    command_flags: List[str] = Field(default_factory=list,
                                   description="Additional command-line flags for the process (e.g., '--verbose', '--fakeroot')")
    
    # Additional configuration
    additional_config: Dict[str, Any] = Field(default_factory=dict, 
                                            description="Additional configuration options")
                                   
    @field_validator('command_flags')
    @classmethod
    def normalize_command_flags(cls, flags):
        """Ensure all command flags are properly formatted."""
        normalized = []
        for flag in flags:
            if not flag.startswith('-'):
                normalized.append(f"--{flag}")
            elif flag.startswith('-') and not flag.startswith('--') and len(flag) > 2:
                normalized.append(f"--{flag[1:]}")
            else:
                normalized.append(flag)
        return normalized
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the NeuProcessDirConfig."""
        languages = ', '.join(self.language_packages.keys()) if self.language_packages else 'none'
        return f"NeuProcessDirConfig(languages=[{languages}], system_packages={len(self.system_packages)}, parallel={self.parallel_execution})"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the NeuProcessDirConfig."""
        return f"NeuProcessDirConfig(language_packages={self.language_packages}, "\
               f"system_packages={self.system_packages}, "\
               f"parallel_execution={self.parallel_execution}, max_workers={self.max_workers})"

class NeuProcessDir(BaseModel):
    """
    NeuProcessDir - Class to generate a self-contained working directory for a NeuProcess.
    
    This class handles:
    1. Directory structure creation
    2. File generation (scripts, configs, etc.)
    3. Support for both script and container execution
    4. Metadata for downstream NeuProcess instances
    """
    # Basic information
    process_id: str = Field(default_factory=generate_process_id, 
                          description="Unique identifier for the process")
    
    # Input sources (mutually exclusive)
    logic: Optional[NeuProcessLogic] = Field(default=None, 
                                           description="NeuProcessLogic used to generate the directory")
    script_paths: Optional[Dict[str, Any]] = Field(default=None, 
                                                  description="Paths to custom scripts")
    
    # Configuration
    config: NeuProcessDirConfig = Field(default_factory=NeuProcessDirConfig, 
                                      description="Configuration for the process directory")
    
    # Working directory information
    working_dir: Optional[Path] = Field(default=None, 
                                      description="Path to the working directory")
    
    # Class variables
    _paths: ClassVar[NeuroAnalystPaths] = NeuroAnalystPaths()
    _template_dir: ClassVar[Path] = Path(__file__).parent / "templates"
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the NeuProcessDir."""
        return f"NeuProcessDir(name='{self.name}', id='{self.process_id}')"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the NeuProcessDir."""
        modes = self.get_available_execution_modes() if hasattr(self, 'get_available_execution_modes') else None
        return f"NeuProcessDir(name='{self.name}', id='{self.process_id}', "\
               f"path='{self.process_dir if hasattr(self, 'process_dir') else None}', "\
               f"modes={modes})"
    
    # Configuration modification methods
    def add_environment_variables(self, variables: Union[str, List[str]]) -> None:
        """
        Add environment variables to the configuration.
        
        Args:
            variables: A single environment variable name or list of names to add
        """
        # Convert single string to list for consistent handling
        var_list = [variables] if isinstance(variables, str) else variables
        
        for variable in var_list:
            if variable not in self.config.environment_variables:
                self.config.environment_variables.append(variable)
    
    def remove_environment_variables(self, variables: Union[str, List[str]]) -> List[str]:
        """
        Remove environment variables from the configuration.
        
        Args:
            variables: A single environment variable name or list of names to remove
            
        Returns:
            List of variables that were successfully removed
        """
        # Convert single string to list for consistent handling
        var_list = [variables] if isinstance(variables, str) else variables
        
        removed = []
        for variable in var_list:
            if variable in self.config.environment_variables:
                self.config.environment_variables.remove(variable)
                removed.append(variable)
        
        return removed
    
    def add_bind_paths(self, paths: Union[str, List[str]]) -> None:
        """
        Add bind paths to the configuration.
        
        Args:
            paths: A single bind path or list of paths to add
        """
        # Convert single string to list for consistent handling
        path_list = [paths] if isinstance(paths, str) else paths
        
        for path in path_list:
            # Normalize path to ensure consistent handling
            norm_path = path if path.startswith('/') else f"/{path}"
            # Strip trailing slash if present for consistency
            norm_path = norm_path.rstrip('/')
            
            if norm_path not in self.config.bind_paths:
                self.config.bind_paths.append(norm_path)
    
    def remove_bind_paths(self, paths: Union[str, List[str]]) -> List[str]:
        """
        Remove bind paths from the configuration.
        
        Args:
            paths: A single bind path or list of paths to remove
            
        Returns:
            List of paths that were successfully removed
        """
        # Convert single string to list for consistent handling
        path_list = [paths] if isinstance(paths, str) else paths
        
        removed = []
        for path in path_list:
            # Normalize path to ensure consistent handling
            norm_path = path if path.startswith('/') else f"/{path}"
            # Strip trailing slash if present for consistency
            norm_path = norm_path.rstrip('/')
            
            if norm_path in self.config.bind_paths:
                self.config.bind_paths.remove(norm_path)
                removed.append(norm_path)
        
        return removed
    
    def add_language_packages(self, language: str, packages: Union[str, List[str]]) -> None:
        """
        Add packages for a specific language to the configuration.
        
        Args:
            language: The programming language (e.g., 'python', 'R')
            packages: A single package name or list of package names to add
        """
        language = language.lower()
        
        # Initialize the language entry if it doesn't exist
        if language not in self.config.language_packages:
            self.config.language_packages[language] = []
        
        # Convert single string to list for consistent handling
        pkg_list = [packages] if isinstance(packages, str) else packages
            
        # Add packages if they're not already in the list
        for package in pkg_list:
            if package not in self.config.language_packages[language]:
                self.config.language_packages[language].append(package)
    
    def remove_language_packages(self, language: str, packages: Union[str, List[str]]) -> List[str]:
        """
        Remove packages for a specific language from the configuration.
        
        Args:
            language: The programming language (e.g., 'python', 'R')
            packages: A single package name or list of package names to remove
            
        Returns:
            List of packages that were successfully removed
        """
        language = language.lower()
        
        # Convert single string to list for consistent handling
        pkg_list = [packages] if isinstance(packages, str) else packages
        
        removed = []
        if language in self.config.language_packages:
            for package in pkg_list:
                if package in self.config.language_packages[language]:
                    self.config.language_packages[language].remove(package)
                    removed.append(package)
        
        return removed
    
    def add_system_packages(self, packages: Union[str, List[str]]) -> None:
        """
        Add system packages to the configuration.
        
        Args:
            packages: A single system package name or list of package names to add
        """
        # Convert single string to list for consistent handling
        pkg_list = [packages] if isinstance(packages, str) else packages
        
        for package in pkg_list:
            if package not in self.config.system_packages:
                self.config.system_packages.append(package)
    
    def remove_system_packages(self, packages: Union[str, List[str]]) -> List[str]:
        """
        Remove system packages from the configuration.
        
        Args:
            packages: A single system package name or list of package names to remove
            
        Returns:
            List of packages that were successfully removed
        """
        # Convert single string to list for consistent handling
        pkg_list = [packages] if isinstance(packages, str) else packages
        
        removed = []
        for package in pkg_list:
            if package in self.config.system_packages:
                self.config.system_packages.remove(package)
                removed.append(package)
        
        return removed
    
    def add_command_flags(self, flags: Union[str, List[str]]) -> None:
        """
        Add command-line flags to the configuration.
        
        Args:
            flags: A single command flag or list of command flags to add
            
        Note:
            Each flag will be prefixed with '--' if it doesn't already start with '-'
        """
        # Convert single string to list for consistent handling
        flag_list = [flags] if isinstance(flags, str) else flags
        
        for flag in flag_list:
            # Ensure each flag starts with '--' or '-'
            if not flag.startswith('-'):
                flag = f"--{flag}"
            elif flag.startswith('-') and not flag.startswith('--') and len(flag) > 2:
                # Convert single dash to double dash for long options (more than one character)
                flag = f"--{flag[1:]}"
            
            # Add flag if it's not already in the list
            if flag not in self.config.command_flags:
                self.config.command_flags.append(flag)
    
    def remove_command_flags(self, flags: Union[str, List[str]]) -> List[str]:
        """
        Remove command-line flags from the configuration.
        
        Args:
            flags: A single command flag or list of command flags to remove
            
        Returns:
            List of flags that were successfully removed
            
        Note:
            The method will try to match flags regardless of '--' prefix
        """
        # Convert single string to list for consistent handling
        flag_list = [flags] if isinstance(flags, str) else flags
        
        removed = []
        for flag in flag_list:
            # Try to match with and without dash prefixes
            normalized_flag = flag.lstrip('-')
            for existing_flag in self.config.command_flags[:]:  # Create a copy to safely modify during iteration
                existing_normalized = existing_flag.lstrip('-')
                if normalized_flag == existing_normalized:
                    self.config.command_flags.remove(existing_flag)
                    removed.append(existing_flag)
                    break
        
        return removed
    
    # Helper methods to format output
    def _format_language_packages_for_readme(self) -> str:
        """Format language packages information for the README file."""
        if not self.config.language_packages:
            return "No specific language packages required."
            
        sections = []
        for language, packages in self.config.language_packages.items():
            if packages:
                package_list = "\n".join([f"- {pkg}" for pkg in packages])
                sections.append(f"### {language.capitalize()} Packages\n{package_list}")
        
        return "\n\n".join(sections) if sections else "No specific language packages required."
        
    def _format_system_packages_for_readme(self) -> str:
        """Format system packages information for the README file."""
        if not self.config.system_packages:
            return "No specific system packages required."
            
        package_list = "\n".join([f"- {pkg}" for pkg in self.config.system_packages])
        return f"The following system packages are required:\n{package_list}"
    
    def _format_environment_variables_for_readme(self) -> str:
        """Format environment variables information for the README file."""
        if not self.config.environment_variables:
            return "No specific environment variables required."
            
        env_lines = ["The following environment variables need to be set before running this process:"]
        for env_var in self.config.environment_variables:
            env_lines.append(f"- `{env_var}`: Required for process execution")
        env_lines.append("\nUse the `--env {VAR}={value}` format in execution commands to set these variables.")
        
        return "\n".join(env_lines)
    
    def _format_bind_paths_for_readme(self) -> str:
        """Format bind paths information for the README file."""
        if not self.config.bind_paths:
            return "No specific path bindings required."
            
        bind_lines = ["The following internal paths need to be mounted/aliased at runtime:"]
        for bind_path in self.config.bind_paths:
            norm_path = bind_path if bind_path.startswith('/') else f"/{bind_path}"
            norm_path = norm_path.rstrip('/')
            bind_lines.append(f"- `{norm_path}`: Internal path that needs to be mapped to an external path")
        bind_lines.append("\nUse the `--bind {path}={target}` format in execution commands to set these path bindings.")
        
        return "\n".join(bind_lines)
    
    def _load_template(self, template_name: str) -> string.Template:
        """Load a template file and return a string.Template object."""
        template_file = self._template_dir / template_name
        with open(template_file, "r") as f:
            template_content = f.read()
        return string.Template(template_content)
    
    # Derived properties
    @property
    def process_name(self) -> str:
        """Get the process name."""
        if self.logic and self.logic.about:
            return self.logic.about.name
        if self.script_paths and self.script_paths.get("metadata"):
            # Read metadata from file
            try:
                with open(self.script_paths["metadata"], "r") as f:
                    metadata = json.load(f)
                return metadata.get("name", self.process_id)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return self.process_id
    
    @property
    def description(self) -> str:
        """Get the process description."""
        if self.logic and self.logic.about:
            return self.logic.about.description
        return f"Process {self.process_id}"
    
    @property
    def version(self) -> str:
        """Get the process version."""
        if self.logic and self.logic.about:
            return self.logic.about.version
        return "1.0.0"
    
    @property
    def author(self) -> str:
        """Get the author of the process."""
        if self.logic and self.logic.about:
            return self.logic.about.author
        return "NeuroAnalyst User"
    
    @property
    def language(self) -> str:
        """Get the programming language of the process."""
        if self.logic:
            return self.logic.language.value
        if self.script_paths and self.script_paths.get("main"):
            suffix = self.script_paths["main"].suffix.lower()
            if suffix == ".py":
                return ProgrammingLanguage.PYTHON.value
            # Add more language detection as needed
        return ProgrammingLanguage.PYTHON.value  # Default to Python
    
    # Model validators
    @field_validator('script_paths')
    def convert_script_paths(cls, v, info):
        """Convert string paths to Path objects in script_paths."""
        if v is None:
            return v
            
        # If it's a dictionary with string paths, convert them to Path objects
        result = {}
        for key, path in v.items():
            if isinstance(path, str):
                result[key] = Path(path)
            else:
                result[key] = path
        return result
    
    # @model_validator(mode="before")
    # def check_input_sources(cls, values):
    #     """Validate that exactly one input source is provided."""
    #     logic = values.get('logic')
    #     script_paths = values.get('script_paths')
        
    #     if logic is None and script_paths is None:
    #         raise ValueError("Either 'logic' or 'script_paths' must be provided")
        
    #     if logic is not None and script_paths is not None:
    #         raise ValueError("Only one of 'logic' or 'script_paths' can be provided")
            
    #     return values
    
    # Class methods for creation
    @classmethod
    def from_logic(cls, logic: NeuProcessLogic, config: Optional[NeuProcessDirConfig] = None) -> 'NeuProcessDir':
        """
        Create a NeuProcessDir from a NeuProcessLogic instance.
        
        Args:
            logic: The NeuProcessLogic instance
            config: Optional configuration for the directory
            
        Returns:
            A new NeuProcessDir instance
        """
        if config is None:
            config = NeuProcessDirConfig()
        
        # Set mandatory binds for all logic kinds
        # mandatory_binds: List[str] = ["/data", "/usr/bin/apptainer", "/usr/bin/singularity", "/etc/apptainer"]
        mandatory_binds: List[str] = ["/data"]
        new_binds: List[str] = list(set(mandatory_binds + config.bind_paths))
        
        new_envs: List[str] = config.environment_variables.copy()
        mandatory_envs: List[str] = ["PROCESS_ID", "PIPELINE_ID", "PIPELINE_NAME", "PROCESS_EXEC_ID"]
        if logic.kind == NeuProcessKind.FILE:
            # Include the mandatory envs to set for file-based processing. 
            mandatory_envs += ["BIDS_FILTERS"]
            
            # Check if input_filepath is the only argument and not optional
            if not any(arg.name == "input_filepath" and not arg.is_optional for arg in logic.arguments):
                raise ValueError("For file-based processing, 'input_filepath' argument must be defined and not optional.")
            
        new_envs: List[str] = list(set(mandatory_envs + new_envs))
            
        config: NeuProcessDirConfig = config.model_copy(update={"bind_paths": new_binds, "environment_variables": new_envs})
        
        return cls(logic=logic, config=config)
    
    @classmethod
    def from_scripts(cls, 
                    main_script: Path,
                    install_script: Optional[Path] = None,
                    metadata: Optional[Path] = None,
                    additional_scripts: Optional[Dict[str, Path]] = None,
                    config: Optional[NeuProcessDirConfig] = None) -> 'NeuProcessDir':
        """
        Create a NeuProcessDir from custom scripts.
        
        Args:
            main_script: Path to the main execution script
            install_script: Path to the installation script (optional)
            metadata: Path to metadata JSON file (optional)
            additional_scripts: Dictionary of additional scripts (optional)
            config: Optional configuration for the directory
            
        Returns:
            A new NeuProcessDir instance
        """
        script_paths = {"main": main_script}
        
        if install_script:
            script_paths["install"] = install_script
            
        if metadata:
            script_paths["metadata"] = metadata
            
        if additional_scripts:
            script_paths.update(additional_scripts)
            
        if config is None:
            config = NeuProcessDirConfig()
            
        return cls(script_paths=script_paths, config=config)
    
    # Generation methods
    def generate(self, target_dir: Optional[Path] = None) -> Path:
        """
        Generate the working directory structure.
        
        Args:
            target_dir: Target directory to create the process directory in.
                      If None, uses the default workdir from NeuroAnalystPaths.
                      
        Returns:
            Path to the generated working directory
        """
        # Determine target directory
        if target_dir is None:
            target_dir = self._paths.workdir
            
        # Create process-specific working directory
        process_dir = target_dir / self.process_id
        process_dir.mkdir(parents=True, exist_ok=True)
        self.working_dir = process_dir
        
        # Generate files based on source type
        if self.logic:
            self._generate_from_logic(process_dir)
        elif self.script_paths:
            self._generate_from_scripts(process_dir)
            
        # Initialize script_paths dictionary if it doesn't exist
        if self.script_paths is None:
            self.script_paths = {}
            
        # Populate script_paths with all generated scripts
        self._populate_script_paths(process_dir)
            
        # Save model JSON for reproducibility
        self._save_model_json(process_dir)
        
        return process_dir
    
    def _generate_from_logic(self, process_dir: Path) -> None:
        """
        Generate directory structure from NeuProcessLogic.
        
        Args:
            process_dir: Target directory to create files in
        """
        assert self.logic is not None, "Logic must be provided"
        
        # Create basic structure
        self._create_directories(process_dir)
        
        # Generate common files
        self._generate_config_json(process_dir)
        self._generate_install_requirements(process_dir)
        
        # Generate main script based on language
        if self.logic.language == ProgrammingLanguage.PYTHON:
            self._generate_python_main(process_dir)
        # Add support for other languages as needed
        
        # Generate Singularity definition file
        self._generate_singularity_def(process_dir)
        
        # Generate build scripts
        self._generate_build_scripts(process_dir)
        
        # Generate execution scripts
        self._generate_execution_scripts(process_dir)
        
        self._generate_readme(process_dir)
    
    def _generate_from_scripts(self, process_dir: Path) -> None:
        """
        Generate directory structure from custom scripts.
        
        Args:
            process_dir: Target directory to create files in
        """
        assert self.script_paths is not None, "Script paths must be provided"
        
        # Create basic structure
        self._create_directories(process_dir)
        
        # Copy provided scripts
        for name, path in self.script_paths.items():
            if name == "main":
                shutil.copy(path, process_dir / f"main{path.suffix}")
            elif name == "install":
                shutil.copy(path, process_dir / "install_requirements.sh")
            else:
                shutil.copy(path, process_dir / path.name)
        
        # Generate common files
        self._generate_readme(process_dir)
        self._generate_config_json(process_dir)
        
        # Generate any missing required files
        if "install" not in self.script_paths:
            self._generate_install_requirements(process_dir)
        
        # Generate Singularity definition file
        self._generate_singularity_def(process_dir)
        
        # Generate build scripts
        self._generate_build_scripts(process_dir)
        
        # Generate execution scripts
        self._generate_execution_scripts(process_dir)
    
    # Helper methods for generation
    def _create_directories(self, process_dir: Path) -> None:
        """Create the directory structure."""
        # Create execute subdirectories - only local scripts
        (process_dir / "execute").mkdir(parents=True, exist_ok=True)
        
        # Create build subdirectories
        (process_dir / "build").mkdir(parents=True, exist_ok=True)
    
    def _generate_readme(self, process_dir: Path) -> None:
        """Generate the README.md file."""
        template = self._load_template("README.md.template")
        
        # Create example values for environment variables and bind paths
        example_env_values = {}
        if self.config.environment_variables:
            for var in self.config.environment_variables:
                example_env_values[var] = f"value_for_{var.lower()}"
                
        example_bind_values = {}
        if self.config.bind_paths:
            for path in self.config.bind_paths:
                # Normalize path to ensure consistent handling
                norm_path = path if path.startswith('/') else f"/{path}"
                # Strip trailing slash if present for consistency
                norm_path = norm_path.rstrip('/')
                # Create example path based on normalized path
                example_bind_values[norm_path] = f"/external/path/to{norm_path}"
        
        # Try to generate example execution commands, but if they fail, create manual examples
        try:
            local_container_cmd = self.generate_example_execution_command(
                "container", "local", example_env_values, example_bind_values)
            local_venv_cmd = self.generate_example_execution_command(
                "script", "local", example_env_values, example_bind_values)
            slurm_container_cmd = self.generate_example_execution_command(
                "container", "slurm", example_env_values, example_bind_values)
            slurm_venv_cmd = self.generate_example_execution_command(
                "script", "slurm", example_env_values, example_bind_values)
            pbs_container_cmd = self.generate_example_execution_command(
                "container", "pbs", example_env_values, example_bind_values)
            pbs_venv_cmd = self.generate_example_execution_command(
                "script", "pbs", example_env_values, example_bind_values)
            lsf_container_cmd = self.generate_example_execution_command(
                "container", "lsf", example_env_values, example_bind_values)
            lsf_venv_cmd = self.generate_example_execution_command(
                "script", "lsf", example_env_values, example_bind_values)
        except (ValueError, FileNotFoundError) as e:
            # If script generation fails, create manual examples
            print(f"Warning: Could not generate example commands: {e}")
            
            # Create example env and bind path strings
            env_args = " ".join(f"--env {var}={example_env_values.get(var, f'<{var.lower()}_value>')}" 
                              for var in self.config.environment_variables)
            
            bind_args = ""
            for path in self.config.bind_paths:
                norm_path = path if path.startswith('/') else f"/{path}"
                norm_path = norm_path.rstrip('/')
                bind_value = example_bind_values.get(norm_path, f"<path_to{norm_path}>")
                bind_args += f" --bind {norm_path}={bind_value}"
            
            # Create manual example commands
            local_container_cmd = f"./execute/run_container.sh {env_args}{bind_args}"
            local_venv_cmd = f"./execute/run_venv.sh {env_args}{bind_args}"
            slurm_container_cmd = f"sbatch ./execute/hpc/slurm/run_container.sh {env_args}{bind_args}"
            slurm_venv_cmd = f"sbatch ./execute/hpc/slurm/run_venv.sh {env_args}{bind_args}"
            pbs_container_cmd = f"qsub ./execute/hpc/pbs/run_container.sh {env_args}{bind_args}"
            pbs_venv_cmd = f"qsub ./execute/hpc/pbs/run_venv.sh {env_args}{bind_args}"
            lsf_container_cmd = f"bsub ./execute/hpc/lsf/run_container.sh {env_args}{bind_args}"
            lsf_venv_cmd = f"bsub ./execute/hpc/lsf/run_venv.sh {env_args}{bind_args}"
            
        # Handle cases where some scripts might not exist
        local_container_example = f"```bash\n{local_container_cmd}\n```" if local_container_cmd else "Not available"
        local_venv_example = f"```bash\n{local_venv_cmd}\n```" if local_venv_cmd else "Not available"
        slurm_container_example = f"```bash\n{slurm_container_cmd}\n```" if slurm_container_cmd else "Not available"
        slurm_venv_example = f"```bash\n{slurm_venv_cmd}\n```" if slurm_venv_cmd else "Not available"
        pbs_container_example = f"```bash\n{pbs_container_cmd}\n```" if pbs_container_cmd else "Not available"
        pbs_venv_example = f"```bash\n{pbs_venv_cmd}\n```" if pbs_venv_cmd else "Not available"
        lsf_container_example = f"```bash\n{lsf_container_cmd}\n```" if lsf_container_cmd else "Not available"
        lsf_venv_example = f"```bash\n{lsf_venv_cmd}\n```" if lsf_venv_cmd else "Not available"
        
        # Prepare context for template
        context = {
            "process_id": self.process_id,
            "process_name": self.process_name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "creation_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "language_packages_info": self._format_language_packages_for_readme(),
            "system_packages": self._format_system_packages_for_readme(),
            "environment_variables_info": self._format_environment_variables_for_readme(),
            "bind_paths_info": self._format_bind_paths_for_readme(),
            "venv_path": str(self._paths.get_venv_path(self.process_id)),
            "image_path": str(self._paths.get_process_image_path(self.process_id)),
            "output_description": "Output files specific to the process",
            "additional_info": "This process was generated by NeuroAnalyst.",
            "arguments": "",
            "local_container_example": local_container_example,
            "local_venv_example": local_venv_example,
            "slurm_container_example": slurm_container_example,
            "slurm_venv_example": slurm_venv_example,
            "pbs_container_example": pbs_container_example,
            "pbs_venv_example": pbs_venv_example,
            "lsf_container_example": lsf_container_example,
            "lsf_venv_example": lsf_venv_example
        }
        
        # Add arguments if available from logic
        if self.logic and self.logic.arguments:
            arg_lines = []
            for arg in self.logic.arguments:
                required = " (Required)" if not arg.is_optional else ""
                arg_lines.append(f"- `--{arg.name}`: {arg.description}{required}")
            context["arguments"] = "\n".join(arg_lines)
        
        # Render template and write to file
        readme_content = template.safe_substitute(context)
        readme_path = process_dir / "README.md"
        with open(readme_path, "w") as f:
            f.write(readme_content)
    
    def _generate_config_json(self, process_dir: Path) -> None:
        """Generate the config.json file."""
        template = self._load_template("config.json.template")
        
        # Import json for proper serialization
        import json
        
        # Create context for template substitution
        context = {
            "process_id": self.process_id,
            "process_name": self.process_name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "creation_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "language": self.language,
            "language_packages": json.dumps(self.config.language_packages, indent=2),
            "system_packages": json.dumps(self.config.system_packages, indent=2),
            "parallel_execution": json.dumps(self.config.parallel_execution).lower(),
            "environment_variables": json.dumps(self.config.environment_variables, indent=2),
            "bind_paths": json.dumps(self.config.bind_paths, indent=2),
            "max_workers": str(self.config.max_workers),
            "bids_validate": json.dumps(self.config.bids_validate).lower()
        }
        
        # Render template and write to file
        config_content = template.safe_substitute(context)
        config_path = process_dir / "config.json"
        with open(config_path, "w") as f:
            f.write(config_content)
    
    def _generate_install_requirements(self, process_dir: Path) -> None:
        """Generate the install_requirements.sh script."""
        template = self._load_template("install_requirements.sh.template")
        
        # System packages section
        system_packages_section = ""
        if self.config.system_packages:
            system_packages_section = "echo \"Installing system packages...\"\n"
            system_packages_section += "apt-get update -y\n"
            system_packages_section += f"apt-get install -y {' '.join(self.config.system_packages)}"
        
        # Language-specific packages section
        language_packages_section = ""
        for language, packages in self.config.language_packages.items():
            if not packages:
                continue
                
            if language.lower() == "python":
                language_packages_section += f"echo \"Checking and installing Python packages...\"\n"
                for pkg in packages:
                    # Extract base package name (handle package==version or package>=version formats)
                    base_pkg = pkg.split('==')[0].split('>=')[0].split('<')[0].strip()
                    language_packages_section += f"pip_check_install {base_pkg}\n"
                language_packages_section += "\n"
            elif language.lower() == "r":
                language_packages_section += f"echo \"Checking and installing R packages...\"\n"
                # Add a helper function for R packages at the top of the section
                language_packages_section += "# Helper function for R packages\n"
                language_packages_section += "r_check_install() {\n"
                language_packages_section += "    pkg=$1\n"
                language_packages_section += "    Rscript -e \"if(!require($pkg, quietly=TRUE)) { install.packages('$pkg', repos='https://cran.rstudio.com/') }\"\n"
                language_packages_section += "}\n\n"
                
                for pkg in packages:
                    language_packages_section += f"r_check_install {pkg}\n"
                language_packages_section += "\n"
            elif language.lower() == "julia":
                language_packages_section += f"echo \"Checking and installing Julia packages...\"\n"
                # Add a helper function for Julia packages at the top of the section
                language_packages_section += "# Helper function for Julia packages\n"
                language_packages_section += "julia_check_install() {\n"
                language_packages_section += "    pkg=$1\n"
                language_packages_section += "    julia -e \"using Pkg; if !haskey(Pkg.project().dependencies, \\\"$pkg\\\") Pkg.add(\\\"$pkg\\\") end\"\n"
                language_packages_section += "}\n\n"
                
                for pkg in packages:
                    language_packages_section += f"julia_check_install {pkg}\n"
                language_packages_section += "\n"
            else:
                language_packages_section += f"echo \"Warning: Package installation for {language} not supported yet.\"\n\n"
        
        # Prepare context for template
        context = {
            "process_id": self.process_id,
            "process_name": self.process_name,
            "version": self.version,
            "author": self.author,
            "creation_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "system_packages_section": system_packages_section,
            "language_packages_section": language_packages_section.strip(),
            "other_installation_steps": ""
        }
        
        # Render template and write to file
        install_content = template.safe_substitute(context)
        install_path = process_dir / "install_requirements.sh"
        with open(install_path, "w") as f:
            f.write(install_content)
        
        # Make the script executable
        os.chmod(install_path, 0o755)
    
    def _generate_python_main(self, process_dir: Path) -> None:
        """Generate the main.py, udf.py, and wrapper.py scripts for Python processes."""
        assert self.logic is not None, "Logic must be provided"
        
        # Determine processing kind (file or bulk)
        kind = self.logic.kind.value if self.logic.kind else "bulk"
        
        # Load templates
        main_template = self._load_template("main.py.template")
        udf_template = self._load_template("udf.py.template")  # Using updated template without wrapper
        wrapper_template = self._load_template("wrapper.py.template")
        
        # Generate arguments for parser
        arg_parser_lines = []
        for arg in self.logic.arguments:
            required = "required=True, " if not arg.is_optional else ""
            arg_parser_lines.append(f"    parser.add_argument('--{arg.name}', {required}help='{arg.description}')")
        
        
        # Prepare context for templates
        context = {
            "process_id": self.process_id,
            "process_name": self.process_name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "creation_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "import_statements": "\n".join(self.logic.import_statements),
            "func_name": self.logic.about.name,
            "func_args": ", ".join([arg.name for arg in self.logic.arguments]),
            "udf_code": self.logic.code,
            # For wrapper.py, use PythonEncoder
            "func": PythonEncoder().encode(self.logic).code,
            "arg_parser_section": "\n".join(arg_parser_lines),
            "func_args_section": "\n".join([f"        '{arg.name}': args.{arg.name}," for arg in self.logic.arguments]),
            "kind": kind,
            "max_workers": self.config.max_workers if self.config.parallel_execution else 1
        }
        
        # Render templates and write to files
        
        # Generate main.py
        main_content = main_template.safe_substitute(context)
        main_path = process_dir / "main.py"
        with open(main_path, "w") as f:
            f.write(main_content)
        
        # Generate udf.py
        udf_content = udf_template.safe_substitute(context)
        udf_path = process_dir / "udf.py"
        with open(udf_path, "w") as f:
            f.write(udf_content)
        
        # Generate wrapper.py
        wrapper_content = wrapper_template.safe_substitute(context)
        wrapper_path = process_dir / "wrapper.py"
        with open(wrapper_path, "w") as f:
            f.write(wrapper_content)
        
        # Make the scripts executable
        os.chmod(main_path, 0o755)
        os.chmod(udf_path, 0o755)
        os.chmod(wrapper_path, 0o755)
    
    def _generate_singularity_def(self, process_dir: Path) -> None:
        """Generate the Singularity definition file."""
        template = self._load_template("singularity.def.template")
        
        # Create a comment with required environment variables
        env_vars_comment = "No specific environment variables required."
        if self.config.environment_variables:
            env_vars_comment = "\n    # ".join(f"{var}" for var in self.config.environment_variables)
        
        # Create environment variables export statements
        env_vars_export = ""
        if self.config.environment_variables:
            env_vars_export = "\n    ".join(f"export {var}=${{{var}}}" for var in self.config.environment_variables)
        
        # Create a comment with required bind paths
        bind_paths_comment = "No specific bind paths required."
        if self.config.bind_paths:
            bind_paths_comment = "\n    ".join(f"{path}" for path in self.config.bind_paths)
        
        # Generate example usage command
        try:
            usage_command = self.generate_singularity_execution_command()
        except Exception as e:
            # Fall back to a simple example if the command generation fails
            usage_command = f"singularity run {self.process_id}.sif [arguments]"
        
        # Prepare extra files section
        extra_files = ""
        
        # Prepare context for template
        context = {
            "process_id": self.process_id,
            "process_name": self.process_name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "creation_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "bootstrap_method": self.config.bootstrap_method,
            "base_image": self.config.base_image,
            "environment_variables_comment": env_vars_comment,
            "environment_variables_export": env_vars_export,
            "bind_paths_comment": bind_paths_comment,
            "extra_files": extra_files,
            "usage_command": usage_command
        }
        
        # Render template and write to file
        def_content = template.safe_substitute(context)
        def_path = process_dir / f"{self.process_id}.def"
        with open(def_path, "w") as f:
            f.write(def_content)
            
        # Make the definition file executable
        os.chmod(def_path, 0o755)
    
    def _generate_build_scripts(self, process_dir: Path) -> None:
        """Generate build scripts for creating container images and virtual environments."""
        # Create build directory if it doesn't exist
        build_dir = process_dir / "build"
        build_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate script to build Singularity image
        self._generate_image_build_script(build_dir)
        
        # Generate script to create virtual environment
        self._generate_venv_build_script(build_dir)
    
    def _generate_image_build_script(self, build_dir: Path) -> None:
        """Generate script to build the Singularity image."""
        image_build_content = f"""#!/bin/bash
# image.sh - Script to build Singularity image for {self.process_id} - {self.process_name}
#
# This script builds a Singularity image from the definition file
# and stores it in the NeuroAnalyst images directory.
#
# Version: {self.version}
# Created: {datetime.datetime.now().strftime("%Y-%m-%d")}
# Author: {self.author}

set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
PARENT_DIR="$( dirname "$SCRIPT_DIR" )"

# Set paths
PROCESS_ID="{self.process_id}"
DEF_FILE="${{PARENT_DIR}}/${{PROCESS_ID}}.def"
IMAGE_PATH="{self._paths.get_process_image_path(self.process_id)}"

echo "Building Singularity image for ${{PROCESS_ID}}..."
echo "Definition file: ${{DEF_FILE}}"
echo "Target image path: ${{IMAGE_PATH}}"

# Create the images directory if it doesn't exist
mkdir -p "$(dirname "${{IMAGE_PATH}}")"

# Build the image
singularity build "${{IMAGE_PATH}}" "${{DEF_FILE}}"

echo "Singularity image built successfully at: ${{IMAGE_PATH}}"
"""
        
        # Write to file
        image_build_path = build_dir / "image.sh"
        with open(image_build_path, "w") as f:
            f.write(image_build_content)
        
        # Make the script executable
        os.chmod(image_build_path, 0o755)
    
    def _generate_venv_build_script(self, build_dir: Path) -> None:
        """Generate script to create and set up a virtual environment."""
        venv_build_content = f"""#!/bin/bash
# venv.sh - Script to create virtual environment for {self.process_id} - {self.process_name}
#
# This script creates a virtual environment in the NeuroAnalyst venvs directory
# and installs all required dependencies.
#
# Version: {self.version}
# Created: {datetime.datetime.now().strftime("%Y-%m-%d")}
# Author: {self.author}

set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
PARENT_DIR="$( dirname "$SCRIPT_DIR" )"

# Set paths
PROCESS_ID="{self.process_id}"
VENV_PATH="{self._paths.get_venv_path(self.process_id)}"
INSTALL_SCRIPT="${{PARENT_DIR}}/install_requirements.sh"

echo "Creating virtual environment for ${{PROCESS_ID}}..."
echo "Virtual environment path: ${{VENV_PATH}}"

# Create the venvs directory if it doesn't exist
mkdir -p "$(dirname "${{VENV_PATH}}")"

# Create the virtual environment if it doesn't exist
if [ ! -d "${{VENV_PATH}}" ]; then
    echo "Creating new virtual environment..."
    python -m venv "${{VENV_PATH}}"
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
source "${{VENV_PATH}}/bin/activate"

# Install requirements
echo "Installing requirements..."
bash "${{INSTALL_SCRIPT}}"

echo "Virtual environment created and requirements installed successfully at: ${{VENV_PATH}}"
"""
        
        # Write to file
        venv_build_path = build_dir / "venv.sh"
        with open(venv_build_path, "w") as f:
            f.write(venv_build_content)
        
        # Make the script executable
        os.chmod(venv_build_path, 0o755)
    
    def _generate_execution_scripts(self, process_dir: Path) -> None:
        """Generate execution scripts for different environments."""
        # Local execution scripts only - HPC scripts removed
        self._generate_local_execution_scripts(process_dir)
    
    def _generate_local_execution_scripts(self, process_dir: Path) -> None:
        """Generate local execution scripts."""
        from .script_builder import assemble_script
        components_dir = self._template_dir / "components"
        
        # Prepare environment variables comment
        env_vars_comment = "No specific environment variables required."
        if self.config.environment_variables:
            env_vars_comment = "\n".join(f"# {var}" for var in self.config.environment_variables)
            
        # Prepare bind paths comment
        bind_paths_comment = "No specific bind paths required."
        if self.config.bind_paths:
            bind_paths_comment = "\n".join(f"# {path} -> /external/path (to be specified)" for path in self.config.bind_paths)
        
        # Prepare environment variables export
        env_vars_export = "# No environment variables to export"
        if self.config.environment_variables:
            env_vars_export = "\n".join([f"export {var}=\"${{{var}:-}}\"" for var in self.config.environment_variables])
        
        # Generate singularity command with runtime variables
        try:
            singularity_command = self.generate_singularity_execution_command(use_runtime_vars=True)
        except Exception as e:
            singularity_command = "echo \"Error generating Singularity command: $e\" && exit 1"
        
        # Prepare bind options for container (for backward compatibility)
        bind_options = ""
        if self.config.bind_paths:
            bind_opts = []
            for path in self.config.bind_paths:
                # Normalize path to ensure consistent handling
                norm_path = path if path.startswith('/') else f"/{path}"
                # Strip trailing slash if present for consistency
                norm_path = norm_path.rstrip('/')
                # Use standard format for external path mapping
                bind_opts.append(f"--bind \"${{PROCESS_DIR}}{norm_path}:$NEUROANALYST_DATA_DIR{norm_path}\"")
            if bind_opts:
                bind_options = " ".join(bind_opts)
        
        # Prepare symbolic links setup for venv
        symbolic_links_setup = "# No symbolic links to set up"
        symbolic_links_cleanup = "# No symbolic links to clean up"
        if self.config.bind_paths:
            symlink_setup_lines = []
            symlink_cleanup_lines = []
            for path in self.config.bind_paths:
                # Normalize path to ensure consistent handling
                norm_path = path if path.startswith('/') else f"/{path}"
                # Strip trailing slash if present for consistency
                norm_path = norm_path.rstrip('/')
                
                # Check if this path is already handled by a custom bind path
                symlink_setup_lines.append(f"if [[ -z \"${{ALREADY_BOUND[{norm_path}]:-}}\" ]]; then")
                symlink_setup_lines.append(f"    # Set default bind path if available from environment")
                symlink_setup_lines.append(f"    BIND_PATH=\"$NEUROANALYST_DATA_DIR{norm_path}\"")
                symlink_setup_lines.append(f"    # Create directory structure if needed")
                symlink_setup_lines.append(f"    mkdir -p \"${{PROCESS_DIR}}{os.path.dirname(norm_path)}\"")
                symlink_setup_lines.append(f"    # Create symbolic link")
                symlink_setup_lines.append(f"    ln -sf \"$BIND_PATH\" \"${{PROCESS_DIR}}{norm_path}\"")
                symlink_setup_lines.append(f"    echo \"Created predefined symlink: $BIND_PATH -> ${{PROCESS_DIR}}{norm_path}\"")
                symlink_setup_lines.append("fi")
                
                symlink_cleanup_lines.append(f"# Remove symlink if it exists")
                symlink_cleanup_lines.append(f"if [ -L \"${{PROCESS_DIR}}{norm_path}\" ]; then")
                symlink_cleanup_lines.append(f"    rm \"${{PROCESS_DIR}}{norm_path}\"")
                symlink_cleanup_lines.append(f"    echo \"Removed symlink ${{PROCESS_DIR}}{norm_path}\"")
                symlink_cleanup_lines.append("fi")
            
            symbolic_links_setup = "\n".join(symlink_setup_lines)
            symbolic_links_cleanup = "\n".join(symlink_cleanup_lines)
        
        try:
            singularity_build_command = self.generate_singularity_build_command()
        except (ValueError, FileNotFoundError):
            singularity_build_command = f"echo \"Error: Failed to generate Singularity build command\" && exit 1"
            
        # Container script - using simplified component template
        container_components = [
            {
                'template': str(components_dir / "script_header.sh.template"),
                'context': {
                    'script_type': 'Local',
                    'process_id': self.process_id,
                    'execution_mode_desc': 'as a Singularity container',
                    'scheduler_desc': '',
                    'usage_command': './run_container.sh [--env KEY=VALUE...] [--bind PATH=EXTERNAL_PATH...] [arguments to pass to main.py]',
                    'environment_variables_comment': env_vars_comment,
                    'bind_paths_comment': bind_paths_comment,
                    'author': self.author,
                    'creation_date': datetime.datetime.now().strftime("%Y-%m-%d")
                }
            },
            {
                'template': str(components_dir / "variable_setup.sh.template"),
                'context': {
                    'dir_levels': '2',
                    'dir_path': '../..',
                    'process_id': self.process_id,
                    'process_name': self.process_name,
                    'resource_path_var': 'IMAGE_PATH',
                    'resource_path': str(self._paths.get_process_image_path(self.process_id)),
                    'script_var': 'MAIN_SCRIPT',
                    'script_path': 'main.py',
                    'other_vars': 'DEF_FILE="' + self.process_id + '.def"',
                    'script_header': 'Local Container',
                    'execution_mode_desc': 'as a container',
                    'scheduler_echo': '',
                    'environment_variables_export': env_vars_export
                }
            },
            {
                'template': str(components_dir / "arg_parsing.sh.template"),
                'context': {
                    'singularity_args_init': 'SINGULARITY_ARGS=()'
                }
            },
            {
                'template': str(components_dir / "simplified_container_execution.sh.template"),
                'context': {
                    'singularity_command': singularity_command
                }
            }
        ]
        
        container_script = assemble_script(container_components)
        container_path = process_dir / "execute" / "run_container.sh"
        with open(container_path, "w") as f:
            f.write(container_script)
        os.chmod(container_path, 0o755)
        
        # Virtual environment script - using components (unchanged)
        try:
            venv_creation_command = self.generate_venv_creation_command()
        except (ValueError, FileNotFoundError):
            venv_creation_command = f"echo \"Error: Failed to generate virtual environment creation command\" && exit 1"
            
        venv_components = [
            {
                'template': str(components_dir / "script_header.sh.template"),
                'context': {
                    'script_type': 'Local',
                    'process_id': self.process_id,
                    'execution_mode_desc': 'using a Python virtual environment',
                    'scheduler_desc': '',
                    'usage_command': './run_venv.sh [--env KEY=VALUE...] [--bind PATH=EXTERNAL_PATH...] [arguments to pass to main.py]',
                    'environment_variables_comment': env_vars_comment,
                    'bind_paths_comment': bind_paths_comment,
                    'author': self.author,
                    'creation_date': datetime.datetime.now().strftime("%Y-%m-%d")
                }
            },
            {
                'template': str(components_dir / "variable_setup.sh.template"),
                'context': {
                    'dir_levels': '2',
                    'dir_path': '../..',
                    'process_id': self.process_id,
                    'process_name': self.process_name,
                    'resource_path_var': 'VENV_PATH',
                    'resource_path': str(self._paths.get_venv_path(self.process_id)),
                    'script_var': 'MAIN_SCRIPT',
                    'script_path': 'main.py',
                    'other_vars': 'INSTALL_SCRIPT="install_requirements.sh"',
                    'script_header': 'Local Venv',
                    'execution_mode_desc': 'with virtual environment',
                    'scheduler_echo': '',
                    'environment_variables_export': env_vars_export
                }
            },
            {
                'template': str(components_dir / "arg_parsing.sh.template"),
                'context': {
                    'singularity_args_init': '# No singularity args for venv mode'
                }
            },
            {
                'template': str(components_dir / "venv_validation.sh.template"),
                'context': {}
            },
            {
                'template': str(components_dir / "env_var_processing.sh.template"),
                'context': {}
            },
            {
                'template': str(components_dir / "venv_bind_paths.sh.template"),
                'context': {
                    'symbolic_links_setup': symbolic_links_setup
                }
            },
            {
                'template': str(components_dir / "venv_execution.sh.template"),
                'context': {
                    'symbolic_links_cleanup': symbolic_links_cleanup
                }
            }
        ]
        
        venv_script = assemble_script(venv_components)
        venv_path = process_dir / "execute" / "run_venv.sh"
        with open(venv_path, "w") as f:
            f.write(venv_script)
        os.chmod(venv_path, 0o755)
    
    
    def _populate_script_paths(self, process_dir: Path) -> None:
        """
        Populate the script_paths dictionary with paths to all generated scripts.
        
        Args:
            process_dir: Path to the process directory
        """
        # Initialize script_paths if it doesn't exist
        if self.script_paths is None or self.script_paths == {}:
            self.script_paths = {
                "main": None,
                "udf": None,
                "wrapper": None,
                "install": None,
                "singularity_def": None,
                "build": {
                    "image": None,
                    "venv": None
                },
                "execute": {
                    "container": None,
                    "venv": None
                }
            }
            
        # Populate main script if it exists
        main_script = process_dir / "main.py"
        if main_script.exists():
            self.script_paths["main"] = main_script
            
        # Populate udf script if it exists
        udf_script = process_dir / "udf.py"
        if udf_script.exists():
            self.script_paths["udf"] = udf_script
            
        # Populate wrapper script if it exists
        wrapper_script = process_dir / "wrapper.py"
        if wrapper_script.exists():
            self.script_paths["wrapper"] = wrapper_script
            
        # Populate install script if it exists
        install_script = process_dir / "install_requirements.sh"
        if install_script.exists():
            self.script_paths["install"] = install_script
            
        # Populate Singularity definition file if it exists
        singularity_def = process_dir / f"{self.process_id}.def"
        if singularity_def.exists():
            self.script_paths["singularity_def"] = singularity_def
            
        # Populate build scripts
        build_dir = process_dir / "build"
        if build_dir.exists():
            # Image build script
            image_script = build_dir / "image.sh"
            if image_script.exists():
                self.script_paths["build"]["image"] = image_script

            # Virtual environment build script
            venv_script = build_dir / "venv.sh"
            if venv_script.exists():
                self.script_paths["build"]["venv"] = venv_script
                
        # Populate execution scripts
        execute_dir = process_dir / "execute"
        if execute_dir.exists():
            # Execution scripts
            container_script = execute_dir / "run_container.sh"
            if container_script.exists():
                self.script_paths["execute"]["container"] = container_script

            script_script = execute_dir / "run_venv.sh"
            if script_script.exists():
                self.script_paths["execute"]["venv"] = script_script

    def _save_model_json(self, process_dir: Path) -> None:
        """Save the complete model JSON for reproducibility."""
        # # Get model data excluding working_dir
        # model_data = self.model_dump(exclude={"working_dir"})
        # model_data = self.model_dump()
        
        
        # # Convert Path objects to strings
        # def convert_paths_to_strings(obj):
        #     if isinstance(obj, dict):
        #         return {k: convert_paths_to_strings(v) for k, v in obj.items()}
        #     elif isinstance(obj, list):
        #         return [convert_paths_to_strings(item) for item in obj]
        #     elif isinstance(obj, Path):
        #         return str(obj)
        #     else:
        #         return obj
        
        # model_data = convert_paths_to_strings(model_data)
        
        # # Ensure script_paths is properly serialized if it exists
        # if self.script_paths is not None:
        #     model_data["script_paths"] = {
        #         k: str(v) for k, v in self.script_paths.items()
        #     }
        
        # model_path = process_dir / "model.json"
        # with open(model_path, "w") as f:
        #     json.dump(model_data, f, indent=2)
        
        json_str: str = self.model_dump_json(indent=2)
        with open(process_dir / "model.json", "w") as f:
            f.write(json_str)

    # Utility methods
    def build_singularity_image(self) -> Path:
        """
        Build the Singularity image for this process.
        
        Returns:
            Path to the built image
        """
        if self.working_dir is None:
            raise ValueError("Working directory has not been generated yet")
            
        def_file = self.working_dir / f"{self.process_id}.def"
        if not def_file.exists():
            raise FileNotFoundError(f"Singularity definition file not found: {def_file}")
            
        # Create directory for the image if it doesn't exist
        image_path = self._paths.get_process_image_path(self.process_id)
        image_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build the image
        cmd = ["singularity", "build", str(image_path), str(def_file)]
        try:
            subprocess.run(cmd, check=True, cwd=str(self.working_dir))
            return image_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to build Singularity image: {e}")
    
    def create_virtual_env(self) -> Path:
        """
        Create a virtual environment for this process.
        
        Returns:
            Path to the created virtual environment
        """
        if self.working_dir is None:
            raise ValueError("Working directory has not been generated yet")
            
        install_script = self.working_dir / "install_requirements.sh"
        if not install_script.exists():
            raise FileNotFoundError(f"Installation script not found: {install_script}")
            
        # Create directory for the venv if it doesn't exist
        venv_path = self._paths.get_venv_path(self.process_id)
        venv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create the virtual environment
        cmd1 = ["python3", "-m", "venv", str(venv_path)]
        try:
            subprocess.run(cmd1, check=True)
            
            # Run the installation script within the virtual environment
            activate_cmd = f"source {venv_path}/bin/activate"
            cmd2 = f"{activate_cmd} && bash {install_script} && deactivate"
            subprocess.run(cmd2, shell=True, check=True, cwd=str(self.working_dir))
            
            return venv_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create virtual environment: {e}")
            
    def generate_singularity_execution_command(self, use_runtime_vars: bool = False) -> str:
        """
        Generate a standalone Singularity execution command with appropriate bind paths and environment variables.
        
        Args:
            use_runtime_vars: If True, use script variables like ${VAR} instead of placeholders like <var_value>
                             This is useful when generating commands to be embedded in shell scripts.
        
        Returns:
            String containing the Singularity execution command
        """
        # Start with the basic command
        image_path = self._paths.get_process_image_path(self.process_id)
        # command_parts = [f"singularity run {image_path}"]
        command_parts = [f"singularity run"]
        
        # Add command flags immediately after 'singularity run'
        if self.config.command_flags:
            command_parts.append(" ".join(self.config.command_flags))
        
        # Add environment variables with --env
        if self.config.environment_variables:
            env_args = []
            for var in self.config.environment_variables:
                if use_runtime_vars:
                    # Use script variables that will be set at runtime
                    env_args.append(f"--env {var}=\"${{{var}}}\"")
                else:
                    # Use placeholders for documentation
                    env_args.append(f"--env {var}=<{var.lower()}_value>")
            
            command_parts.append(" ".join(env_args))
                
        # Add bind paths with --bind
        if self.config.bind_paths:
            bind_args = []
            for path in self.config.bind_paths:
                # Normalize path to ensure consistent handling
                norm_path = path if path.startswith('/') else f"/{path}"
                # Strip trailing slash if present for consistency
                norm_path = norm_path.rstrip('/')
                
                if use_runtime_vars:
                    # Use the BIND_PATHS associative array that will be set at runtime
                    # Escape the path when used as an array key to handle special characters
                    safe_key = norm_path.replace('"', '\\"')  # Escape double quotes in the path
                    bind_args.append(f"--bind \"${{BIND_PATHS[\"{safe_key}\"]}}\":\"{norm_path}\"")
                else:
                    # Use placeholders for documentation
                    bind_args.append(f"--bind \"<path_to{norm_path}>\":\"{norm_path}\"")
            
            command_parts.append(" ".join(bind_args))
            
        # Specify the image path
        command_parts.append(f"\"{image_path}\"")
        
        # Return the final command
        return " ".join(command_parts)
    
    def generate_singularity_build_command(self) -> str:
        """
        Generate the command to build a Singularity image for this process.
        
        Returns:
            String containing the command to build the Singularity image
        """
        if self.working_dir is None:
            raise ValueError("Working directory has not been generated yet")
            
        def_file = self.working_dir / f"{self.process_id}.def"
        if not def_file.exists():
            raise FileNotFoundError(f"Singularity definition file not found: {def_file}")
            
        # Get the path where the image should be stored
        image_path = self._paths.get_process_image_path(self.process_id)
        
        # Create the command to build the image
        # Make sure parent directory exists
        mkdir_cmd = f"mkdir -p \"{image_path.parent}\""
        
        # Build the singularity image
        build_cmd = f"singularity build \"{image_path}\" \"{def_file}\""
        
        return f"{mkdir_cmd} && {build_cmd}"
    
    def generate_venv_creation_command(self) -> str:
        """
        Generate the command to create a virtual environment for this process.
        
        Returns:
            String containing the command to create the virtual environment
        """
        if self.working_dir is None:
            raise ValueError("Working directory has not been generated yet")
            
        install_script = self.working_dir / "install_requirements.sh"
        if not install_script.exists():
            raise FileNotFoundError(f"Installation script not found: {install_script}")
            
        # Get the path where the venv should be stored
        venv_path = self._paths.get_venv_path(self.process_id)
        
        # Create the command to create the venv
        # Make sure parent directory exists
        mkdir_cmd = f"mkdir -p \"{venv_path.parent}\""
        
        # Create the virtual environment
        venv_cmd = f"python3 -m venv \"{venv_path}\""
        
        # Activate and install requirements
        activate_cmd = f"source \"{venv_path}/bin/activate\""
        install_cmd = f"bash \"{install_script}\""
        deactivate_cmd = "deactivate"
        
        return f"{mkdir_cmd} && {venv_cmd} && {activate_cmd} && {install_cmd} && {deactivate_cmd}"

    def generate_execution_command(self, execution_mode: str = None, scheduler: str = None) -> str:
        """
        Generate the execution command for a specific execution mode and scheduler.
        
        Args:
            execution_mode: Mode of execution (container or venv). If None, default to container.
            scheduler: Scheduler to use (local, slurm, pbs, lsf). If None, default to local.
            
        Returns:
            String containing the execution command
        """
        if self.working_dir is None:
            raise ValueError("Working directory has not been generated yet")
        
        # Default values
        if execution_mode is None:
            execution_mode = "container"
        
        if scheduler is None:
            scheduler = "local"
            
        # Validate inputs
        if execution_mode not in ("container", "script"):
            raise ValueError(f"Invalid execution mode: {execution_mode}. Must be container or script.")
            
        if scheduler not in ("local", "slurm", "pbs", "lsf"):
            raise ValueError(f"Invalid scheduler: {scheduler}. Must be local, slurm, pbs, or lsf.")
        
        # Determine script path - Using working_dir directly to find the scripts
        # All execution scripts are now directly in the execute directory
        script_dir = self.working_dir / "execute"
        script_name = "run_container.sh" if execution_mode == "container" else "run_venv.sh"
        script_path = script_dir / script_name
        
        # Set appropriate scheduler command if needed
        if scheduler == "slurm":
            scheduler_cmd = "sbatch"
        elif scheduler == "pbs":
            scheduler_cmd = "qsub"
        elif scheduler == "lsf":
            scheduler_cmd = "bsub"
        else:
            scheduler_cmd = ""  # No scheduler command for local execution
        
        # Check if script exists - use only the path part, not the scheduler command
        if not script_path.exists():
            raise FileNotFoundError(f"Execution script not found: {script_path}")
        
        # Build command with environment variables and bind paths
        if scheduler_cmd:
            command_parts = [scheduler_cmd, str(script_path)]
        else:
            command_parts = [str(script_path)]
        
        # Add environment variables with simplified format
        if self.config.environment_variables:
            env_args = []
            for var in self.config.environment_variables:
                # Use the same format for all schedulers for consistency
                env_args.append(f"--env {var}=<{var.lower()}_value>")
            
            command_parts.append(" ".join(env_args))
                
        # Add bind paths with simplified format
        if self.config.bind_paths:
            bind_args = []
            for path in self.config.bind_paths:
                # Normalize path to ensure consistent handling
                norm_path = path if path.startswith('/') else f"/{path}"
                # Strip trailing slash if present for consistency
                norm_path = norm_path.rstrip('/')
                # Use simplified format for bind paths
                bind_args.append(f"--bind {norm_path}=<path_to{norm_path}>")
            
            command_parts.append(" ".join(bind_args))
        
        # Return the final command
        return " ".join(command_parts)
        
    def generate_all_execution_commands(self) -> Dict[str, Dict[str, str]]:
        """
        Generate execution commands for all combinations of execution modes and schedulers.
        
        Returns:
            Dictionary of execution commands organized by scheduler and execution mode
        """
        if self.working_dir is None:
            raise ValueError("Working directory has not been generated yet")
            
        schedulers = ["local", "slurm", "pbs", "lsf"]
        execution_modes = ["container", "script"]
        
        commands = {}
        
        for scheduler in schedulers:
            commands[scheduler] = {}
            for mode in execution_modes:
                try:
                    commands[scheduler][mode] = self.generate_execution_command(mode, scheduler)
                except (ValueError, FileNotFoundError):
                    # Skip if script doesn't exist
                    continue
                    
        return commands
        
    def generate_example_execution_command(self, execution_mode: str = None, scheduler: str = None, 
                                          env_values: Dict[str, str] = None, 
                                          bind_values: Dict[str, str] = None) -> str:
        """
        Generate an example execution command with actual values for environment variables and bind paths.
        
        Args:
            execution_mode: Mode of execution (container or venv). If None, default to container.
            scheduler: Scheduler to use (local, slurm, pbs, lsf). If None, default to local.
            env_values: Dictionary of environment variable names and values.
            bind_values: Dictionary of bind path names and target paths.
            
        Returns:
            String containing the execution command with actual values
        """
        # Generate the base command
        base_command = self.generate_execution_command(execution_mode, scheduler)
        
        # Default values
        if env_values is None:
            env_values = {}
            
        if bind_values is None:
            bind_values = {}
            
        # Replace environment variable placeholders with actual values
        command = base_command
        
        # Replace env placeholders
        for var, value in env_values.items():
            command = command.replace(f"--env {var}=<{var.lower()}_value>", f"--env {var}={value}")
                
        # Replace bind path placeholders
        for path, target in bind_values.items():
            # Normalize path to ensure consistent handling
            norm_path = path if path.startswith('/') else f"/{path}"
            # Strip trailing slash if present for consistency
            norm_path = norm_path.rstrip('/')
            
            command = command.replace(f"--bind {norm_path}=<path_to{norm_path}>", f"--bind {norm_path}={target}")
                
        return command
