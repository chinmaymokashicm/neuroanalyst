#!/usr/bin/env python
"""
Example script for using NeuProcessExec.

This script demonstrates how to create and use NeuProcessExec instances
to execute NeuProcess objects with specific runtime configuration.
"""

import os
from pathlib import Path

from src.neuroanalyst.models.process import (
    NeuProcessLogic, NeuProcessDir, NeuProcess, NeuProcessExec,
    ExecutionMode, HPCScheduler
)


def example_from_process_id():
    """Example of creating a NeuProcessExec from a process ID."""
    # Assuming we have a process with ID "PR-XXXXXX"
    process_id = "PR-XXXXXX"
    
    try:
        # Create a NeuProcessExec without providing bind paths and environment variables
        process_exec = NeuProcessExec.from_process_id(
            process_id=process_id
        )
        
        # Print the current configuration status
        process_exec.print_configuration_status()
        
        # Set the required values one by one
        process_exec.set_bind_path_value("/data", "/path/to/data")
        process_exec.set_bind_path_value("/output", "/path/to/output")
        process_exec.set_env_var_value("BIDS_ROOT", "/path/to/bids")
        process_exec.set_env_var_value("PIPELINE_NAME", "test_pipeline")
        
        # Print the updated configuration status
        process_exec.print_configuration_status()
        
        # Generate and execute the command
        cmd = process_exec.generate_command()
        print(f"Generated command: {cmd}")
        
        # Execute the command
        result = process_exec.execute()
        print(f"Execution successful: {result.stdout}")
    except FileNotFoundError:
        print("Process ID not found")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except RuntimeError as e:
        print(f"Execution failed: {e}")


def example_from_process(process: NeuProcess):
    """Example of creating a NeuProcessExec from a NeuProcess."""
    # Create a NeuProcessExec from the NeuProcess
    process_exec = NeuProcessExec(
        process=process,
        bind_path_values={
            "/data": "/path/to/data",
            "/output": "/path/to/output"
        },
        env_var_values={
            "BIDS_ROOT": "/path/to/bids",
            "PIPELINE_NAME": "test_pipeline"
        }
    )
    
    # Perform a dry run to get information about the execution
    dry_run_info = process_exec.dry_run()
    print(f"Dry run information: {dry_run_info}")


def example_path_normalization(process: NeuProcess):
    """Example of using path normalization with NeuProcessExec."""
    print("\n=== Path Normalization Example ===")
    
    # Create a NeuProcessExec with minimal configuration
    process_exec = NeuProcessExec(
        process=process
    )
    
    # Print the required bind paths
    print(f"Required bind paths: {process.bind_paths}")
    
    # Set values with and without trailing slashes
    for i, bind_path in enumerate(process.bind_paths):
        # For some paths, add a trailing slash to demonstrate normalization
        path_to_set = bind_path
        if i % 2 == 0 and not bind_path.endswith('/'):  # For even indices without trailing slash
            path_to_set = f"{bind_path}/"
            print(f"Setting bind path with trailing slash: {path_to_set}")
        else:
            print(f"Setting bind path as-is: {path_to_set}")
            
        value = f"/path/to/{bind_path.strip('/')}"
        process_exec.set_bind_path_value(path_to_set, value)
    
    # Check that all bind paths are properly set
    print("\nBind path values:")
    for path, value in process_exec.bind_path_values.items():
        print(f"  {path} = {value}")
    
    # Print configuration status to verify all paths are recognized
    process_exec.print_configuration_status()
    
    print("=== End of Path Normalization Example ===\n")


if __name__ == "__main__":
    # Example usage
    try:
        example_from_process_id()
    except FileNotFoundError:
        print("Process ID not found, skipping example_from_process_id()")
    
    # The examples below require an actual NeuProcess instance
    # They are included for documentation purposes only
    # 
    # process = NeuProcess.from_process_id("PR-XXXXXX")
    # example_from_process(process)
    # example_dynamic_configuration(process)
