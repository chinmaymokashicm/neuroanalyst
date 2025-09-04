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
    or a process ID.
    
    Note: NeuProcess is not executed directly. The NeuProcessExec class will be responsible
    for execution-related functionality.
    """
    
    # Basic information
    process_id: str = Field(default_factory=generate_process_id, 
                          description="Unique identifier for the process")
    
    # Input sources (mutually exclusive)
    process_dir: Optional[NeuProcessDir] = Field(default=None, 
                                               description="NeuProcessDir instance")
    process_dir_path: Optional[Path] = Field(default=None, 
                                           description="Path to the process directory")
    
    # Execution requirements
    bind_paths: List[str] = Field(default_factory=list,
                                description="Paths that need to be mounted/aliased at runtime")
    environment_variables: List[str] = Field(default_factory=list,
                                          description="Environment variables required for execution")
    
    # Class variables
    _paths: ClassVar[NeuroAnalystPaths] = NeuroAnalystPaths()
    
    # Model validators
    @model_validator(mode="before")
    def check_input_sources(cls, values):
        """Validate that at least one input source is provided."""
        process_dir = values.get('process_dir')
        process_dir_path = values.get('process_dir_path')
        process_id = values.get('process_id')
        
        if process_dir is None and process_dir_path is None and process_id is None:
            raise ValueError("Either 'process_dir', 'process_dir_path', or 'process_id' must be provided")
            
        # If process_id is provided but not process_dir_path, construct the path
        if process_id is not None and process_dir_path is None and process_dir is None:
            values['process_dir_path'] = cls._paths.get_process_workdir(process_id)
            
        return values
    
    def model_post_init(self, __context):
        """Post-initialization processing."""
        # If process_dir_path is provided but not process_dir, load the NeuProcessDir from the path
        if self.process_dir is None and self.process_dir_path is not None:
            self._load_process_dir()
            
        # Initialize bind_paths and environment_variables from process_dir if not provided
        if self.process_dir and self.process_dir.config:
            # Only copy if the user hasn't explicitly set them
            if not self.bind_paths and self.process_dir.config.bind_paths:
                self.bind_paths = self.process_dir.config.bind_paths.copy()
                
            if not self.environment_variables and self.process_dir.config.environment_variables:
                self.environment_variables = self.process_dir.config.environment_variables.copy()
    
    def _load_process_dir(self) -> None:
        """Load NeuProcessDir from process_dir_path."""
        if self.process_dir_path is None:
            raise ValueError("process_dir_path must be provided")
            
        model_json_path = self.process_dir_path / "model.json"
        if not model_json_path.exists():
            raise FileNotFoundError(f"model.json not found at {model_json_path}")
            
        try:
            with open(model_json_path, "r") as f:
                model_data = json.load(f)
            
            self.process_dir = NeuProcessDir.model_validate(model_data)
            
            # Update process_id if not explicitly set
            if self.process_id == generate_process_id():  # If it's a default generated ID
                self.process_id = self.process_dir.process_id
                
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to load NeuProcessDir from {model_json_path}: {e}")
    
    # Properties to access NeuProcessDir attributes
    @property
    def working_dir(self) -> Optional[Path]:
        """Get the working directory."""
        if self.process_dir:
            return self.process_dir.working_dir
        return None
    
    @property
    def config(self) -> Any:
        """Get the process configuration."""
        if self.process_dir:
            return self.process_dir.config
        return None
    
    # Note: bind_paths and environment_variables are now explicit fields, so we don't need property methods for them.
    # The properties below are kept for backwards compatibility and are now deprecated.
    
    @property
    def process_bind_paths(self) -> List[str]:
        """Get the bind paths from the underlying process_dir. Deprecated, use bind_paths field directly."""
        if self.process_dir and self.process_dir.config:
            return self.process_dir.config.bind_paths
        return []
    
    @property
    def process_environment_variables(self) -> List[str]:
        """Get the environment variables from the underlying process_dir. Deprecated, use environment_variables field directly."""
        if self.process_dir and self.process_dir.config:
            return self.process_dir.config.environment_variables
        return []
    
    @property
    def process_name(self) -> str:
        """Get the process name."""
        if self.process_dir:
            return self.process_dir.process_name
        return self.process_id
    
    @property
    def description(self) -> str:
        """Get the process description."""
        if self.process_dir:
            return self.process_dir.description
        return f"Process {self.process_id}"
    
    @property
    def version(self) -> str:
        """Get the process version."""
        if self.process_dir:
            return self.process_dir.version
        return "1.0.0"
    
    @property
    def author(self) -> str:
        """Get the author of the process."""
        if self.process_dir:
            return self.process_dir.author
        return "NeuroAnalyst User"
    
    @property
    def image_path(self) -> Path:
        """Get the path to the Singularity image."""
        return self._paths.get_process_image_path(self.process_id)
    
    @property
    def venv_path(self) -> Path:
        """Get the path to the virtual environment."""
        return self._paths.get_venv_path(self.process_id)
    
    # Singularity image methods
    def build_image(self) -> Path:
        """
        Build the Singularity image for this process.
        
        Returns:
            Path to the built image
        
        Raises:
            ValueError: If process_dir is not available
            RuntimeError: If image build fails
        """
        if self.process_dir is None:
            self._load_process_dir()
            
        if self.process_dir is None:
            raise ValueError("Cannot build image: process_dir is not available")
            
        return self.process_dir.build_singularity_image()
    
    def image_exists(self) -> bool:
        """
        Check if the Singularity image for this process exists.
        
        Returns:
            True if the image exists, False otherwise
        """
        return self.image_path.exists()
    
    # Virtual environment methods
    def create_virtual_env(self) -> Path:
        """
        Create a virtual environment for this process.
        
        Returns:
            Path to the created virtual environment
            
        Raises:
            ValueError: If process_dir is not available
            RuntimeError: If virtual environment creation fails
        """
        if self.process_dir is None:
            self._load_process_dir()
            
        if self.process_dir is None:
            raise ValueError("Cannot create virtual environment: process_dir is not available")
            
        return self.process_dir.create_virtual_env()
    
    def venv_exists(self) -> bool:
        """
        Check if the virtual environment for this process exists.
        
        Returns:
            True if the virtual environment exists, False otherwise
        """
        return self.venv_path.exists() and (self.venv_path / "bin" / "python").exists()
    
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
