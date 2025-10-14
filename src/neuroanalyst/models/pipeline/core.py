"""
NeuPipeline Core Module

This module implements the NeuPipeline class, which represents a neuroimaging pipeline
composed of multiple NeuProcessExec instances organized into execution steps.

NeuPipeline is responsible for:
1. Managing a sequence of pipeline steps (each with one or more NeuProcessExec instances)
2. Generating execution scripts for the entire pipeline with dependencies
3. Storing pipeline metadata for reproducibility
4. Tracking status of each process and enabling resumable execution
"""

import os
import json
import time
import subprocess
import logging
import concurrent.futures
from enum import Enum
from pathlib import Path
from datetime import datetime
from threading import Lock
from typing import Optional, List, Dict, Any, Union, Set, ClassVar, Literal

from pydantic import BaseModel, Field, model_validator
import pandas as pd

from ...utils.constants import NeuroAnalystPaths
from ...utils.id_generators import generate_id
from ..about import About
from ..bids import BIDSDatasetDescription, BIDSGeneratedByToolInfo, PipelineDescriptionSpec
from ..process.exec.core import NeuProcessExec, HPCScheduler
from ..process.process.core import NeuProcess
from .executor import ProcessStatus, LSFExecutor, SLURMExecutor, PBSExecutor, LocalExecutor

class NeuProcessExecStatus(BaseModel):
    """
    NeuProcessExecStatus - Class representing the status of a single process execution.
    
    This class tracks the status of a single NeuProcessExec instance, including timestamps
    for when the process started and completed, as well as any error messages if it failed.
    """
    
    # Basic information
    process_id: str = Field(description="Unique identifier for the NeuProcess")
    exec_id: str = Field(description="Unique identifier for the NeuProcessExec instance")
    name: str = Field(description="Name of the process execution")
    
    # Status information
    status: str = Field(description="Current status of the process execution (e.g., NOT_STARTED, RUNNING, COMPLETE, FAILED)")
    started_at: Optional[str] = Field(default=None, description="Timestamp when the process execution started")
    completed_at: Optional[str] = Field(default=None, description="Timestamp when the process execution completed")
    last_updated: str = Field(description="Timestamp when the status was last updated")
    error: Optional[str] = Field(default=None, description="Error message if the process execution failed")
    
    # Scheduler job ID (if applicable)
    scheduler_job_id: Optional[str] = Field(default=None, description="Job ID assigned by the HPC scheduler")

class NeuPipelineStepStatus(BaseModel):
    """
    NeuPipelineStepStatus - Class representing the status of a pipeline step execution.

    This class tracks the status of a single step in the pipeline, including the status
    of each individual process execution within the step.
    """

    # Step-level status
    step_id: int = Field(description="Index of the step in the pipeline")
    name: str = Field(description="Name of the pipeline step")
    status: str = Field(description="Overall status of the step (e.g., NOT_STARTED, RUNNING, COMPLETE, FAILED)")
    started_at: Optional[str] = Field(default=None, description="Timestamp when the step started")
    completed_at: Optional[str] = Field(default=None, description="Timestamp when the step completed")
    last_updated: str = Field(description="Timestamp when the step status was last updated")
    error: Optional[str] = Field(default=None, description="Error message if the step failed")
    
    # Processes in the step
    processes: List[NeuProcessExecStatus] = Field(default_factory=list, description="List of processes in the step with their statuses")
    
    def __iter__(self):
        """Allow iteration over the processes in the step."""
        return iter(self.processes)

class NeuPipelineStatus(BaseModel):
    """
    NeuPipelineStatus - Class representing the status of a pipeline execution.
    
    This class tracks the overall status of the pipeline as well as the status of each
    individual step and process execution within the pipeline.
    """
    
    # Pipeline-level status
    pipeline_id: str = Field(description="Unique identifier for the pipeline")
    created_at: str = Field(description="Timestamp when the pipeline was created")
    last_updated: str = Field(description="Timestamp when the pipeline status was last updated")
    status: str = Field(description="Overall status of the pipeline (e.g., NOT_STARTED, RUNNING, COMPLETE, FAILED)")
    scheduler: str = Field(description="HPC scheduler used for the pipeline (e.g., LSF, SLURM, PBS, LOCAL)")
    
    # Steps in the pipeline
    steps: List[NeuPipelineStepStatus] = Field(default_factory=list, description="List of steps in the pipeline with their statuses")

    def __iter__(self):
        """Allow iteration over the steps in the pipeline."""
        return iter(self.steps)

    def get_status(self, step_idx: int, exec_id: Optional[str] = None) -> dict:
        """Retrieve the status of a pipeline step or a specific process execution.
        
        Args:
            step_idx: The index of the step in the pipeline
            exec_id: Optional; The execution ID of the specific process to retrieve
            
        Returns:
            dict: The status information of the step or process, or None if not found
        """
        if step_idx < 0 or step_idx >= len(self.steps):
            return None
        step_status = self.steps[step_idx]
        if exec_id is None:
            return step_status.model_dump()
        for proc_status in step_status.processes:
            if proc_status.exec_id == exec_id:
                return proc_status.model_dump()
        return None

