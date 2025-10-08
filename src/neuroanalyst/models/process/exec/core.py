"""
NeuProcessExec Core Module

This module implements the NeuProcessExec class, which represents an execution instance
of a neuroimaging process (NeuProcess). NeuProcessExec is responsible for executing
a NeuProcess with specific runtime configuration, including bind paths and environment variables.

NeuProcessExec serves as a bridge between the abstract NeuProcess definition and the
actual execution in a specific environment (local, HPC) and mode (script, container).
"""

import os
import json
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, ClassVar

from pydantic import BaseModel, Field, field_validator, model_validator

from ....utils.constants import NeuroAnalystPaths
from ....utils.id_generators import generate_process_exec_id
from ..process.core import NeuProcess
from ..dir.core import ExecutionMode


# Custom JSON encoder that handles Path objects
class PathEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


class HPCScheduler(str, Enum):
    """Enum for HPC scheduler types."""
    LSF = "lsf"
    SLURM = "slurm"
    PBS = "pbs"
    LOCAL = "local"  # For local execution


class NeuProcessExec(BaseModel):
    """
    NeuProcessExec - Class representing an execution instance of a NeuProcess.
    
    This class handles:
    1. Execution of a NeuProcess with specific runtime configuration
    2. Generation of execution commands based on environment and mode
    3. Validation of bind paths and environment variables
    4. Execution of the generated commands
    
    A NeuProcessExec can be created from a NeuProcess, a process ID, or a path to a process directory.
    """
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the NeuProcessExec."""
        if hasattr(self, 'process') and hasattr(self.process, 'process_id'):
            process_id = self.process.process_id
        else:
            process_id = 'unknown'
        
        if hasattr(self, 'execution_id'):
            exec_id = self.execution_id
        else:
            exec_id = 'unknown'
            
        return f"NeuProcessExec(id='{exec_id}', process_id='{process_id}')"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the NeuProcessExec."""
        scheduler = getattr(self, 'scheduler', 'unknown')
        mode = getattr(self, 'execution_mode', 'unknown')
        
        return f"NeuProcessExec(id='{getattr(self, 'execution_id', 'unknown')}', "\
               f"process_id='{getattr(self.process, 'process_id', 'unknown') if hasattr(self, 'process') else 'unknown'}', "\
               f"mode='{mode}', scheduler='{scheduler}')"
    
    # Basic information
    exec_id: str = Field(default_factory=generate_process_exec_id, 
                        description="Unique identifier for the execution instance")
    
    # Input source (NeuProcess)
    process: NeuProcess = Field(description="NeuProcess to execute")
    
    # Runtime configuration
    bind_path_values: Dict[str, str] = Field(default_factory=dict,
                                          description="Values for bind paths, keyed by bind path name")
    env_var_values: Dict[str, str] = Field(default_factory=dict,
                                         description="Values for environment variables, keyed by variable name")
    
    # Execution options
    execution_mode: ExecutionMode = Field(default=ExecutionMode.CONTAINER,
                                        description="Mode of execution (venv, container, auto)")
    scheduler: HPCScheduler = Field(default=HPCScheduler.LSF,
                                  description="HPC scheduler to use (lsf, slurm, pbs, none)")
    
    # Command storage
    exec_command: Optional[str] = Field(default=None,
                                      description="Generated execution command")
    
    # Class variables
    _paths: ClassVar[NeuroAnalystPaths] = NeuroAnalystPaths()
    
    @model_validator(mode="after")
    def validate_bind_paths_and_env_vars(self) -> "NeuProcessExec":
        """
        Validate that all required bind paths and environment variables have values.
        This validator no longer raises exceptions but is used to ensure the model
        is properly initialized.
        """
        return self
    
    @classmethod
    def from_process(cls, process: NeuProcess, **kwargs) -> "NeuProcessExec":
        """
        Create a NeuProcessExec from a NeuProcess instance.
        
        Args:
            process: NeuProcess instance
            **kwargs: Additional arguments to pass to the NeuProcessExec constructor
            
        Returns:
            NeuProcessExec instance
        """
        return cls(process=process, **kwargs)
    
    @classmethod
    def from_process_id(cls, process_id: str, **kwargs) -> "NeuProcessExec":
        """
        Create a NeuProcessExec from a process ID.
        
        Args:
            process_id: Process ID
            **kwargs: Additional arguments to pass to the NeuProcessExec constructor
            
        Returns:
            NeuProcessExec instance
        """
        process = NeuProcess.from_process_id(process_id)
        return cls(process=process, **kwargs)
    
    @classmethod
    def from_dir_path(cls, dir_path: Path, **kwargs) -> "NeuProcessExec":
        """
        Create a NeuProcessExec from a path to a process directory.
        
        Args:
            dir_path: Path to the process directory
            **kwargs: Additional arguments to pass to the NeuProcessExec constructor
            
        Returns:
            NeuProcessExec instance
        """
        process = NeuProcess.from_dir_path(dir_path)
        return cls(process=process, **kwargs)
    
    @classmethod
    def from_exec_id(cls, exec_id: str) -> "NeuProcessExec":
        """
        Create a NeuProcessExec from a saved execution ID.
        
        Args:
            exec_id: Execution ID of a previously saved NeuProcessExec
            
        Returns:
            NeuProcessExec instance
            
        Raises:
            FileNotFoundError: If the execution directory or model.json file does not exist
            ValueError: If the model.json file cannot be parsed
        """
        from ....utils.constants import PATHS
        
        # Get the path to the execution directory
        exec_dir = PATHS.get_process_exec_path(exec_id)
        if not exec_dir.exists():
            raise FileNotFoundError(f"Execution directory not found: {exec_dir}")
        
        # Get the path to the model.json file
        model_path = exec_dir / "model.json"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load the model from the file
        try:
            with open(model_path, "r") as f:
                model_data = json.load(f)
            
            # Create and return the NeuProcessExec instance
            return cls.model_validate(model_data)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse model.json: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load NeuProcessExec from disk: {e}")
    
    def set_bind_path_value(self, bind_path: str, value: str) -> None:
        """
        Set the value for a bind path.
        
        Args:
            bind_path: Bind path name
            value: Bind path value
        
        Raises:
            ValueError: If the bind path is not required by the process
            
        Note:
            This method automatically normalizes paths by removing trailing slashes
            for consistent comparison. For example, '/data/' and '/data' are treated
            as the same path.
        """
        # Normalize the path by removing trailing slashes
        normalized_path = bind_path.rstrip('/')
        
        # Find a matching path in the required bind paths (ignoring trailing slashes)
        matching_path = None
        for path in self.process.bind_paths:
            if path.rstrip('/') == normalized_path:
                matching_path = path
                break
        
        if matching_path is None:
            raise ValueError(f"Bind path '{bind_path}' is not required by the process. Required paths: {', '.join(self.process.bind_paths)}")
        
        # Store the value using the original required path name from the process
        self.bind_path_values[matching_path] = value
        
        # Save the updated model to disk
        try:
            self.save_to_disk()
        except Exception as e:
            # Don't raise an exception if saving fails - just continue
            print(f"Warning: Failed to save execution model after updating bind path: {e}")
    
    def set_env_var_value(self, env_var: str, value: str) -> None:
        """
        Set the value for an environment variable.
        
        Args:
            env_var: Environment variable name
            value: Environment variable value
        
        Raises:
            ValueError: If the environment variable is not required by the process
        """
        if env_var not in self.process.environment_variables:
            raise ValueError(f"Environment variable '{env_var}' is not required by the process")
        
        self.env_var_values[env_var] = value
        
        # Save the updated model to disk
        try:
            self.save_to_disk()
        except Exception as e:
            # Don't raise an exception if saving fails - just continue
            print(f"Warning: Failed to save execution model after updating environment variable: {e}")
    
    def get_configuration_status(self) -> Dict[str, Dict[str, List[str]] | Dict[str, Any]]:
        """
        Get the status of required bind paths and environment variables.
        
        Returns:
            Dict with information about provided and missing bind paths and environment variables,
            as well as execution command status
            
        Note:
            This method handles path normalization, treating paths with or without
            trailing slashes as equivalent (e.g., '/data/' is the same as '/data').
        """
        # Get normalized (no trailing slash) versions of all required bind paths
        normalized_required_paths = {path.rstrip('/'): path for path in self.process.bind_paths}
        
        # Get normalized versions of all provided bind paths
        normalized_provided_paths = {path.rstrip('/'): path for path in self.bind_path_values.keys()}
        
        # Determine which paths are missing (based on normalized paths)
        missing_paths = []
        for norm_req_path, orig_req_path in normalized_required_paths.items():
            if norm_req_path not in normalized_provided_paths:
                missing_paths.append(orig_req_path)
        
        # For environment variables (no normalization needed)
        missing_env_vars = [var for var in self.process.environment_variables if var not in self.env_var_values]
        
        status = {
            "bind_paths": {
                "required": self.process.bind_paths,
                "provided": list(self.bind_path_values.keys()),
                "missing": missing_paths
            },
            "environment_variables": {
                "required": self.process.environment_variables,
                "provided": list(self.env_var_values.keys()),
                "missing": missing_env_vars
            },
            "command": {
                "is_set": self.exec_command is not None,
                "value": self.exec_command if self.exec_command is not None else None
            }
        }
        return status
    
    def print_configuration_status(self) -> None:
        """
        Print a report of the required, provided, and missing bind paths and environment variables,
        as well as the execution command status.
        """
        status = self.get_configuration_status()
        
        print(f"\n=== Configuration Status for NeuProcessExec {self.exec_id} ===")
        
        # Bind paths section
        print("\nBind Paths:")
        print(f"  Required ({len(status['bind_paths']['required'])}): {', '.join(status['bind_paths']['required'])}")
        print(f"  Provided ({len(status['bind_paths']['provided'])}): {', '.join(status['bind_paths']['provided'])}")
        
        if status['bind_paths']['missing']:
            print(f"  Missing ({len(status['bind_paths']['missing'])}): {', '.join(status['bind_paths']['missing'])}")
        else:
            print("  Missing (0): None")
        
        # Environment variables section
        print("\nEnvironment Variables:")
        print(f"  Required ({len(status['environment_variables']['required'])}): {', '.join(status['environment_variables']['required'])}")
        print(f"  Provided ({len(status['environment_variables']['provided'])}): {', '.join(status['environment_variables']['provided'])}")
        
        if status['environment_variables']['missing']:
            print(f"  Missing ({len(status['environment_variables']['missing'])}): {', '.join(status['environment_variables']['missing'])}")
        else:
            print("  Missing (0): None")
        
        # Command status section
        print("\nExecution Command:")
        if status['command']['is_set']:
            print(f"  Status: ✅ Command is set")
            print(f"  Command: {status['command']['value']}")
        else:
            print(f"  Status: ❌ Command is not set")
        
        # Overall status
        print("\nOverall Status:")
        if not status['bind_paths']['missing'] and not status['environment_variables']['missing']:
            print("  Configuration: ✅ All required configuration values are provided")
        else:
            print("  Configuration: ❌ Missing required configuration values")
        
        print(f"=== End of Configuration Status ===\n")
    
    def check_configuration_complete(self) -> bool:
        """
        Check if all required bind paths and environment variables have values.
        
        Returns:
            bool: True if all required values are provided, False otherwise
        """
        status = self.get_configuration_status()
        return not status['bind_paths']['missing'] and not status['environment_variables']['missing']
    
    def generate_command(self) -> str:
        """
        Generate the execution command for the process.
        
        This method will generate the appropriate command based on the execution mode
        and scheduler, using the scripts available in the process directory.
        The generated command is stored in the exec_command field.
        
        Returns:
            str: The generated command
            
        Raises:
            ValueError: If any required bind path or environment variable is missing
            FileNotFoundError: If the required script is not found
        """
        # Check if all required values are provided
        if not self.check_configuration_complete():
            status = self.get_configuration_status()
            missing_binds = status['bind_paths']['missing']
            missing_envs = status['environment_variables']['missing']
            
            error_msg = "Cannot generate command: missing required configuration values.\n"
            
            if missing_binds:
                error_msg += f"Missing bind paths: {', '.join(missing_binds)}\n"
            
            if missing_envs:
                error_msg += f"Missing environment variables: {', '.join(missing_envs)}\n"
            
            error_msg += "Use print_configuration_status() to see the full configuration status."
            raise ValueError(error_msg)
        
        #! Determine the execution mode - for now, let us choose container even if the image does not exist
        # mode = self.determine_execution_mode()
        mode = ExecutionMode.CONTAINER

        location: str = "local" if self.scheduler == HPCScheduler.LOCAL else "hpc"
        cmd_prefix: str | None = None
        script_args: str = ""

        # Get the script path based on execution environment
        if location == "local":
            cmd_prefix = "source"
            script_path: str = self.process.process_dir.script_paths["execute"]["local"][self.execution_mode]
        else:
            if self.scheduler == HPCScheduler.LSF:
                cmd_prefix = "bsub <"
            elif self.scheduler == HPCScheduler.SLURM:
                cmd_prefix = "sbatch"
            elif self.scheduler == HPCScheduler.PBS:
                cmd_prefix = "qsub"
            script_path: str = self.process.process_dir.script_paths["execute"]["hpc"][self.scheduler][self.execution_mode]

        # Add arguments to the script - the script itself will handle container execution
        # Pass bind path and environment variable arguments that the script will use
        
        # Add bind path arguments
        for bind_path, value in self.bind_path_values.items():
            # For bind paths, we need to handle the format correctly
            # The key is whether we need to quote the entire argument or just the path value
            needs_quoting = " " in str(value) or (isinstance(value, str) and any(c in value for c in "*?[](){}|&;<>"))
            
            if needs_quoting:
                # Quote just the value part to preserve shell interpretation
                script_args += f" --bind {bind_path}='{value}'"
            else:
                # No special characters that need quoting
                script_args += f" --bind {bind_path}={value}"
        
        # Add environment variable arguments
        for env_var, value in self.env_var_values.items():
            if value is None:
                continue
            
            # Special handling for JSON values
            if isinstance(value, str) and (value.startswith('{') or value.startswith('[')) and ('"' in value):
                # For JSON, need to escape double quotes and wrap in single quotes
                # Single quotes provide the best protection against shell interpretation
                script_args += f" --env '{env_var}={value}'"
                
            # Handle values with spaces or special shell characters
            elif isinstance(value, str) and (" " in value or any(c in value for c in "*?[](){}|&;<>\\")):
                # Use single quotes for values with spaces or special chars
                # Single quotes prevent all shell interpretation
                script_args += f" --env '{env_var}={value}'"
            else:
                # Simple values without spaces or special chars
                script_args += f" --env {env_var}={value}"
        
        # Construct the final command
        cmd = f"{cmd_prefix} {script_path}{script_args}"
        
        # Store the generated command in the exec_command field
        self.exec_command = cmd
        
        # Try to save the updated model to disk
        try:
            self.save_to_disk()
        except Exception as e:
            # Don't raise an exception if saving fails - just continue
            print(f"Warning: Failed to save execution model after generating command: {e}")
        
        return cmd
    
    def execute(self) -> subprocess.CompletedProcess:
        """
        Execute the generated command.
        
        Returns:
            subprocess.CompletedProcess: The result of the command execution
            
        Raises:
            ValueError: If any required bind path or environment variable is missing
            RuntimeError: If the command execution fails
        """
        # Use the stored command if available, or generate a new one
        cmd = self.exec_command if self.exec_command else self.generate_command()
        
        # Execute the command
        try:
            # Save the execution to disk before running
            self.save_to_disk()
            
            # Run the command and capture output
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command execution failed: {e.stderr}")
    
    def dry_run(self) -> Dict[str, Any]:
        """
        Perform a dry run of the execution, returning information about the command
        that would be executed.
        
        Returns:
            Dict[str, Any]: Information about the dry run
        """
        # Get configuration status
        config_status = self.get_configuration_status()
        config_complete = self.check_configuration_complete()
        
        # # Try to determine the execution mode
        # mode = self.determine_execution_mode()
        
        # Map execution mode to script key suffix
        mode_suffix = "container" if self.execution_mode == ExecutionMode.CONTAINER else "venv"
        
        # Map scheduler to script key prefix
        if self.scheduler == HPCScheduler.LOCAL:
            scheduler_prefix = "execute_local"
        else:
            scheduler_prefix = f"execute_{self.scheduler.value}"
        
        # Construct the script key
        script_key = f"{scheduler_prefix}_{mode_suffix}"
        
        # Check if script exists
        script_exists = (self.process.script_paths is not None and 
                        script_key in self.process.script_paths)
        
        # Prepare the result
        result = {
            "exec_id": self.exec_id,
            "process_id": self.process.process_id,
            "execution_mode": self.execution_mode.value,
            "scheduler": self.scheduler.value,
            "script_key": script_key,
            "script_exists": script_exists,
            "bind_paths": {
                "values": self.bind_path_values,
                "missing": config_status["bind_paths"]["missing"]
            },
            "environment_variables": {
                "values": self.env_var_values,
                "missing": config_status["environment_variables"]["missing"]
            },
            "configuration_complete": config_complete,
            "exec_command": self.exec_command
        }
        
        # Try to generate command if configuration is complete
        if config_complete:
            try:
                result["command"] = self.generate_command()
            except Exception as e:
                result["command_error"] = str(e)
        else:
            result["command_error"] = "Cannot generate command: missing required configuration values"
        
        return result
    
    def save_to_disk(self) -> Path:
        """
        Save the NeuProcessExec instance to disk.
        
        This method saves the model to the process_execs directory with the exec_id as the folder name.
        
        Returns:
            Path to the saved model.json file
        """
        from ....utils.constants import PATHS
        
        # Create process_execs directory if it doesn't exist
        exec_dir = PATHS.get_process_exec_path(self.exec_id)
        exec_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the model as JSON, using our custom encoder to handle Path objects
        model_path = exec_dir / "model.json"
        with open(model_path, "w") as f:
            json.dump(self.model_dump(), f, indent=4, cls=PathEncoder)
        
        return model_path
