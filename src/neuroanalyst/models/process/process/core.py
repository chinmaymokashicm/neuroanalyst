"""
NeuProcess Core Module

This module implements the NeuProcess class, which represents a neuroimaging process.
NeuProcess is not executed directly, but serves as a container for process metadata,
Singularity image building, and virtual environment creation functionality.

NeuProcess builds upon NeuProcessDir, which provides the directory structure and configuration
required for process preparation.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, ClassVar

from pydantic import BaseModel, Field, model_validator

from ....utils.constants import NeuroAnalystPaths
from ....utils.id_generators import generate_process_id
from ...about import About
from ..dir.core import NeuProcessDir


class NeuProcess(BaseModel):
    """
    NeuProcess - Class representing a neuroimaging process.
    
    This class handles:
    1. Building Singularity/Apptainer images from NeuProcessDir instances
    2. Creating virtual environments for script-based execution
    
    A NeuProcess can be created from a NeuProcessDir, a path to a process directory,
    or a process ID using the provided classmethods.
    
    Note: NeuProcess is not executed directly. The NeuProcessExec class will be responsible
    for execution-related functionality.
    """
    
    # Basic information
    process_id: str = Field(default_factory=generate_process_id, 
                          description="Unique identifier for the process")
    
    # Input source
    process_dir: NeuProcessDir = Field(description="NeuProcessDir instance")
    
    # Execution requirements
    bind_paths: List[str] = Field(default_factory=list,
                                description="Paths that need to be mounted/aliased at runtime")
    environment_variables: List[str] = Field(default_factory=list,
                                          description="Environment variables required for execution")
    command_flags: Optional[List[str]] = Field(default=None,
                                                description="Additional command-line flags for the process. E.g., ['--verbose', '--fakeroot']")

    # Class variables
    _paths: ClassVar[NeuroAnalystPaths] = NeuroAnalystPaths()
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the NeuProcess."""
        string: str = f"""
        NeuProcess:
          ID: {self.process_id}
          Name: {self.process_dir.logic.about.name}
          Directory: {self.process_dir.working_dir}
          Bind Paths: {self.bind_paths}
          Environment Variables: {self.environment_variables}
          Command Flags: {self.command_flags}
        """
        return string.strip()
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the NeuProcess."""
        string: str = f"""
        NeuProcess(
          process_id='{self.process_id}',
          process_dir={repr(self.process_dir)},
          bind_paths={self.bind_paths},
          environment_variables={self.environment_variables},
          command_flags={self.command_flags}
        )
        """
        return string.strip()
    
    def model_post_init(self, __context):
        """Post-initialization processing."""
        # Initialize bind_paths and environment_variables from process_dir if not provided
        if self.process_dir and self.process_dir.config:
            # Only copy if the user hasn't explicitly set them
            if not self.bind_paths and self.process_dir.config.bind_paths:
                self.bind_paths = self.process_dir.config.bind_paths.copy()
                
            if not self.environment_variables and self.process_dir.config.environment_variables:
                self.environment_variables = self.process_dir.config.environment_variables.copy()
                
            # Copy command flags if not explicitly set
            if self.command_flags is None and hasattr(self.process_dir.config, 'command_flags'):
                self.command_flags = self.process_dir.config.command_flags.copy() if self.process_dir.config.command_flags else []
            
            # Update process_id if not explicitly set
            if self.process_id == generate_process_id():  # If it's a default generated ID
                self.process_id = self.process_dir.process_id
    
    @classmethod
    def from_process_dir(cls, process_dir: NeuProcessDir, **kwargs):
        """
        Create a NeuProcess from a NeuProcessDir instance.
        
        Args:
            process_dir: NeuProcessDir instance
            **kwargs: Additional arguments to pass to the NeuProcess constructor
            
        Returns:
            NeuProcess instance
        """
        return cls(process_dir=process_dir, **kwargs)
    
    @classmethod
    def from_dir_path(cls, dir_path: Path, **kwargs):
        """
        Create a NeuProcess from a path to a process directory.
        
        Args:
            dir_path: Path to the process directory
            **kwargs: Additional arguments to pass to the NeuProcess constructor
            
        Returns:
            NeuProcess instance
            
        Raises:
            FileNotFoundError: If model.json is not found in the directory
            ValueError: If the model.json file cannot be parsed
        """
        model_json_path = dir_path / "model.json"
        if not model_json_path.exists():
            raise FileNotFoundError(f"model.json not found at {model_json_path}")
            
        try:
            with open(model_json_path, "r") as f:
                model_data = json.load(f)
            
            # If script_paths exists but is null in the JSON, set it to None
            if "script_paths" in model_data and model_data["script_paths"] is None:
                del model_data["script_paths"]  # Remove the key to use the default
            
            # Convert string paths back to Path objects in script_paths if present
            if "script_paths" in model_data and model_data["script_paths"]:
                script_paths = model_data["script_paths"]
                for key, path_str in script_paths.items():
                    if isinstance(path_str, str):
                        script_paths[key] = Path(path_str)
            
            # Create and validate the process_dir
            process_dir = NeuProcessDir.model_validate(model_data)
            
            # Set the working_dir since it was excluded in the JSON
            process_dir.working_dir = dir_path
            
            return cls(process_dir=process_dir, **kwargs)
                
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to load NeuProcessDir from {model_json_path}: {e}")
    
    @classmethod
    def from_process_id(cls, process_id: str, **kwargs):
        """
        Create a NeuProcess from a process ID.
        
        Args:
            process_id: Process ID
            **kwargs: Additional arguments to pass to the NeuProcess constructor
            
        Returns:
            NeuProcess instance
            
        Raises:
            FileNotFoundError: If the process directory is not found
            ValueError: If the model.json file cannot be parsed
        """
        paths = NeuroAnalystPaths()
        dir_path = paths.get_process_workdir(process_id)
        return cls.from_dir_path(dir_path, process_id=process_id, **kwargs)
    
    # Properties to access NeuProcessDir attributes
    @property
    def working_dir(self) -> Path:
        """Get the working directory."""
        return self.process_dir.working_dir
    
    @property
    def config(self) -> Any:
        """Get the process configuration."""
        return self.process_dir.config
    
    @property
    def process_name(self) -> str:
        """Get the process name."""
        return self.process_dir.process_name
    
    @property
    def description(self) -> str:
        """Get the process description."""
        return self.process_dir.description
    
    @property
    def version(self) -> str:
        """Get the process version."""
        return self.process_dir.version
    
    @property
    def author(self) -> str:
        """Get the author of the process."""
        return self.process_dir.author
    
    @property
    def image_path(self) -> Path:
        """Get the path to the Singularity image."""
        return self._paths.get_process_image_path(self.process_id)
    
    @property
    def venv_path(self) -> Path:
        """Get the path to the virtual environment."""
        return self._paths.get_venv_path(self.process_id)
    
    @property
    def logic(self) -> Any:
        """Get the logic associated with the process."""
        return self.process_dir.logic
    
    # Singularity image methods
    def build_singularity_image(self, scheduler=None, scheduler_args=None, **kwargs) -> tuple[Path, str]:
        """
        Build a Singularity image for this process.
        
        Args:
            scheduler: Optional scheduler to use ("slurm", "pbs", "lsf"). If None, builds locally.
            scheduler_args: Dictionary of scheduler-specific arguments with keys matching scheduler flags.
            **kwargs: Additional arguments for backward compatibility.
        
        Returns:
            Tuple containing (image_path, job_id)
        
        Raises:
            RuntimeError: If image build fails
        """
            
        return self.process_dir.build_singularity_image(scheduler=scheduler, scheduler_args=scheduler_args)
    
    def image_exists(self) -> bool:
        """
        Check if the Singularity image for this process exists.
        
        Returns:
            True if the image exists, False otherwise
        """
        return self.image_path.exists()
        
    def generate_singularity_build_command(self, scheduler=None, scheduler_args=None) -> str:
        """
        Generate the command to build a Singularity image for this process.
        
        Args:
            scheduler: Optional scheduler to use ("slurm", "pbs", "lsf"). If None, builds locally.
            scheduler_args: Dictionary of scheduler-specific arguments with keys matching scheduler flags.
        
        Returns:
            String containing the command to build the Singularity image
        """
            
        return self.process_dir.generate_singularity_build_command(scheduler=scheduler, scheduler_args=scheduler_args)
    
    # Virtual environment methods
    def create_virtual_env(self, scheduler=None, scheduler_args=None, **kwargs) -> tuple[Path, str]:
        """
        Create a virtual environment for this process.
        
        Args:
            scheduler: Optional scheduler to use ("slurm", "pbs", "lsf"). If None, builds locally.
            scheduler_args: Dictionary of scheduler-specific arguments with keys matching scheduler flags.
            **kwargs: Additional arguments for backward compatibility.
        
        Returns:
            Tuple containing (venv_path, job_id)
            
        Raises:
            RuntimeError: If virtual environment creation fails
        """
            
        return self.process_dir.create_virtual_env(scheduler=scheduler, scheduler_args=scheduler_args)
    
    def venv_exists(self) -> bool:
        """
        Check if the virtual environment for this process exists.
        
        Returns:
            True if the virtual environment exists, False otherwise
        """
        return self.venv_path.exists()
        
    def generate_venv_creation_command(self, scheduler=None, scheduler_args=None) -> str:
        """
        Generate the command to create a virtual environment for this process.
        
        Args:
            scheduler: Optional scheduler to use ("slurm", "pbs", "lsf"). If None, builds locally.
            scheduler_args: Dictionary of scheduler-specific arguments with keys matching scheduler flags.
        
        Returns:
            String containing the command to create the virtual environment
        """

        return self.process_dir.generate_venv_creation_command(scheduler=scheduler, scheduler_args=scheduler_args) and (self.venv_path / "bin" / "python").exists()

    # Bind paths and environment variables management
    def add_bind_path(self, path: str) -> None:
        """
        Add a bind path to the process.
        
        Args:
            path: Path to add
        """
        # Normalize the path to ensure consistent handling
        norm_path = path if path.startswith('/') else f"/{path}"
        # Strip trailing slash for consistency
        norm_path = norm_path.rstrip('/')
        
        if norm_path not in self.bind_paths:
            self.bind_paths.append(norm_path)
    
    def remove_bind_path(self, path: str) -> bool:
        """
        Remove a bind path from the process.
        
        Args:
            path: Path to remove
            
        Returns:
            True if the path was removed, False if it wasn't found
        """
        # Normalize the path to ensure consistent handling
        norm_path = path if path.startswith('/') else f"/{path}"
        # Strip trailing slash for consistency
        norm_path = norm_path.rstrip('/')
        
        if norm_path in self.bind_paths:
            self.bind_paths.remove(norm_path)
            return True
        return False
    
    def add_environment_variable(self, variable: str) -> None:
        """
        Add an environment variable to the process.
        
        Args:
            variable: Environment variable to add
        """
        if variable not in self.environment_variables:
            self.environment_variables.append(variable)
    
    def remove_environment_variable(self, variable: str) -> bool:
        """
        Remove an environment variable from the process.
        
        Args:
            variable: Environment variable to remove
            
        Returns:
            True if the variable was removed, False if it wasn't found
        """
        if variable in self.environment_variables:
            self.environment_variables.remove(variable)
            return True
        return False
    
    def get_non_standard_bind_paths(self) -> list[str]:
        """
        Get bind paths that are not standard NeuroAnalyst paths.
        
        Returns:
            List of non-standard bind paths
        """
        standard_paths: set[str] = {"/data"}
        return [path for path in self.bind_paths if path not in standard_paths]
    
    def get_non_standard_environment_variables(self) -> list[str]:
        """
        Get environment variables that are not standard NeuroAnalyst variables.
        
        Returns:
            List of non-standard environment variables
        """
        standard_vars: set[str] = {"BIDS_FILTERS", "PROCESS_ID", "PROCESS_EXEC_ID", "PIPELINE_ID", "PIPELINE_NAME"}
        return [var for var in self.environment_variables if var not in standard_vars]
    
    def get_non_standard_parameters(self) -> Dict[str, Any]:
        """
        Get non-standard parameters (bind paths and environment variables).
        
        Returns:
            Dictionary with keys 'bind_paths' and 'environment_variables' containing non-standard entries
        """
        return {
            "bind_paths": self.get_non_standard_bind_paths(),
            "environment_variables": self.get_non_standard_environment_variables()
        }
