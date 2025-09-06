#!/usr/bin/env python
"""
Example script demonstrating the creation and execution of a NeuPipeline.

This script shows how to:
1. Create NeuProcessExec instances
2. Organize them into NeuPipelineSteps
3. Create a NeuPipeline
4. Generate the pipeline execution script
5. Execute the pipeline
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import the neuroanalyst package
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.neuroanalyst.models.about import About
from src.neuroanalyst.models.process.exec.core import NeuProcessExec, HPCScheduler
from src.neuroanalyst.models.process.process.core import NeuProcess
from src.neuroanalyst.models.pipeline.core import NeuPipeline, NeuPipelineStep
from src.neuroanalyst.utils.constants import NeuroAnalystPaths


def main():
    """Main function to demonstrate the NeuPipeline class."""
    # Get NeuProcessExec instances
    # In a real scenario, these would be created from actual NeuProcess instances
    # For this example, we'll use mock instances
    print("Creating NeuProcessExec instances...")
    process_exec1 = NeuProcessExec(
        exec_id="PE-123456",
        process=None,  # In a real scenario, this would be a NeuProcess instance
        bind_paths_values={},
        env_vars_values={}
    )
    process_exec1.generate_command = lambda: "echo 'Running process 1'"
    
    process_exec2 = NeuProcessExec(
        exec_id="PE-234567",
        process=None,  # In a real scenario, this would be a NeuProcess instance
        bind_paths_values={},
        env_vars_values={}
    )
    process_exec2.generate_command = lambda: "echo 'Running process 2'"
    
    process_exec3 = NeuProcessExec(
        exec_id="PE-345678",
        process=None,  # In a real scenario, this would be a NeuProcess instance
        bind_paths_values={},
        env_vars_values={}
    )
    process_exec3.generate_command = lambda: "echo 'Running process 3'"
    
    # Create pipeline steps
    print("Creating pipeline steps...")
    step1 = NeuPipelineStep(
        name="Preprocessing",
        description="Data preprocessing step",
        process_execs=[process_exec1]
    )
    
    step2 = NeuPipelineStep(
        name="Processing",
        description="Data processing step",
        process_execs=[process_exec2, process_exec3]  # These will run in parallel
    )
    
    # Create pipeline
    print("Creating pipeline...")
    pipeline = NeuPipeline(
        name="Example Pipeline",
        description="An example pipeline to demonstrate the NeuPipeline class",
        version="0.1.0",
        about=About(
            name="Example User",
            email="example@example.com",
            organization="Example Organization"
        ),
        steps=[step1, step2],
        scheduler=HPCScheduler.LOCAL  # Use local execution for this example
    )
    
    # Create pipeline directory and generate execution script
    print("Creating pipeline directory and generating execution script...")
    pipeline_dir = pipeline.create_pipeline_dir()
    print(f"Pipeline directory created at: {pipeline_dir}")
    print(f"Pipeline ID: {pipeline.pipeline_id}")
    
    # Print the path to the execution script
    print(f"Execution script generated at: {pipeline.script_path}")
    
    # In a real scenario, the pipeline would be executed like this:
    # result = pipeline.execute()
    # print(result)
    
    # For this example, we'll just print a message
    print("To execute the pipeline, run the following command:")
    print(f"bash {pipeline.script_path}")


if __name__ == "__main__":
    main()
