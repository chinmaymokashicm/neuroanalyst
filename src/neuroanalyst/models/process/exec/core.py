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
from bids import BIDSLayout

from ....utils.constants import NeuroAnalystPaths
from ....utils.id_generators import generate_process_exec_id
from ....utils.bids import split_by_subject_session
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


BASH_SCRIPT_NAME: str = "bash_script.sh"

class NeuProcessExec(BaseModel):
    """
    NeuProcessExec - Class representing an execution instance of a NeuProcess.
    
    This class handles:
    1. Execution of a NeuProcess with specific runtime configuration
    2. Generation of execution commands based on environment and mode
    3. Validation of bind paths and environment variables
    4. Execution of the generated commands
    
    A NeuProcessExec can be created from a NeuProcess, a process ID, or a path to a process directory.
    
    Scheduler flags can be set dynamically using the scheduler_flags field. Common flags include:
    - LSF: queue, mem, time, nodes, etc.
    - SLURM: partition, mem, time, cpus-per-task, etc.
    - PBS: queue, mem, walltime, nodes, etc.
    """
    # Basic information
    exec_id: str = Field(default_factory=generate_process_exec_id, 
                        description="Unique identifier for the execution instance")
    
    process: NeuProcess = Field(description="NeuProcess to execute")
    
    # Runtime configuration
    bind_path_values: Dict[str, str] = Field(default_factory=dict,
                                          description="Values for bind paths, keyed by bind path name")
    env_var_values: Dict[str, str] = Field(default_factory=dict,
                                         description="Values for environment variables, keyed by variable name")
    command_flags: Optional[List[str]] = Field(default=None,
                                                description="Additional command-line flags for the process. E.g., ['--verbose', '--fakeroot']")
    scheduler_flags: Dict[str, int | float | str] = Field(default_factory=dict,
                                         description="Scheduler-specific flags to pass to the scheduler command. E.g., {'queue': 'normal', 'mem': '4GB'}")
    
    # Execution options
    execution_mode: ExecutionMode = Field(default=ExecutionMode.CONTAINER,
                                        description="Mode of execution (venv, container, auto)")
    scheduler: HPCScheduler = Field(default=HPCScheduler.LSF,
                                  description="HPC scheduler to use (lsf, slurm, pbs, none)")

    # Command storage
    script_path: Optional[Path] = Field(default=None,
                                        description="Path to the script file")
    exec_command: Optional[str] = Field(default=None,
                                      description="Generated execution command")
    
    # Class variables
    
    @property
    def username(self) -> Optional[str]:
        """Get the username associated with the process, if any."""
        return self.process.username
    
    @property
    def bids_filters(self) -> Dict[str, Any]:
        """Get the BIDS filters from the environment variable values."""
        bids_filters_str: Optional[str] = self.env_var_values.get("BIDS_FILTERS")
        if bids_filters_str:
            try:
                return json.loads(bids_filters_str)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for BIDS_FILTERS environment variable")
        return {}
    
    @property
    def exec_log_dir(self) -> Path:
        """Get the path to the execution log directory."""
        log_dir: Path = Path(NeuroAnalystPaths(username=self.username).logs) / "process_execs" / self.exec_id
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    @property
    def exec_log_path(self) -> Path:
        """Get the path to the execution log file."""
        return self.exec_log_dir / f"{self.exec_id}.log"
    
    @property
    def exec_error_path(self) -> Path:
        """Get the path to the execution error file."""
        return self.exec_log_dir / f"{self.exec_id}.err"

    @property
    def is_fully_configured(self) -> bool:
        """
        Check if all required bind paths and environment variables have values.
        
        Returns:
            bool: True if all required values are provided, False otherwise
        """
        missing_bind_paths = [path for path in self.process.bind_paths if path not in self.bind_path_values]
        missing_env_vars = [var for var in self.process.environment_variables if var not in self.env_var_values]
        return len(missing_bind_paths) == 0 and len(missing_env_vars) == 0
    
    @classmethod
    def generate_from_process(cls, process: NeuProcess, **kwargs) -> "NeuProcessExec":
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
    def generate_from_process_id(cls, process_id: str, username: Optional[str] = None, **kwargs) -> "NeuProcessExec":
        """
        Create a NeuProcessExec from a process ID.
        
        Args:
            process_id: Process ID
            username: Username of the process owner
            **kwargs: Additional arguments to pass to the NeuProcessExec constructor
            
        Returns:
            NeuProcessExec instance
        """
        process = NeuProcess.from_process_id(process_id, username=username)
        return cls(process=process, **kwargs)
    
    @classmethod
    def generate_from_process_dir_path(cls, dir_path: Path, **kwargs) -> "NeuProcessExec":
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
    def from_exec_id(cls, exec_id: str, username: Optional[str] = None) -> "NeuProcessExec":
        """
        Create a NeuProcessExec from a saved execution ID.
        
        Args:
            exec_id: Execution ID of a previously saved NeuProcessExec
            username: Username of the user executing the process
            
        Returns:
            NeuProcessExec instance
            
        Raises:
            FileNotFoundError: If the execution directory or model.json file does not exist
            ValueError: If the model.json file cannot be parsed
        """
        
        # Get the path to the execution directory
        paths = NeuroAnalystPaths(username=username)
        exec_dir = paths.get_process_exec_path(exec_id)
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
    
    @staticmethod
    def spawn_optimized_execs(process: NeuProcess, bids_filters: dict, bids_layout: BIDSLayout, max_chunk_size: int = 5) -> tuple[list["NeuProcessExec"], list[tuple[list[str], list[str]]]]:
        """
        Create multiple NeuProcessExec instances by splitting BIDS filters into optimized chunks.
        This method uses the split_by_subject_session function to divide the BIDS query
        into chunks that each return <= max_chunk_size files, while maintaining subject-session integrity.
        
        Args:
            process: NeuProcess instance to execute
            bids_filters: Base BIDS filters to apply (should not include 'subject' or 'session')
            bids_layout: BIDSLayout object for querying the BIDS dataset
            max_chunk_size: Maximum number of files per chunk (default: 5)
        Returns:
            tuple: (list of NeuProcessExec instances, list of subject-session pairs for each exec)
        """
        process_execs: list[NeuProcessExec] = []
        subject_session_pairs: list[tuple[list[str], list[str]]] = []
        for chunk in split_by_subject_session(bids_layout=bids_layout, bids_filters=bids_filters, max_chunk_size=max_chunk_size):
            if chunk["n_files"] == 0:
                print(f"Warning: No files found for the given BIDS filters ( {bids_filters} ) chunk. Skipping this chunk.")
                continue
            bids_filters: dict = chunk["bids_filters"]
            subject_session_pairs.append(chunk["subject_session_pair"])
            process_exec: NeuProcessExec = NeuProcessExec.generate_from_process(process)
            process_exec.env_var_values["BIDS_FILTERS"] = json.dumps(bids_filters)
            process_execs.append(process_exec)
        return process_execs, subject_session_pairs

    def __str__(self) -> str:
        """Return a human-readable string representation of the NeuProcessExec."""
        process_id: str = self.process.process_id if hasattr(self, 'process') else 'unknown'
        process_exec_id: str = self.exec_id if hasattr(self, 'exec_id') else 'unknown'

        return f"NeuProcessExec(id='{process_exec_id}', process_id='{process_id}')"

    def __repr__(self) -> str:
        """Return a detailed string representation of the NeuProcessExec."""
        scheduler = getattr(self, 'scheduler', 'unknown')
        mode = getattr(self, 'execution_mode', 'unknown')
        
        return f"NeuProcessExec(id='{getattr(self, 'exec_id', 'unknown')}', "\
               f"process_id='{getattr(self.process, 'process_id', 'unknown') if hasattr(self, 'process') else 'unknown'}', "\
               f"mode='{mode}', scheduler='{scheduler}')"
               
    def delete(self) -> None:
        """
        Delete the NeuProcessExec directory and all its contents from disk.
        
        Raises:
            FileNotFoundError: If the execution directory does not exist
            Exception: If deletion fails for any reason
        """
        exec_dir: Path = Path(NeuroAnalystPaths(username=self.username).get_process_exec_path(self.exec_id))
        if not exec_dir.exists():
            print(f"Execution directory not found: {exec_dir}")
            return
        
        try:
            # Recursively delete the execution directory
            for item in exec_dir.iterdir():
                if item.is_dir():
                    for subitem in item.rglob('*'):
                        if subitem.is_file():
                            subitem.unlink()
                    item.rmdir()
                else:
                    item.unlink()
            exec_dir.rmdir()
        except Exception as e:
            raise Exception(f"Failed to delete NeuProcessExec directory: {e}")
    
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
            
    def set_scheduler_flag(self, flag: str, value: str) -> None:
        """
        Set a scheduler flag. These flags will be passed to the scheduler command
        (bsub, sbatch, qsub) when executing the process.
        
        Args:
            flag: Flag name (e.g., 'queue', 'mem', 'time', etc.)
            value: Flag value
            
        Examples:
            # LSF
            set_scheduler_flag('queue', 'normal')
            set_scheduler_flag('mem', '4GB')
            
            # SLURM
            set_scheduler_flag('partition', 'normal')
            set_scheduler_flag('mem', '4G')
            
            # PBS
            set_scheduler_flag('queue', 'batch')
            set_scheduler_flag('l mem', '4gb')
        """
        self.scheduler_flags[flag] = value
            
    def set_scheduler_flags(self, flags: Dict[str, str]) -> None:
        """
        Set multiple scheduler flags at once.
        
        Args:
            flags: Dictionary of flag names and values
            
        Examples:
            # LSF
            set_scheduler_flags({'queue': 'normal', 'mem': '4GB', 'time': '1:00'})
            
            # SLURM
            set_scheduler_flags({'partition': 'normal', 'mem': '4G', 'time': '01:00:00'})
            
            # PBS
            set_scheduler_flags({'queue': 'batch', 'l mem': '4gb', 'l walltime': '1:00:00'})
        """
        self.scheduler_flags.update(flags)
    
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
            "scheduler_flags": {
                "provided": self.scheduler_flags
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
            
        # Scheduler flags section
        print("\nScheduler Flags:")
        if status['scheduler_flags']['provided']:
            print(f"  Provided ({len(status['scheduler_flags']['provided'])}): {', '.join([f'{k}={v}' for k, v in status['scheduler_flags']['provided'].items()])}")
        else:
            print("  Provided (0): None")
        
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
    
    def generate_script_args_str(self, include_newlines: bool = True) -> str:
        """
        Generate the script arguments string for bind paths and environment variables.
        
        Returns:
            str: The generated script arguments string
        """
        script_args: str = ""
        # Add bind path arguments
        for bind_path, value in self.bind_path_values.items():
            # For bind paths, we need to handle the format correctly
            # The key is whether we need to quote the entire argument or just the path value
            needs_quoting = " " in str(value) or (isinstance(value, str) and any(c in value for c in "*?[](){}|&;<>"))
            
            if needs_quoting:
                # Quote just the value part to preserve shell interpretation
                if include_newlines:
                    script_args += f" \\\n  --bind {bind_path}='{value}'"
                else:
                    script_args += f" --bind {bind_path}='{value}'"
            else:
                # No special characters that need quoting
                if include_newlines:
                    script_args += f" \\\n  --bind {bind_path}={value}"
                else:
                    script_args += f" --bind {bind_path}={value}"
        
        # Add environment variable arguments
        for env_var, value in self.env_var_values.items():
            if value is None:
                continue
            
            # Special handling for JSON values - must be properly quoted to ensure they're passed correctly
            if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                # Ensure the JSON is properly formatted
                try:
                    # Validate that it's proper JSON by parsing it
                    json_obj = json.loads(value)
                    # Re-serialize with properly escaped quotes for shell
                    # json_str = json.dumps(json_obj).replace('"', '\\"')
                    json_str = json.dumps(json_obj)
                    # Use double quotes for the whole argument to preserve the JSON structure
                    if include_newlines:
                        script_args += f" \\\n  --env {env_var}='{json_str}'"
                    else:
                        script_args += f" --env {env_var}='{json_str}'"
                except json.JSONDecodeError:
                    # If it's not valid JSON, treat it as a regular string with special characters
                    if include_newlines:
                        script_args += f" \\\n  --env '{env_var}={value}'"
                    else:
                        script_args += f" --env '{env_var}={value}'"

            # Handle values with spaces or special shell characters
            elif isinstance(value, str) and (" " in value or any(c in value for c in "*?[](){}|&;<>\\")):
                # Use single quotes for values with spaces or special chars
                # Single quotes prevent all shell interpretation
                if include_newlines:
                    script_args += f" \\\n  --env '{env_var}={value}'"
                else:
                    script_args += f" --env '{env_var}={value}'"
            else:
                # Simple values without spaces or special chars
                if include_newlines:
                    script_args += f" \\\n  --env {env_var}={value}"
                else:
                    script_args += f" --env {env_var}={value}"
                    
        # Add command flags
        command_flags = self.command_flags or []
        
        # If process has command flags and they're not overridden by exec, use those instead
        if not command_flags and self.process and self.process.command_flags:
            command_flags = self.process.command_flags
            
        for flag in command_flags:
            # Ensure flag starts with '--'
            if not flag.startswith('-'):
                flag = f"--{flag}"
            elif flag.startswith('-') and not flag.startswith('--') and len(flag) > 2:
                flag = f"--{flag[1:]}"
                
            if include_newlines:
                script_args += f" \\\n  {flag}"
            else:
                script_args += f" {flag}"

        return script_args

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

        location: str = "local" if self.scheduler == HPCScheduler.LOCAL else "hpc"
        cmd_prefix: str | None = None
        script_args: str = ""

        # Get the script path based on execution environment
        # All execution scripts are now in the execute directory directly
        self.script_path: str = self.process.process_dir.script_paths["execute"][self.execution_mode]
        
        if location == "local":
            cmd_prefix = "source"
        else:
            # Set appropriate scheduler command
            if self.scheduler == HPCScheduler.LSF:
                cmd_prefix = "bsub"
            elif self.scheduler == HPCScheduler.SLURM:
                cmd_prefix = "sbatch"
            elif self.scheduler == HPCScheduler.PBS:
                cmd_prefix = "qsub"

        # Add arguments to the script - the script itself will handle container execution
        # Pass bind path and environment variable arguments that the script will use

        # Generate the bash script if not already set and save to disk
        exec_dir: Path = Path(NeuroAnalystPaths(username=self.username).process_execs) / self.exec_id
        # if not Path(exec_dir / BASH_SCRIPT_NAME).exists():
        #     bash_script_with_runtime_args_path: str = str(self.generate_and_save_bash_script())
        # else:
        #     bash_script_with_runtime_args_path: str = str(exec_dir / BASH_SCRIPT_NAME)
        bash_script_with_runtime_args_path, _ = self.generate_bash_script()
        
        # Construct the final command. Include creation of log directory if it doesn't exist within the command.
        if self.scheduler == HPCScheduler.LOCAL:
            cmd = "mkdir -p " + str(self.exec_log_dir) + " && "
            cmd += f"{cmd_prefix} {bash_script_with_runtime_args_path} > {self.exec_log_path} 2> {self.exec_error_path}"
        elif self.scheduler == HPCScheduler.LSF:
            cmd = "mkdir -p " + str(self.exec_log_dir) + " && "
            cmd += f"{cmd_prefix} -o {self.exec_log_path} -e {self.exec_error_path} -J {self.exec_id}{self._format_lsf_flags()} {bash_script_with_runtime_args_path}"
        elif self.scheduler == HPCScheduler.SLURM:
            cmd = "mkdir -p " + str(self.exec_log_dir) + " && "
            cmd += f"{cmd_prefix} --output={self.exec_log_path} --error={self.exec_error_path}{self._format_slurm_flags()} {bash_script_with_runtime_args_path}"
        elif self.scheduler == HPCScheduler.PBS:
            cmd = "mkdir -p " + str(self.exec_log_dir) + " && "
            cmd += f"{cmd_prefix} -o {self.exec_log_path} -e {self.exec_error_path}{self._format_pbs_flags()} {bash_script_with_runtime_args_path}"
        else:
            raise ValueError(f"Unsupported scheduler: {self.scheduler}")
        
        # Store the generated command in the exec_command field
        self.exec_command = cmd
        
        return cmd
    
    def _format_lsf_flags(self) -> str:
        """
        Format scheduler flags for LSF.
        
        Returns:
            str: Formatted LSF flags
        """
        flag_str = ""
        for key, value in self.scheduler_flags.items():
            # Common LSF flags and their corresponding formats
            if key == "queue" or key == "q":
                flag_str += f" -q {value}"
            elif key == "mem" or key == "M":
                flag_str += f" -M {value}"
            elif key == "time" or key == "W":
                flag_str += f" -W {value}"
            elif key == "n" or key == "nodes":
                flag_str += f" -n {value}"
            elif key == "R":
                flag_str += f" -R {value}"
            elif key == "P" or key == "project":
                flag_str += f" -P {value}"
            else:
                # For any other flags, format as -flag value, preserving any existing hyphens
                prefix = "" if key.startswith("-") else "-"
                flag_str += f" {prefix}{key} {value}"
        return flag_str
        
    def _format_slurm_flags(self) -> str:
        """
        Format scheduler flags for SLURM.
        
        Returns:
            str: Formatted SLURM flags
        """
        flag_str = ""
        for key, value in self.scheduler_flags.items():
            # Common SLURM flags and their corresponding formats
            if key == "partition" or key == "p":
                flag_str += f" --partition={value}"
            elif key == "mem":
                flag_str += f" --mem={value}"
            elif key == "time" or key == "t":
                flag_str += f" --time={value}"
            elif key == "cpus-per-task" or key == "c":
                flag_str += f" --cpus-per-task={value}"
            elif key == "nodes" or key == "N":
                flag_str += f" --nodes={value}"
            elif key == "ntasks" or key == "n":
                flag_str += f" --ntasks={value}"
            elif key == "account" or key == "A":
                flag_str += f" --account={value}"
            elif key == "qos":
                flag_str += f" --qos={value}"
            else:
                # For any other flags, format as --flag=value
                if key.startswith("--"):
                    # Already has double dash prefix
                    flag_str += f" {key}={value}"
                elif key.startswith("-"):
                    # Has single dash prefix, add one more dash
                    flag_str += f" -{key}={value}"
                else:
                    # No dash prefix, add double dash
                    flag_str += f" --{key}={value}"
        return flag_str
        
    def _format_pbs_flags(self) -> str:
        """
        Format scheduler flags for PBS/Torque.
        
        Returns:
            str: Formatted PBS flags
        """
        flag_str = ""
        for key, value in self.scheduler_flags.items():
            # Common PBS flags and their corresponding formats
            if key == "queue" or key == "q":
                flag_str += f" -q {value}"
            elif key == "walltime" or key == "l walltime":
                flag_str += f" -l walltime={value}"
            elif key == "mem" or key == "l mem":
                flag_str += f" -l mem={value}"
            elif key == "nodes" or key == "l nodes":
                flag_str += f" -l nodes={value}"
            elif key == "ppn" or key == "l ppn":
                flag_str += f" -l ppn={value}"
            elif key == "A" or key == "account":
                flag_str += f" -A {value}"
            elif key.startswith("l "):
                # For other PBS resource flags
                resource = key.replace("l ", "")
                flag_str += f" -l {resource}={value}"
            else:
                # For any other flags, format as -flag value, preserving any existing hyphens
                prefix = "" if key.startswith("-") else "-"
                flag_str += f" {prefix}{key} {value}"
        return flag_str
    
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
            "scheduler_flags": {
                "values": self.scheduler_flags
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
    
    def generate_bash_script(self) -> tuple[Path, str]:
        """
        Generate the bash script for executing the process with the current configuration.
        
        Returns:
            tuple: (Path to the bash script, bash script content as a string)
        """
        
        # Create process_execs directory if it doesn't exist
        exec_dir = Path(NeuroAnalystPaths(username=self.username).process_execs) / self.exec_id
        
        exec_dir.mkdir(parents=True, exist_ok=True)
        
        script_args_str = self.generate_script_args_str()
        
        script_str: str = f"""#!/bin/bash
bash {self.script_path} {' '.join(self.command_flags) if self.command_flags else ''} \\
    {script_args_str}
        """
        
        script_path = exec_dir / BASH_SCRIPT_NAME
        
        return script_path, script_str
    
    def save_to_disk(self) -> Path:
        """
        Save the NeuProcessExec instance to disk.
        
        This method saves the model to the process_execs directory with the exec_id as the folder name.
        
        Returns:
            Path to the saved model.json file
        """
        
        # Create process_execs directory if it doesn't exist
        exec_dir = Path(NeuroAnalystPaths(username=self.username).process_execs) / self.exec_id
        
        exec_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the model as JSON, using our custom encoder to handle Path objects
        model_path = exec_dir / "model.json"
        with open(model_path, "w") as f:
            json.dump(self.model_dump(), f, indent=4, cls=PathEncoder)
            
        # Save the bash script to disk
        bash_script_path, bash_script_str = self.generate_bash_script()
        with open(bash_script_path, "w") as f:
            f.write(bash_script_str)

        os.chmod(bash_script_path, 0o755) # Make the script executable
        
        return model_path