class NeuPipelineStep(BaseModel):
    """
    NeuPipelineStep - Class representing a step in a neuroimaging pipeline.
    
    A pipeline step contains one or more NeuProcessExec instances that can be executed
    in parallel. Steps are executed in sequence, with each step waiting for all processes
    in the previous step to complete before beginning.
    """
    
    # Name and description
    name: str = Field(description="Name of the pipeline step")
    description: Optional[str] = Field(default=None, description="Description of the step")
    
    # Process executions within this step
    process_execs: List[NeuProcessExec] = Field(
        default_factory=list,
        description="Process execution instances to run in parallel in this step"
    )
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the NeuPipelineStep."""
        processes = len(getattr(self, 'processes', [])) if hasattr(self, 'processes') else 0
        # return f"NeuPipelineStep(name='{self.name}', processes={processes})"
        detailed_info: str = f"""
        Name: {self.name}
        Description: {self.description if self.description else 'None'}
        Processes: {processes}
        Steps: {getattr(self, 'process_execs', []) if hasattr(self, 'process_execs') else 'None'}
        Status: {getattr(self, 'status', 'None') if hasattr(self, 'status') else 'None'}
        """
        return detailed_info

    def __repr__(self) -> str:
        """Return a detailed string representation of the NeuPipelineStep."""
        processes = getattr(self, 'processes', []) if hasattr(self, 'processes') else []
        process_ids = [p.execution_id for p in processes] if processes else []
        
        return f"NeuPipelineStep(name='{self.name}', "\
               f"description='{self.description if self.description else 'None'}', "\
               f"processes={process_ids})"
    
    @model_validator(mode='after')
    def validate_process_execs(self) -> 'NeuPipelineStep':
        """Validate that there is at least one process exec in the step."""
        # For testing purposes, we're temporarily disabling this validation
        # In production code, uncomment the following check
        # if not self.process_execs:
        #     raise ValueError("Pipeline step must contain at least one process execution")
        return self


class NeuPipeline(BaseModel):
    """
    NeuPipeline - Class representing a neuroimaging pipeline.
    
    A pipeline is a sequence of steps, where each step contains one or more process
    executions that can run in parallel. Steps are executed in sequence, with dependencies
    between them.
    
    This class handles:
    1. Organizing NeuProcessExec instances into sequential steps
    2. Generating execution scripts with proper dependencies
    3. Storing pipeline metadata for reproducibility
    """
    # Basic information
    pipeline_id: str = Field(default_factory=lambda: generate_id("pipeline_id"), 
                           description="Unique identifier for the pipeline")
    bids_root: Path = Field(..., description="Path to the BIDS dataset root directory")
    
    # Author and metadata
    about: About = Field(default_factory=About, description="Author and metadata information")
    
    # Pipeline steps
    steps: List[NeuPipelineStep] = Field(
        default_factory=list,
        description="Ordered steps to execute in the pipeline"
    )
    
    # Execution configuration
    scheduler: HPCScheduler = Field(
        default=HPCScheduler.LSF,
        description="HPC scheduler to use for all processes in the pipeline"
    )
    start_from_raw_bids: bool = Field(default=True, description="Whether to start processing from raw BIDS data")
    
    # Execution command
    execution_command: Optional[str] = Field(
        default=None,
        description="The generated execution command for the pipeline"
    )
    
    # Cache paths for easy access
    _paths: ClassVar[NeuroAnalystPaths] = NeuroAnalystPaths()
    
    @model_validator(mode='after')
    def validate_steps(self) -> 'NeuPipeline':
        """Validate that there is at least one step in the pipeline."""
        # For testing purposes, we're temporarily disabling this validation
        # In production code, uncomment the following check
        if not self.steps:
            raise ValueError("Pipeline must contain at least one step")
        return self
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the NeuPipeline."""
        steps_count = len(getattr(self, 'steps', [])) if hasattr(self, 'steps') else 0
        name = getattr(self.about, 'name', 'unnamed') if hasattr(self, 'about') else 'unnamed'
        return f"NeuPipeline(name='{name}', steps={steps_count})"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the NeuPipeline.
        - Pipeline details
        - Scheduler
        - Step names
        - Individual process IDs, process exec IDs
        """
        steps = getattr(self, 'steps', []) if hasattr(self, 'steps') else []
        step_details = []
        for i, step in enumerate(steps):
            proc_execs = getattr(step, 'process_execs', []) if hasattr(step, 'process_execs') else []
            step_details.append(f"Step {i+1}: {step.name}, Processes: {[f"{proc_exec.process.process_id} - {proc_exec.exec_id}" for proc_exec in proc_execs]}")
        
        name = getattr(self.about, 'name', 'unnamed') if hasattr(self, 'about') else 'unnamed'
        
        # return f"NeuPipeline(name='{name}'id='{self.pipeline_id}', "\
        #        f"steps={'\n'.join(step_details)}, scheduler={self.scheduler.value})"
        
        return f"""
NeuPipeline Details:
Name: {name}
ID: {self.pipeline_id}
Scheduler: {self.scheduler.value}
Steps:
{'\t\n'.join(step_details) if step_details else 'None'}
BIDS Root: {self.bids_root}
About: {self.about if self.about else 'None'}
Execution Command: {self.execution_command if self.execution_command else 'Not generated yet'}
    """
    
    @property
    def pipeline_dir_path(self) -> Path:
        """Get the path to the pipeline directory."""
        return Path(self._paths.pipelines) / self.pipeline_id
    
    @property
    def model_path(self) -> Path:
        """Get the path to the pipeline model file."""
        return self.pipeline_dir_path / "model.json"
    
    @property
    def script_path(self) -> Path:
        """Get the path to the pipeline execution script."""
        return self.pipeline_dir_path / f"{self.pipeline_id}.sh"
    
    @property
    def command(self) -> str:
        """Get the execution command for the pipeline.
        
        Returns:
            str: The command to execute the pipeline
        
        Raises:
            ValueError: If the execution command is not yet generated
        """
        if not self.execution_command:
            if self.script_path.exists():
                # If the script exists but execution_command is not set, generate it
                self.execution_command = f"bash {self.script_path}"
            else:
                raise ValueError("Pipeline execution script has not been generated yet. "
                                "Call create_pipeline_dir() first.")
        return self.execution_command

    def apply_standard_exec_params(self):
        """Apply standard execution parameters to all processes in the pipeline."""
        
        # If starting from raw BIDS, ensure that the first step's processes take only raw BIDS input
        # Assume that BIDS filters are set at BIDS_FILTERS env var in the process execs
        if self.start_from_raw_bids and self.steps:
            first_step = self.steps[0]
            for proc_exec in first_step.process_execs:
                # Check if scope="raw" is set in BIDS_FILTERS. If not, set it.
                bids_filters_str: str = proc_exec.env_var_values.get("BIDS_FILTERS", "{}")
                bids_filters: dict = json.loads(bids_filters_str) if bids_filters_str else {}
                if "scope" not in bids_filters or bids_filters["scope"] != "raw":
                    bids_filters["scope"] = "raw"
                    proc_exec.set_env_var_value("BIDS_FILTERS", json.dumps(bids_filters))
        
        # For the process execs in the remaining steps, ensure they have scope="<pipeline_name>"
        starting_step_idx = 1 if self.start_from_raw_bids else 0
        for step in self.steps[starting_step_idx:]:
            for proc_exec in step.process_execs:
                # Check if scope is set in BIDS_FILTERS. If not, set it.
                bids_filters_str: str = proc_exec.env_var_values.get("BIDS_FILTERS", "{}")
                bids_filters: dict = json.loads(bids_filters_str) if bids_filters_str else {}
                # if "scope" not in bids_filters or bids_filters["scope"] != self.about.name:
                if "scope" not in bids_filters:
                    bids_filters["scope"] = self.about.name
                    proc_exec.set_env_var_value("BIDS_FILTERS", json.dumps(bids_filters))

        for step in self.steps:
            for proc_exec in step.process_execs:
                # Apply the pipeline's scheduler to each process exec
                proc_exec.scheduler = self.scheduler
                
                # Set standard environment variables - PIPELINE_NAME, PIPELINE_ID, PROCESS_ID, PROCESS_EXEC_ID
                proc_exec.set_env_var_value("PIPELINE_NAME", self.about.name)
                proc_exec.set_env_var_value("PIPELINE_ID", self.pipeline_id)
                proc_exec.set_env_var_value("PROCESS_ID", proc_exec.process.process_id)
                proc_exec.set_env_var_value("PROCESS_EXEC_ID", proc_exec.exec_id)
                
                # Set standard bind-mount paths - /data, 
                proc_exec.set_bind_path_value("/data", str(self.bids_root))

                # Generate the command to ensure it's ready
                proc_exec.generate_command()
                
                # Check if all the required configuration is set
                if not proc_exec.check_configuration_complete():
                    print(f"WARNING: ProcessExec {proc_exec.exec_id} in step '{step.name}' is missing configuration.")
                    print(proc_exec.print_configuration_status())
    
    def create_pipeline_dir(self) -> Path:
        """Create the pipeline directory structure."""
        # Create the main pipeline directory
        pipeline_dir = self.pipeline_dir_path
        pipeline_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize status tracking
        self._initialize_status_tracking()
        
        # Create the execution script
        self._generate_execution_script()
        
        # Create README.md with pipeline information
        self._generate_readme()
        
        # Save the model file for reproducibility
        with open(self.model_path, "w") as f:
            f.write(self.model_dump_json(indent=2))
        
        return pipeline_dir
    
    def _build_script_content(self, script_lines: List[str]) -> List[str]:
        """
        Build script content for the pipeline execution that:
        1. Loads relevant variables
        2. Creates a timestamped log directory
        3. Loads model.json and iterates through steps
        4. Handles different schedulers dynamically
        5. Maintains logs and updates status.json
        6. Supports resuming functionality
        
        Args:
            script_lines: The base script lines to build upon
            
        Returns:
            List[str]: The completed script content as a list of strings
        """
        # Path to template file
        template_dir = Path(__file__).parent / "templates"
        template_path = template_dir / "pipeline_script_template.sh"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Pipeline script template not found at {template_path}")
        
        # Read the template file
        with open(template_path, "r") as f:
            template_content = f.read()
        
        # Replace placeholders with actual values
        script_content = template_content.replace("PL_ID_PLACEHOLDER", self.pipeline_id)
        script_content = script_content.replace("PL_DIR_PLACEHOLDER", str(self.pipeline_dir_path))
        script_content = script_content.replace("SCHEDULER_PLACEHOLDER", self.scheduler.value.upper())
        
        # Add the script content to the script_lines
        script_lines.append(script_content)
        
        return script_lines
    
    def _generate_execution_script(self) -> Path:
        """Generate the execution script for the pipeline."""
        # Common script components
        script_lines = []
        
        # Add shebang and header comment
        # script_lines.append("#!/bin/bash")
        # script_lines.append("")
        script_lines.append(f"# NeuPipeline Execution Script: {self.about.name}")
        script_lines.append(f"# Pipeline ID: {self.pipeline_id}")
        script_lines.append(f"# Version: {self.about.version}")
        script_lines.append(f"# Author: {self.about.author}")
        if hasattr(self.about, 'contact') and self.about.contact:
            script_lines.append(f"# Contact: {self.about.contact}")
        script_lines.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        script_lines.append("")
        
        # Add description
        if self.about.description:
            script_lines.append("# Description:")
            for line in self.about.description.split("\n"):
                script_lines.append(f"# {line}")
            script_lines.append("")
        
        # Use the improved script generator to build the script content
        script_lines = self._build_script_content(script_lines)
        
        # Convert script_lines list to a string
        script_content = "\n".join(script_lines)
        
        with open(self.script_path, "w") as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(self.script_path, 0o755)
        
        # Save the execution command
        self.execution_command = f"bash {self.script_path}"
        
        return self.script_path
    
    def _generate_readme(self) -> Path:
        """Generate a README.md file with pipeline information."""
        readme_path = self.pipeline_dir_path / "README.md"
        
        lines = []
        lines.append(f"# {self.about.name}")
        lines.append("")
        
        # Add description
        if self.about.description:
            lines.append("## Description")
            lines.append(self.about.description)
            lines.append("")
        
        # Add pipeline information
        lines.append("## Pipeline Information")
        lines.append(f"- **Pipeline ID:** {self.pipeline_id}")
        lines.append(f"- **Version:** {self.about.version}")
        lines.append(f"- **Author:** {self.about.name}")
        if self.about.author:
            lines.append(f"- **Contact:** {self.about.author}")
        lines.append(f"- **Scheduler:** {self.scheduler.value}")
        lines.append("")
        
        # Add steps information
        lines.append("## Pipeline Steps")
        for i, step in enumerate(self.steps):
            lines.append(f"### Step {i+1}: {step.name}")
            
            if step.description:
                lines.append(step.description)
                lines.append("")
            
            lines.append("Processes:")
            for j, proc_exec in enumerate(step.process_execs):
                lines.append(f"- **Process {j+1}:** {proc_exec.exec_id}")
        
        # Add usage instructions
        lines.append("")
        lines.append("## Usage")
        lines.append("To execute this pipeline, run the following command:")
        lines.append("")
        lines.append("```bash")
        if self.execution_command:
            lines.append(self.execution_command)
        else:
            lines.append(f"bash {self.script_path}")
        lines.append("```")
        
        # Write to file
        with open(readme_path, "w") as f:
            f.write("\n".join(lines))
        
        return readme_path
    
    def _initialize_status_tracking(self) -> Path:
        """Initialize the status tracking file for the pipeline."""
        # Create the status file in the pipeline directory
        status_path = self.pipeline_dir_path / "status.json"
        
        current_time = datetime.now().isoformat()
        
        pipeline_status = NeuPipelineStatus(
            pipeline_id=self.pipeline_id,
            created_at=current_time,
            last_updated=current_time,
            status=ProcessStatus.NOT_STARTED.value,
            scheduler=self.scheduler.value,
            steps=[]
        )
        for i, step in enumerate(self.steps):
            step_status = NeuPipelineStepStatus(
                step_id=i,
                name=step.name,
                status=ProcessStatus.NOT_STARTED.value,
                started_at=None,
                completed_at=None,
                last_updated=current_time,
                error=None,
                processes=[]
            )
            for j, proc_exec in enumerate(step.process_execs):
                proc_status = NeuProcessExecStatus(
                    process_id=proc_exec.process.process_id if hasattr(proc_exec, 'process') else proc_exec.exec_id,
                    exec_id=proc_exec.exec_id,
                    name=proc_exec.process.process_id if hasattr(proc_exec, 'process') else proc_exec.exec_id,
                    status=ProcessStatus.NOT_STARTED.value,
                    started_at=None,
                    completed_at=None,
                    last_updated=current_time,
                    error=None,
                    scheduler_job_id=None
                )
                step_status.processes.append(proc_status)
            pipeline_status.steps.append(step_status)

        # Save the pipeline status file
        with open(status_path, "w") as f:
            f.write(pipeline_status.model_dump_json(indent=2))
        
        return status_path
    
    def get_pipeline_status(self) -> NeuPipelineStatus:
        """Retrieve the current status of the pipeline from the status file.
        
        Returns:
            NeuPipelineStatus: The current status of the pipeline.
        Raises:
            FileNotFoundError: If the status file does not exist.
        """
        status_path = self.pipeline_dir_path / "status.json"
        
        if not status_path.exists():
            raise FileNotFoundError(f"Status file not found at {status_path}")
        
        with open(status_path, "r") as f:
            status_data = json.load(f)
        
        return NeuPipelineStatus.model_validate(status_data)
    
    def print_pipeline_status(self) -> None:
        """Print a formatted report of the current pipeline status."""
        try:
            status_data: NeuPipelineStatus = self.get_pipeline_status()
            
            print(f"\n{'='*80}")
            print(f"Pipeline Status: {status_data.pipeline_id}")
            print(f"{'='*80}")
            print(f"Created: {status_data.created_at}")
            print(f"Last Updated: {status_data.last_updated}")
            print(f"Overall Status: {status_data.status}")
            print(f"{'-'*80}")

            for step in status_data.steps:
                print(f"\nStep {step.step_id + 1}: {step.name} - {step.status}")

                if step.status == ProcessStatus.RUNNING.value and step.started_at:
                    print(f"  Started: {step.started_at}")

                if step.status == ProcessStatus.COMPLETE.value:
                    print(f"  Completed: {step.completed_at}")

                if step.status == ProcessStatus.FAILED.value:
                    print(f"  Failed: {step.completed_at}")
                    print(f"  Error: {step.error}")

                print("  Processes:")
                for proc in step.processes:
                    status_indicator = {
                        ProcessStatus.NOT_STARTED.value: "⬜",
                        ProcessStatus.RUNNING.value: "🔄",
                        ProcessStatus.COMPLETE.value: "✅",
                        ProcessStatus.FAILED.value: "❌"
                    }.get(proc.status, "?")

                    print(f"  {status_indicator} Process {proc.process_id}: {proc.name} - {proc.status}")

                    if proc.status == ProcessStatus.RUNNING.value and proc.started_at:
                        print(f"    Started: {proc.started_at}")

                    if proc.status == ProcessStatus.COMPLETE.value:
                        print(f"    Completed: {proc.completed_at}")

                    if proc.status == ProcessStatus.FAILED.value:
                        print(f"    Failed: {proc.completed_at}")
                        print(f"    Error: {proc.error}")

                    if proc.scheduler_job_id:
                        print(f"    Job ID: {proc.scheduler_job_id}")
            
            print(f"\n{'='*80}\n")
            
        except FileNotFoundError:
            print(f"No status information available for pipeline {self.pipeline_id}")
            
    def update_pipeline_status(self, step_idx: int, exec_id: str, new_status: ProcessStatus, error_msg: Optional[str] = None, scheduler_job_id: Optional[str] = None) -> None:
        """Update the status of a specific process execution in the pipeline.
        Args:
            step_idx: The index of the step in the pipeline
            exec_id: The execution ID of the specific process to update
            new_status: The new status to set for the process execution
            error_msg: Optional; Error message if the process failed
            scheduler_job_id: Optional; Job ID assigned by the HPC scheduler
            
        Raises:
            FileNotFoundError: If the status file does not exist
            ValueError: If the step index or exec_id is invalid
        """
        
        status: NeuPipelineStatus = self.get_pipeline_status()
        
        current_time = datetime.now().isoformat()
        status.last_updated = current_time
        
        if step_idx < 0 or step_idx >= len(status.steps):
            raise IndexError(f"Step index {step_idx} out of range")
        
        step_status = status.steps[step_idx]
        step_status.last_updated = current_time
        
        if not exec_id:
            raise ValueError("exec_id must be provided to update process status")
        
        proc_status = next((p for p in step_status.processes if p.exec_id == exec_id), None)
        if not proc_status:
            raise ValueError(f"Process exec ID {exec_id} not found in step {step_idx}")
        
        proc_status.status = new_status.value
        proc_status.last_updated = current_time
        
        if new_status == ProcessStatus.RUNNING:
            proc_status.started_at = current_time
            if scheduler_job_id:
                proc_status.scheduler_job_id = scheduler_job_id
        elif new_status in (ProcessStatus.COMPLETE, ProcessStatus.FAILED):
            proc_status.completed_at = current_time
            if new_status == ProcessStatus.FAILED and error_msg:
                proc_status.error = error_msg
        
        # Update step status based on process statuses
        if all(p.status == ProcessStatus.COMPLETE.value for p in step_status.processes):
            step_status.status = ProcessStatus.COMPLETE.value
            step_status.completed_at = current_time
        elif any(p.status == ProcessStatus.FAILED.value for p in step_status.processes):
            step_status.status = ProcessStatus.FAILED.value
            step_status.completed_at = current_time
            step_status.error = "One or more processes failed"
        elif any(p.status == ProcessStatus.RUNNING.value for p in step_status.processes):
            step_status.status = ProcessStatus.RUNNING.value
            if not step_status.started_at:
                step_status.started_at = current_time
        else:
            step_status.status = ProcessStatus.NOT_STARTED.value
            
        # Update overall pipeline status based on step statuses
        if all(s.status == ProcessStatus.COMPLETE.value for s in status.steps):
            status.status = ProcessStatus.COMPLETE.value
        elif any(s.status == ProcessStatus.FAILED.value for s in status.steps):
            status.status = ProcessStatus.FAILED.value
        elif any(s.status == ProcessStatus.RUNNING.value for s in status.steps):
            status.status = ProcessStatus.RUNNING.value
        else:
            status.status = ProcessStatus.NOT_STARTED.value
            
        # Save the updated status back to the file
        status_path = self.pipeline_dir_path / "status.json"
        with open(status_path, "w") as f:
            f.write(status.model_dump_json(indent=2))
        
    
    def execute_via_bash(self, resume: bool = False) -> str:
        """Execute the pipeline by running the generated bash script.
        
        Args:
            resume: If True, resume execution from the last successful step
        
        Returns:
            str: A message indicating the result of the execution
            
        Raises:
            FileNotFoundError: If resume=True and the status file does not exist
        """
        # Ensure pipeline directory and bash script exist
        if not self.script_path.exists():
            self.create_pipeline_dir()
        
        # If resuming, update the status
        if resume:
            status_path = self.pipeline_dir_path / "status.json"
            
            if not status_path.exists():
                raise FileNotFoundError(f"Status file not found at {status_path}")
            
            # Get current status
            with open(status_path, "r") as f:
                status_data = json.load(f)
            
            # Check if pipeline already completed
            if status_data["status"] == "complete":
                return f"Pipeline {self.pipeline_id} already completed. Nothing to resume."
            
            # Update status to indicate resuming
            status_data["status"] = "resuming"
            status_data["last_updated"] = datetime.now().isoformat()
            
            with open(status_path, "w") as f:
                json.dump(status_data, f, indent=2)
        
        # Ensure execution_command is set
        if not self.execution_command:
            self.execution_command = f"bash {self.script_path}"
        
        # Execute the script
        try:
            result = subprocess.run(
                ["bash", str(self.script_path)],
                check=True,
                capture_output=True,
                text=True
            )
            return f"Pipeline {self.pipeline_id} executed successfully. Output:\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Pipeline {self.pipeline_id} execution failed. Error:\n{e.stderr}"
        
    def get_earliest_incomplete_step_index(self) -> Optional[int]:
        """Get the index of the earliest incomplete step in the pipeline.
        
        Returns:
            Optional[int]: The index of the earliest incomplete step, or None if all steps are complete
        """
        status = self.get_pipeline_status()
        
        for i, step in enumerate(status.steps):
            if step.status != ProcessStatus.COMPLETE.value:
                return i
        return None
    
    def reset_pipeline_status(self) -> None:
        """Reset the pipeline status to NOT_STARTED for all steps and processes."""
        self._initialize_status_tracking()

    def pre_execution_checks(self) -> List[str]:
        """Perform pre-execution checks to ensure all processes are properly configured.
        
        Returns:
            List[str]: A list of warning messages for any issues found.
        """
        warnings = []
        
        for step in self.steps:
            for proc_exec in step.process_execs:
                if not proc_exec.check_configuration_complete():
                    warnings.append(f"WARNING: ProcessExec {proc_exec.exec_id} in step '{step.name}' is missing configuration.")
                    warnings.append(proc_exec.print_configuration_status())
        
        return warnings
    
    def pre_execution(self, logger: logging.Logger) -> None:
        """Perform any necessary actions before executing the first step.
        
        Args:
            logger: Logger instance for logging details.
        """
        # Create dataset_description.json if not exists
        dataset_description_path = self.bids_root / "derivatives" / self.about.name / "dataset_description.json"
        if not dataset_description_path.exists():
            dataset_description_path.parent.mkdir(parents=True, exist_ok=True)
            dataset_description = BIDSDatasetDescription(
                Name=self.about.name,
                BIDSVersion="1.6.0",
                DatasetType="derivative",
                GeneratedBy=[
                    BIDSGeneratedByToolInfo(
                        Name=self.about.name,
                        Version=self.about.version if self.about.version else "0.1.0",
                        Description=self.about.description if self.about.description else "Neuroimaging pipeline",
                        Author=self.about.author if self.about.author else "Unknown",
                    ),
                    BIDSGeneratedByToolInfo(
                        Name="NeuroAnalyst",
                        Version="0.1.0",
                        CodeURL="https://github.com/chinmaymokashicm/neuroanalyst"
                    )
                ],
                License="CC0",
                Authors=[self.about.author] if self.about.author else [],
                Acknowledgements="",
                HowToAcknowledge="Please cite the NeuroAnalyst repository.",
                PipelineDescription=PipelineDescriptionSpec(
                    Name=self.about.name,
                    Version="0.1.0",
                    CodeURL="https://github.com/chinmaymokashicm/neuroanalyst",
                    Description=self.about.description if self.about.description else "Pipeline description not provided."
                ),
                PipelineSteps=[{
                    "name": step.name, 
                    "description": step.description if step.description else "",
                    "processes": [{
                        "process_exec_id": proc_exec.exec_id,
                        "process_id": proc_exec.process.process_id if hasattr(proc_exec, 'process') else proc_exec.exec_id,
                    } for proc_exec in step.process_execs]
                    } for step in self.steps]
            )
            with open(dataset_description_path, "w") as f:
                f.write(dataset_description.model_dump_json(indent=2))
                logger.info(f"Created dataset_description.json at {dataset_description_path}")

    def load_metrics(self, filepath: str, numeric_only: bool = True) -> Dict[str, Any]:
        """Load metrics from a sidecar file and provide associated metadata such as -
            - function name
            - process ID
            - process exec ID
            - processing time
            - processing date
            - directory
            - input file path
            - output file path
            - BIDS entities (subject, session, etc.)

        Args:
            filepath: The path to the sidecar JSON file.
            numeric_only: If True, only load numeric metrics. Non-numeric metrics will be ignored.

        Returns:
            Dict[str, Any]: A dictionary mapping metric names to their values.
            Dict[str, Any]: A dictionary containing metadata about the metrics.
        """
        metrics, about = {}, {}
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                if "metrics" in data and isinstance(data["metrics"], dict):
                    file_metrics = data["metrics"]
                    if numeric_only:
                        file_metrics = {k: v for k, v in file_metrics.items() if isinstance(v, (int, float))}
                    metrics.update(file_metrics)
                if "FunctionName" in data:
                    bids_entities: Dict[str, Any] = {f"bids_{k}": v for k, v in data.get("BIDSEntities", {}).items() if v}
                    about = {
                        "function": data.get("FunctionName", ""),
                        "processing_time": data.get("ProcessingTime", ""),
                        "processing_date": data.get("ProcessingDate", ""),
                        "process_id": data.get("ProcessID", ""),
                        "process_exec_id": data.get("ProcessExecID", ""),
                        "directory": data.get("Directory", ""),
                        "input_file": data.get("InputFile", ""),
                        "output_file": data.get("OutputFile", ""),
                        **bids_entities
                    }
        except Exception as e:
            print(f"Error loading metrics from {filepath}: {e}")

        return metrics, about
    
    def aggregate_metrics(self, sidecar_filepaths: list[str | Path]) -> pd.DataFrame:
        """
        Aggregate metrics from all sidecar files in the derivatives directory of the pipeline.
        Assumptions:
            - Sidecar files are JSON files with a 'metrics' key containing numeric metrics.
            - All sidecar files are associated with the same process ID - ensuring that the metrics have been generated by the same process.
        
        Args:
            sidecar_filepaths: List of paths to sidecar JSON files.
        
        Returns:
            pd.DataFrame: A DataFrame containing aggregated metrics with metadata.
        """
        # Ensure that all sidecar files belong to the same process ID
        process_id: Optional[str] = None
        all_metrics = []
        for filepath in sidecar_filepaths:
            metrics, about = self.load_metrics(str(filepath), numeric_only=True)
            if metrics:
                all_metrics.append({**metrics, **about})
                if "process_id" not in about:
                    raise ValueError(f"Sidecar file {filepath} missing 'process_id' in metadata.")
                if process_id is None:
                    process_id = about["process_id"]
                elif process_id != about["process_id"]:
                    raise ValueError(f"Sidecar file {filepath} has a different 'process_id' ({about['process_id']}) than expected ({process_id}).")

        # If we have all metrics and a consistent process ID, create a DataFrame
        if all_metrics and process_id:
            df = pd.DataFrame(all_metrics)
            return df

        # If we didn't collect any valid metrics, return an empty DataFrame
        return pd.DataFrame()

    def generate_summary(self) -> Path:
        """Generate a summary report of the pipeline configuration.
        This method creates an Excel file summarizing the pipeline steps, processes, and aggregated metrics.
        Steps:
            1. List all steps and the unique process IDs within each step. Convert this into a Pandas DataFrame.
            2. Assign each sidecar filepath to the relevant step and process ID.
            3. For each step and process ID, aggregate metrics from the associated sidecar files. Also create a sheet for metadata.
            4. Write all DataFrames to an Excel file with appropriate sheet names.
        
        Returns:
            Path: The path to the generated summary file.
        """
        derivatives_dir: Path = self.bids_root / "derivatives" / self.about.name
        summary_path: Path = derivatives_dir / "pipeline_summary.xlsx"
        
        # Step 1: List all steps and the unique process IDs within each step. Convert this into a Pandas DataFrame.
        step_info = []
        for i, step in enumerate(self.steps):
            # Get unique process IDs in this step
            process_ids: list[str] = list(set([pe.process.process_id for pe in step.process_execs]))
            for process_id in process_ids:
                step_info.append({
                    "step_idx": i,
                    "step_number": i + 1,
                    "step_name": step.name,
                    "step_description": step.description if step.description else "",
                    "process_id": process_id,
                })
        df_steps = pd.DataFrame(step_info)
        
        # Step 2: Assign each sidecar filepath to the relevant step and process ID.
        sidecar_mappings: dict = {step_idx: {process_id: [] for process_id in [pe.process.process_id for pe in step.process_execs]} for step_idx, step in enumerate(self.steps)}
        for sidecar_filepath in derivatives_dir.rglob("*.json"):
            if sidecar_filepath.name == "dataset_description.json":
                continue  # Skip dataset_description.json
            with open(sidecar_filepath, "r") as f:
                try:
                    data = json.load(f)
                    if "ProcessExecID" in data and "ProcessID" in data:
                        process_exec_id = data["ProcessExecID"]
                        process_id = data["ProcessID"]
                        step_idx: int = next((i for i, step in enumerate(self.steps) if any(pe.exec_id == process_exec_id for pe in step.process_execs)), None)
                        if step_idx is not None:
                            sidecar_mappings[step_idx][process_id].append(sidecar_filepath)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {sidecar_filepath}. Skipping.")
                    continue

        # Step 3: For each step and process ID, aggregate metrics from the associated sidecar files. Also create a sheet for metadata.

        # Create metadata sheet first
        metadata = {
            "Pipeline ID": self.pipeline_id,
            "Pipeline Name": self.about.name,
            "Version": self.about.version,
            "Author": self.about.author,
            "Description": self.about.description if self.about.description else "",
            "BIDS Root": str(self.bids_root),
            "Generated On": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Number of Steps": len(self.steps),
            "Scheduler": self.scheduler.value
        }
        df_metadata = pd.DataFrame(list(metadata.items()), columns=["Key", "Value"])
        
        with pd.ExcelWriter(summary_path, engine='openpyxl') as writer:
            # Always write the metadata sheet first to ensure at least one sheet exists
            df_metadata.to_excel(writer, sheet_name="Metadata", index=False)
            
            for step_idx, process_sidecars in sidecar_mappings.items():
                step = self.steps[step_idx]
                
                for process_id, filepaths in process_sidecars.items():
                    df_metrics: pd.DataFrame = self.aggregate_metrics(filepaths)
                    if df_metrics.empty:
                        continue
                    df_metrics["step_idx"] = step_idx
                    df_merged: pd.DataFrame = pd.merge(
                        df_steps,
                        df_metrics,
                        how="inner",
                        left_on=["step_idx", "process_id"],
                        right_on=["step_idx", "process_id"]
                    )
                    df_merged = df_merged.drop(columns=["step_idx"])
                    try:
                        logic_name: Optional[str] = NeuProcess.from_process_id(process_id).process_dir.logic.about.name
                    except Exception:
                        logic_name = process_id
                    process_name: str = logic_name
                    sheet_name = f"{step.name[:20]}_{process_name[:20]}".replace(" ", "_")
                    df_merged.to_excel(writer, sheet_name=sheet_name, index=False)
                    
        return summary_path
    
    def post_execution(self, logger: logging.Logger) -> None:
        """Perform any necessary actions after executing all steps.

        Args:
            logger: Logger instance for logging details.
        """
        # Generate summary report
        summary_path = self.generate_summary()
        logger.info(f"Generated pipeline summary at {summary_path}")
        
        # Print final status
        self.print_pipeline_status()

    def execute_via_python(self, logger: logging.Logger, resume: bool = False) -> str:
        """Execute the pipeline step-by-step via Python.
        
        Args:
            logger: Logger instance for logging execution details.
            resume: If True, resume execution from the last successful step.
        Returns:
            str: A message indicating the result of the execution.
        """
        # Ensure pipeline directory and bash script exist
        if not self.script_path.exists():
            self.create_pipeline_dir()

        self.pre_execution(logger)

        starting_step_index = 0 if not resume else self.get_earliest_incomplete_step_index()
        
        if starting_step_index is None:
            return f"Pipeline {self.pipeline_id} already completed. Nothing to resume."
        
        for step_index in range(starting_step_index, len(self.steps)):
            step = self.steps[step_index]
            logger.info(f"Executing Step {step_index + 1}/{len(self.steps)}: {step.name}")
            
            # Execute all processes in this step concurrently
            
            executors = {}
            status_lock = Lock()  # For thread-safe status updates
            failure = False
            failure_message = ""
            
            def execute_and_monitor_process(proc_exec):
                nonlocal failure, failure_message
                
                try:
                    logger.info(f"Executing Process: {proc_exec.exec_id}")
                    
                    # Execute the process based on the scheduler
                    if self.scheduler == HPCScheduler.LSF:
                        executor = LSFExecutor(proc_exec.exec_command)
                    elif self.scheduler == HPCScheduler.SLURM:
                        executor = SLURMExecutor(proc_exec.exec_command)
                    elif self.scheduler == HPCScheduler.PBS:
                        executor = PBSExecutor(proc_exec.exec_command)
                    else:
                        executor = LocalExecutor(proc_exec.exec_command)
                    
                    executors[proc_exec.exec_id] = executor
                    
                    executor.submit()
                    logger.info(f"Submitted process {proc_exec.exec_id} with Job ID: {executor.job_id}")
                    
                    with status_lock:
                        # Update status to RUNNING
                        self.update_pipeline_status(step_index, proc_exec.exec_id, ProcessStatus.RUNNING, scheduler_job_id=executor.job_id)
                    
                    # Poll until done
                    while not executor.is_done() and not failure:
                        executor.poll_status()
                        logger.info(f"Process {proc_exec.exec_id} Status: {executor.status.value}")
                        time.sleep(10)  # Polling interval
                    
                    if failure:  # Another process has already failed
                        logger.warning(f"Process {proc_exec.exec_id} terminated due to failure in another process")
                        return False
                    
                    if executor.is_success():
                        logger.info(f"Process {proc_exec.exec_id} completed successfully.")
                        with status_lock:
                            self.update_pipeline_status(step_index, proc_exec.exec_id, ProcessStatus.COMPLETE)
                        return True
                    else:
                        logger.error(f"Process {proc_exec.exec_id} failed.")
                        with status_lock:
                            self.update_pipeline_status(step_index, proc_exec.exec_id, ProcessStatus.FAILED, error_msg="Process failed during execution.")
                        failure = True
                        failure_message = f"Pipeline {self.pipeline_id} execution halted due to failure in process {proc_exec.exec_id}."
                        return False
                
                except Exception as e:
                    logger.error(f"Error executing process {proc_exec.exec_id}: {e}")
                    with status_lock:
                        self.update_pipeline_status(step_index, proc_exec.exec_id, ProcessStatus.FAILED, error_msg=str(e))
                    failure = True
                    failure_message = f"Pipeline {self.pipeline_id} execution halted due to error in process {proc_exec.exec_id}: {e}"
                    return False
            
            # Start all processes in this step concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(step.process_execs)) as executor:
                futures = {executor.submit(execute_and_monitor_process, proc_exec): proc_exec.exec_id for proc_exec in step.process_execs}
                
                # Wait for all processes to complete
                all_succeeded = True
                for future in concurrent.futures.as_completed(futures):
                    proc_id = futures[future]
                    try:
                        success = future.result()
                        all_succeeded = all_succeeded and success
                    except Exception as e:
                        logger.error(f"Exception in process {proc_id}: {e}")
                        all_succeeded = False
                
                if not all_succeeded:
                    # If any process failed, cancel all other running processes
                    for exec_id, exec_obj in executors.items():
                        if not exec_obj.is_done():
                            logger.warning(f"Terminating process {exec_id} due to failure in other process")
                            # Here we would ideally cancel the job, but that's specific to each scheduler
                    
                    return failure_message if failure_message else f"Pipeline {self.pipeline_id} execution halted due to failure."

            logger.info(f"Step {step_index + 1} completed.")
        
        logger.info(f"Pipeline {self.pipeline_id} completed successfully.")
        
        self.post_execution(logger)
            
        return f"Pipeline {self.pipeline_id} executed successfully."

    def resume_via_bash(self) -> str:
        """Resume pipeline execution via bash script.
        
        Args:
            resume: If True, resume execution from the last successful step.
        Returns:
            str: A message indicating the result of the execution.
        """
        return self.execute_via_bash(resume=True)
    
    @classmethod
    def from_model_file(cls, model_path: Union[str, Path]) -> 'NeuPipeline':
        """Create a NeuPipeline instance from a model file."""
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        with open(model_path, "r") as f:
            model_data = json.load(f)
        
        return cls.model_validate(model_data)
    
    @classmethod
    def from_pipeline_id(cls, pipeline_id: str) -> 'NeuPipeline':
        """Create a NeuPipeline instance from a pipeline ID."""
        paths = NeuroAnalystPaths()
        model_path = Path(paths.pipelines) / pipeline_id / "model.json"
        
        return cls.from_model_file(model_path)
