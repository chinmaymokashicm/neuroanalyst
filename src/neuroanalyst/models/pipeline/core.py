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
import asyncio
from enum import Enum
from pathlib import Path
from datetime import datetime
from threading import Lock
from typing import Optional, List, Dict, Any, Union, Set, ClassVar, Literal

from pydantic import BaseModel, Field, model_validator, field_validator
import pandas as pd
from bids import BIDSLayout

from ...utils.constants import NeuroAnalystPaths
from ...utils.id_generators import generate_id
from ...utils.data import flatten_dict
from ..about import About
from ..bids import BIDSDatasetDescription, BIDSGeneratedByToolInfo, PipelineDescriptionSpec
from ..process.exec.core import NeuProcessExec, HPCScheduler, ExecutionMode
from ..process.process.core import NeuProcess
from ..process.logic.core import NeuProcessLogic
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
    status: ProcessStatus = Field(description="Current status of the process execution")
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
    status: ProcessStatus = Field(description="Current status of the pipeline step")
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
    status: ProcessStatus = Field(description="Overall status of the pipeline")
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
    
    def get_completion_percentage(self, step_idx: Optional[int] = None, process_id: Optional[str] = None) -> float:
        """Calculate the completion percentage of the pipeline, a specific step, or a specific process.
        
        Args:
            step_idx: Optional; The index of the step in the pipeline
            process_id: Optional; The process ID to calculate completion for
        Returns:
            float: Completion percentage (0.0 to 100.0)
        """
        total_count: int = 0
        complete_count: int = 0
        
        if step_idx is not None:
            if step_idx < 0 or step_idx >= len(self.steps):
                return 0.0
            step_status = self.steps[step_idx]
            for proc_status in step_status.processes:
                if process_id is None or proc_status.process_id == process_id:
                    total_count += 1
                    if proc_status.status == ProcessStatus.COMPLETE:
                        complete_count += 1
        else:
            for step_status in self.steps:
                for proc_status in step_status.processes:
                    if process_id is None or proc_status.process_id == process_id:
                        total_count += 1
                        if proc_status.status == ProcessStatus.COMPLETE:
                            complete_count += 1
        
        if total_count == 0:
            return 0.0
        return (complete_count / total_count) * 100.0
    
    def get_stats(self, by: Literal["process", "step", "all"] = "process") -> dict:
        """Get statistics about the pipeline execution.
        
        Args:
            by: "process" to get stats per process, "step" to get stats per step, "all" to get stats per process per step
            
        Returns:
            dict: A dictionary with counts of statuses
        """
        # Provide a count of exec statuses by 'by' parameter
        stats: dict = {}
        if by == "all":
            for idx in range(len(self.steps)):
                step_status: NeuPipelineStepStatus = self.steps[idx]
                step_status_stats: dict = {status_category: 0 for status_category in ProcessStatus._value2member_map_.keys()}
                for proc_status in step_status.processes:
                    key = proc_status.status.value
                    step_status_stats[key] = step_status_stats.get(key, 0) + 1
                stats[idx] = step_status_stats
        elif by == "step":
            step_stats: dict = {status_category: 0 for status_category in ProcessStatus._value2member_map_.keys()}
            for step_status in self.steps:
                key = step_status.status.value
                step_stats[key] = step_stats.get(key, 0) + 1
            stats = step_stats
        elif by == "process":
            proc_stats: dict = {status_category: 0 for status_category in ProcessStatus._value2member_map_.keys()}
            for step_status in self.steps:
                for proc_status in step_status.processes:
                    key = proc_status.status.value
                    proc_stats[key] = proc_stats.get(key, 0) + 1
            stats = proc_stats
        else:
            raise ValueError("Invalid 'by' parameter. Must be 'process', 'step', or 'all'.")
        return stats

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
        unique_processes: Set[str] = set(proc_exec.process.process_id for proc_exec in self.process_execs)
        detailed_info: str = f"Name: {self.name}\n"
        detailed_info += f"Description: {self.description if self.description else 'None'}\n"
        detailed_info += f"Processes: {', '.join(unique_processes)}\n"
        if unique_processes:
            for process in unique_processes:
                detailed_info += f"  Process ID: {process}\n"
                detailed_info += f"  Number of process execs: {len(self.process_execs)}\n"
                detailed_info += f"  Execution Mode: {self.process_execs[0].execution_mode.value}\n"
        
        return detailed_info
    
    @model_validator(mode='after')
    def validate_process_execs(self) -> 'NeuPipelineStep':
        """Validate that there is at least one process exec in the step."""
        if not self.process_execs:
            raise ValueError("Pipeline step must contain at least one process execution")
        return self
    
    def add_process_exec(self, proc_exec: NeuProcessExec) -> None:
        """Add a NeuProcessExec instance to the step."""
        if not isinstance(proc_exec, NeuProcessExec):
            raise TypeError("proc_exec must be an instance of NeuProcessExec")
        if proc_exec in self.process_execs:
            print(f"ProcessExec {proc_exec.exec_id} already in step {self.name}")
            return
        self.process_execs.append(proc_exec)

# Define default scheduler flags for each scheduler
DEFAULT_SCHEDULER_FLAGS = {
    HPCScheduler.LSF : {"-n": 2, "-q": "medium", "-M": "20GB", "-W": "12:00"},
    HPCScheduler.SLURM : {"--cpus-per-task": 2, "--partition": "medium", "--mem": "20G", "--time": "12:00:00"},
    HPCScheduler.PBS : {"-l": "nodes=1:ppn=2,mem=20gb,walltime=12:00:00", "-q": "medium"},
    HPCScheduler.LOCAL : {}
}

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
    # start_from_raw_bids: bool = Field(default=True, description="Whether to start processing from raw BIDS data")
    starting_bids_scope: str = Field(default="raw", description="The starting BIDS scope for the pipeline")
    
    # Execution command
    execution_command: Optional[str] = Field(
        default=None,
        description="The generated execution command for the pipeline"
    )
    
    # Cache paths for easy access
    # _paths: ClassVar[NeuroAnalystPaths] = NeuroAnalystPaths()
    
    @field_validator('about', mode='before')
    def validate_about(cls, v: dict | About) -> About:
        """Ensure 'about' is an About instance."""
        if isinstance(v, dict):
            return About(**v)
        elif isinstance(v, About):
            return v
        else:
            raise TypeError("about must be an instance of About or a dict")
    
    @model_validator(mode='after')
    def validate_model(self) -> 'NeuPipeline':
        """Validate that there is at least one step in the pipeline."""
        if not self.steps:
            raise ValueError("Pipeline must contain at least one step")
        
        # Check if about.name is not already a derivatives name in the dataset.
        derivatives_root: Path = self.bids_root / "derivatives"
        
        if derivatives_root.exists():
            derivatives_dirs = [d.name for d in derivatives_root.iterdir() if d.is_dir()]
            if self.about.name in derivatives_dirs:
                print(Warning(f"Pipeline name '{self.about.name}' conflicts with existing derivatives directory in BIDS dataset."))
        
        return self
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the NeuPipeline.
        - Pipeline details
        - Scheduler
        - Step names
            - Process names
            - Individual process IDs, process exec IDs, number of execs per process
        - Individual process IDs, process exec IDs
        """
        detailed_info: str = f"Pipeline ID: {self.pipeline_id}\n"
        detailed_info += f"Name: {self.about.name}\n"
        detailed_info += f"Description: {self.about.description if self.about.description else 'None'}\n"
        detailed_info += f"Author: {self.about.author if self.about.author else 'None'}\n"
        detailed_info += f"Version: {self.about.version if self.about.version else 'None'}\n"
        detailed_info += f"Number of Steps: {len(self.steps)}\n"
        detailed_info += f"Scheduler: {self.scheduler.value}\n"
        for step_idx, step in enumerate(self.steps):
            detailed_info += f" Step {step_idx + 1} - Name: {step.name}\n"
            step_info_lines: list[str] = str(step).splitlines()
            for line in step_info_lines:
                detailed_info += f"   {line}\n"
        return detailed_info
    
    @property
    def username(self) -> Optional[str]:
        """Get the username associated with the pipeline (from the first process exec)."""
        if self.steps and self.steps[0].process_execs:
            return self.steps[0].process_execs[0].username
        return None
    
    @property
    def pipeline_dir_path(self) -> Path:
        """Get the path to the pipeline directory."""
        return Path(NeuroAnalystPaths(username=self.username).pipelines) / self.pipeline_id
    
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
    
    @property
    def process_execs(self) -> List[NeuProcessExec]:
        """Get a flat list of all NeuProcessExec instances in the pipeline."""
        proc_execs: List[NeuProcessExec] = []
        for step in self.steps:
            proc_execs.extend(step.process_execs)
        return proc_execs
    
    @property
    def log_dir(self) -> Path:
        """Get the path to the pipeline log directory."""
        dir_path: Path = Path(NeuroAnalystPaths(username=self.username).logs) / "pipelines" / self.pipeline_id
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    @property
    def log_file_path(self) -> Path:
        """Get the path to the pipeline log file."""
        return self.log_dir / f"{self.pipeline_id}.log"
    
    @property
    def logger(self) -> logging.Logger:
        """Get a logger instance for the pipeline."""
        logger = logging.getLogger(self.pipeline_id)
        if not logger.hasHandlers():
            logger.setLevel(logging.INFO)
            file_handler = logging.FileHandler(self.log_file_path, mode='a')
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        return logger
    
    @property
    def is_ready(self) -> bool:
        """Check if the pipeline is ready for execution."""
        return all(proc_exec.is_fully_configured for proc_exec in self.process_execs)
    
    @classmethod
    def constructor_v2(
        cls,
        about_pipeline: About | dict,
        username: str,
        bids_root: str | Path,
        steps_info: list[list[str]],
        process_configs: list[list[str | dict]],
        starting_bids_filters: dict[str, str],
        execution_mode: str | ExecutionMode,
        scheduler: HPCScheduler,
        starting_scope: str = "raw",
        verify_environment: bool = True
    ):
        """
        Construct a NeuPipeline instance from high-level process configurations.
        Args:
            about_pipeline (About | dict): Metadata about the pipeline. If dict, requires keys: name, description, version, author.
            username (str): Username of the pipeline creator. This username will be associated with all processes.
            bids_root (str | Path): Path to the BIDS dataset root directory.
            steps_info (list[list[str]]): List of steps, each defined by [step_name, step_description].
            process_configs (list[list[str | dict]]): List of process configurations, each with keys: 'process_ids' and 'extra_parameters'.
                'process_ids' can be a single process ID (str) or a list of process IDs (list[str]).
                'extra_parameters' can be a single dict or a list of dicts corresponding to each process ID.
            starting_bids_filters (dict): BIDS filters to apply to the first step.
            execution_mode (ExecutionMode): Execution mode for all processes (CONTAINER or VENV).
            scheduler (HPCScheduler): HPC scheduler to use for all processes.
            starting_scope (str): Scope to use for the first step.
            verify_environment (bool): Whether to verify the environment for each process.
        
        Returns:
            NeuPipeline: The constructed NeuPipeline instance.
        
        Raises:
            ValueError: If any validation checks fail.
        """
        if len(steps_info) != len(process_configs):
            raise ValueError("Number of steps_info must match number of process_configs")
        
        bids_root: str = str(bids_root)
        
        about_pipeline: About = About.model_validate(about_pipeline) if isinstance(about_pipeline, dict) else about_pipeline
        if not isinstance(about_pipeline, About):
            raise ValueError("about_pipeline must be an instance of About or a valid dict")
        
        bids_layout: BIDSLayout = BIDSLayout(bids_root, derivatives=True)
        
        n_steps: int = len(steps_info)
        step_configs: dict[int, any] = {
            step_id: {
                "bids_filters": {},
                "processes": [],
                "extra_parameters": []
                } for step_id in range(n_steps)
            }
        
        for step_id, proc_config in enumerate(process_configs):
            process_ids: list[str] | str = proc_config[0]
            extra_parameters: list[dict] | dict = proc_config[1]
            
            if not process_ids:
                raise ValueError(f"Step {step_id}: Each process configuration must include at least one process ID in 'process_ids'")
            if isinstance(process_ids, str):
                process_ids = [process_ids]
                
            if len(process_ids) != len(set(process_ids)):
                raise ValueError(f"Repetitions found in process IDs for Step {step_id}. Each process ID must be unique within a step.")
            
            if not extra_parameters:
                raise ValueError(f"Step {step_id}: Each process configuration must include at least one process ID in 'extra_parameters'")
            if isinstance(extra_parameters, dict):
                extra_parameters = [extra_parameters]
                
            if len(process_ids) != len(extra_parameters):
                raise KeyError(f"'process_ids' has {len(process_ids)} items while 'extra_parameters' has {len(extra_parameters)}")
            
            step_configs[step_id]["processes"] = [NeuProcess.from_process_id(process_id, username=username) for process_id in process_ids]
            step_configs[step_id]["extra_parameters"] = extra_parameters
            
            if step_id == 0:
                # First step - use starting_bids_filters
                step_configs[step_id]["bids_filters"] = starting_bids_filters.copy()
            
            else:
                # Next step - take output_entities of the logic of the first process of the previous step.
                if not step_configs[step_id]["bids_filters"]:
                    previous_process: NeuProcess = step_configs[step_id - 1]["processes"][0]
                    previous_logic: NeuProcessLogic = previous_process.logic
                    step_configs[step_id]["bids_filters"] = previous_logic.output_entities.copy()        
        
        steps: list[NeuPipelineStep] = []
        # Spawn optimized process execs for the first process of the first step. Use its subject/session splits to create the rest of the process execs.
        # For example, if the first process spawns 3 execs for (sub-01, ses-01), (sub-01, ses-02), (sub-02, ses-01),
        # then for each these pairs, merge the BIDS filters for each process in the step and create the same number of execs for each process.
        first_process: NeuProcess = step_configs[0]["processes"][0]
        process_execs_first, subject_session_pairs = NeuProcessExec.spawn_optimized_execs(
            process=first_process,
            bids_filters=step_configs[0]["bids_filters"],
            bids_layout=bids_layout
        )
        
        if not process_execs_first:
            raise ValueError("No process executions were created for the first process of the first step. Check BIDS filters and dataset.")
        
        for step_id, step_config in step_configs.items():
            step_process_execs: list[NeuProcessExec] = []
            for process_idx, process in enumerate(step_config["processes"]):
                step_extra_parameters: dict[str, dict[str, any]] = step_config["extra_parameters"][process_idx]
                extra_env_vars: dict[str, str] = step_extra_parameters.get("environment_variables", {})
                extra_binds: dict[str, str] = step_extra_parameters.get("bind_paths", {})
                for (subjects, sessions) in subject_session_pairs:
                    # Merge BIDS filters for the current process
                    merged_bids_filters: dict = step_config["bids_filters"].copy()
                    merged_bids_filters["subject"] = subjects
                    merged_bids_filters["session"] = sessions
                    
                    proc_exec: NeuProcessExec = NeuProcessExec.generate_from_process(process)
                    proc_exec.set_env_var_value("BIDS_FILTERS", json.dumps(merged_bids_filters))
                    
                    for key, value in extra_env_vars.items():
                        proc_exec.set_env_var_value(key, value)
                    for key, value in extra_binds.items():
                        proc_exec.set_bind_path_value(key, value)
                    step_process_execs.append(proc_exec)
                    
            step: NeuPipelineStep = NeuPipelineStep(
                name=steps_info[step_id][0],
                description=steps_info[step_id][1],
                process_execs=step_process_execs
            )
            steps.append(step)

        pipeline: NeuPipeline = NeuPipeline(
            about=about_pipeline,
            bids_root=Path(bids_root),
            steps=steps,
            scheduler=scheduler,
        )
        
        pipeline.apply_standard_exec_params(starting_scope=starting_scope, execution_mode=execution_mode)
        
        if len(pipeline.get_missing_configs()) > 0:
            print("Pipeline Missing Configurations:", pipeline.get_missing_configs())
            raise ValueError(f"Pipeline construction failed due to missing configurations: {pipeline.get_missing_configs()}")
        
        if verify_environment:
            # Verify that each unique process has the required environment (container image or venv)
            unique_process_ids: Set[str] = set([proc_exec.process.process_id for proc_exec in pipeline.process_execs])
            for unique_proc_id in unique_process_ids:
                process: NeuProcess = NeuProcess.from_process_id(unique_proc_id, username=username)
                if execution_mode == ExecutionMode.CONTAINER:
                    image_path: Path = NeuroAnalystPaths(username=username).get_process_image_path(unique_proc_id)
                    if not image_path.exists():
                        raise ValueError(f"Process ID '{unique_proc_id}' does not have a container image")
                elif execution_mode == ExecutionMode.VENV:
                    venv_path: Path = NeuroAnalystPaths(username=username).get_venv_path(unique_proc_id)
                    if not venv_path.exists() or (venv_path / "bin" / "activate").exists() is False:
                        raise ValueError(f"Process ID '{unique_proc_id}' does not have a virtual environment")
                else:
                    raise ValueError(f"Invalid execution mode: {execution_mode}")
        
        print(f"Constructed NeuPipeline with {len(pipeline.steps)} steps and {len(pipeline.process_execs)} process executions.")
        
        return pipeline
               
    
    @classmethod
    def constructor(
        cls,
        about_pipeline: About | dict,
        bids_root: str | Path,
        step_defs: List[List[str | List[str]]],
        starting_bids_filters: dict[str, str],
        execution_mode: str | ExecutionMode,
        scheduler: HPCScheduler,
        starting_scope: str = "raw"
    ):
        """
        Construct a NeuPipeline instance from high-level definitions.
        ! Not maintained, use constructor_v2 instead.
        Args:
            about_pipeline (About | dict): Metadata about the pipeline. If dict, requires keys: name, description, version, author.
            bids_root (str | Path): Path to the BIDS dataset root directory.
            step_defs (List[List[str | List[str]]]): List of steps, each defined by [name, description, process_ids].
            starting_bids_filters (dict): BIDS filters to apply to the first step.
            execution_mode (ExecutionMode): Execution mode for all processes (CONTAINER or VENV).
            starting_scope (str): Scope to use for the first step.
            scheduler (HPCScheduler): HPC scheduler to use for all processes.
            
        Returns:
            NeuPipeline: The constructed NeuPipeline instance.
        """
        # Define default scheduler flags for each scheduler
        default_scheduler_flags = {
            HPCScheduler.LSF : {"-n": 2, "-q": "medium", "-M": "20GB", "-W": "12:00"},
            HPCScheduler.SLURM : {"--cpus-per-task": 2, "--partition": "medium", "--mem": "20G", "--time": "12:00:00"},
            HPCScheduler.PBS : {"-l": "nodes=1:ppn=2,mem=20gb,walltime=12:00:00", "-q": "medium"},
            HPCScheduler.LOCAL : {}
        }
        bids_root: str = str(bids_root)
        execution_mode: ExecutionMode = execution_mode if isinstance(execution_mode, ExecutionMode) else ExecutionMode(execution_mode)
        
        # Validate structure of step_defs
        paths = NeuroAnalystPaths()
        for step_idx, step_def in enumerate(step_defs):
            if len(step_def) != 3:
                raise ValueError(f"Step {step_idx} must contain exactly 3 elements: Name, Description, Process IDs")
            if not all(isinstance(item, str) for item in step_def[:2]):
                raise ValueError(f"Step {step_idx} name and description must be strings")
            if not all(isinstance(item, (str, list)) for item in step_def[2]):
                raise ValueError(f"Step {step_idx} process IDs must be strings or lists of strings")
            # Check if all process IDs in the step are unique and exist
            if len(step_def[2]) != len(set(step_def[2])):
                print(f"Step definition: {step_def}")
                raise ValueError(f"Step {step_idx} contains duplicate process IDs")
            # Check if all process IDs are unique in the step
            if len(step_def[2]) != len(set(step_def[2])):
                raise ValueError(f"Step {step_idx} contains duplicate process IDs")
            # Check if all process IDs exist
            for proc_id in step_def[2]:
                if not paths.get_process_workdir(proc_id).exists():
                    raise ValueError(f"Process ID '{proc_id}' in step {step_idx} does not exist")
            
        bids_layout: BIDSLayout = BIDSLayout(bids_root, derivatives=True)
        about_pipeline: About = About.model_validate(about_pipeline) if isinstance(about_pipeline, dict) else about_pipeline
        
        steps: List[NeuPipelineStep] = []
        for step_idx, step_def in enumerate(step_defs):
            step_name, step_description, process_ids = step_def
            step_proc_execs: list[NeuProcessExec] = []
            bids_filters: dict = starting_bids_filters
            for proc_id in process_ids:
                process: NeuProcess = NeuProcess.from_process_id(proc_id)
                if execution_mode == ExecutionMode.CONTAINER:
                    # Check if process image exists
                    if not paths.get_process_image_path(proc_id).exists():
                        raise ValueError(f"Process ID '{proc_id}' does not have a container image")
                elif execution_mode == ExecutionMode.VENV:
                    # Check if process venv exists
                    if not paths.get_venv_path(proc_id).exists():
                        raise ValueError(f"Process ID '{proc_id}' does not have a virtual environment")
                else:
                    raise ValueError(f"Invalid execution mode: {execution_mode}")
                
                # Apply BIDS filters to all processes.
                process_execs: list[NeuProcessExec] = NeuProcessExec.spawn_optimized_execs(process, bids_filters, bids_layout)
                for proc_exec in process_execs:
                    # Set scope in BIDS filters
                    bids_filters_str: str = proc_exec.env_var_values.get("BIDS_FILTERS", "{}")
                    bids_filters: dict = json.loads(bids_filters_str) if bids_filters_str else {}
                    if "scope" in bids_filters:
                        raise ValueError(f"'scope' should not be set in BIDS filters for process exec {proc_exec.exec_id}. It is handled separately.")
                    if step_idx == 0:
                        # First step - use starting_scope
                        bids_filters["scope"] = starting_scope
                    else:
                        bids_filters["scope"] = about_pipeline.name
                    proc_exec.set_env_var_value("BIDS_FILTERS", json.dumps(bids_filters))
                    
                    # Set default scheduler flags if not already set
                    if not proc_exec.scheduler_flags:
                        proc_exec.set_scheduler_flags(default_scheduler_flags[scheduler])
                        
                    # Set /data bind path if not already set
                    if "/data" not in proc_exec.bind_path_values:
                        proc_exec.set_bind_path_value("/data", bids_root)

                    # Set execution mode
                    proc_exec.execution_mode = execution_mode

                    step_proc_execs.append(proc_exec)
                
                # Update bids_filters for the next process in the step
                # Assume that the output scope of the current process becomes the input scope for the next
                first_proc_id: NeuProcess = NeuProcess.from_process_id(process_ids[0])
                bids_filters = first_proc_id.process_dir.logic.output_entities if first_proc_id.process_dir and first_proc_id.process_dir.logic else {}
            
            step: NeuPipelineStep = NeuPipelineStep(
                name=step_name,
                description=step_description,
                process_execs=step_proc_execs
            )
            steps.append(step)
            
        pipeline: NeuPipeline = NeuPipeline(
            about=about_pipeline,
            steps=steps,
            scheduler=scheduler,
            bids_root=bids_root
        )
        return pipeline
    
    def delete(self, delete_execs: bool = False) -> None:
        """
        Delete the pipeline directory and all its contents.
        Optionally delete all associated NeuProcessExec instances.
        
        Args:
            delete_execs (bool): Whether to delete all associated NeuProcessExec instances
        """
        for process_exec in self.process_execs:
            if delete_execs:
                process_exec.delete()
        
        if self.pipeline_dir_path.exists():
            for item in self.pipeline_dir_path.iterdir():
                if item.is_dir():
                    for subitem in item.rglob('*'):
                        if subitem.is_file():
                            subitem.unlink()
                    item.rmdir()
                else:
                    item.unlink()
            self.pipeline_dir_path.rmdir()
                
    def add_step(self, step: NeuPipelineStep) -> None:
        """Add a NeuPipelineStep instance to the pipeline."""
        if not isinstance(step, NeuPipelineStep):
            raise TypeError("step must be an instance of NeuPipelineStep")
        self.steps.append(step)

    def get_missing_bind_paths(self, by: Literal["process_id", "step_idx"] = "process_id") -> Dict[str, Set[str]]:
        """
        Get a dictionary of missing bind-mount paths for each process execution in the pipeline.
        
        Args:
            by: Whether to return missing paths by 'process_id' or 'step_idx'
            
        Returns:
            Dict[str, Set[str]]: A dictionary mapping process IDs or step indices to sets of missing bind paths
        """
        missing_paths: Dict[str, Set[str]] = {}
        for step_idx, step in enumerate(self.steps):
            for proc_exec in step.process_execs:
                config: dict = proc_exec.get_configuration_status()
                missing: List[str] = config.get("bind_paths", {}).get("missing", [])
                if missing:
                    key: str = proc_exec.process.process_id if by == "process_id" else str(step_idx)
                    if key not in missing_paths:
                        missing_paths[key] = set()
                    missing_paths[key].update(missing)
        return missing_paths
    
    def get_missing_env_vars(self, by: Literal["process_id", "step_idx"] = "process_id") -> Dict[str, Set[str]]:
        """
        Get a dictionary of missing environment variables for each process execution in the pipeline.
        
        Args:
            by: Whether to return missing env vars by 'process_id' or 'step_idx'
            
        Returns:
            Dict[str, Set[str]]: A dictionary mapping process IDs or step indices to sets of missing env vars
        """
        missing_vars: Dict[str, Set[str]] = {}
        for step_idx, step in enumerate(self.steps):
            for proc_exec in step.process_execs:
                config: dict = proc_exec.get_configuration_status()
                missing: List[str] = config.get("environment_variables", {}).get("missing", [])
                if missing:
                    key: str = proc_exec.process.process_id if by == "process_id" else str(step_idx)
                    if key not in missing_vars:
                        missing_vars[key] = set()
                    missing_vars[key].update(missing)
        return missing_vars
    
    def get_missing_scheduler_flags(self, by: Literal["process_id", "step_idx"] = "process_id") -> Dict[str, Set[str]]:
        """
        Get a dictionary of missing scheduler flags for each process execution in the pipeline.
        
        Args:
            by: Whether to return missing scheduler flags by 'process_id' or 'step_idx'
            
        Returns:
            Dict[str, Set[str]]: A dictionary mapping process IDs or step indices to sets of missing scheduler flags
        """
        missing_flags: Dict[str, Set[str]] = {}
        for step_idx, step in enumerate(self.steps):
            for proc_exec in step.process_execs:
                config: dict = proc_exec.get_configuration_status()
                missing: List[str] = config.get("scheduler_flags", {}).get("missing", [])
                if missing:
                    key: str = proc_exec.process.process_id if by == "process_id" else str(step_idx)
                    if key not in missing_flags:
                        missing_flags[key] = set()
                    missing_flags[key].update(missing)
        return missing_flags
    
    def get_missing_configs(self, by: Literal["process_id", "step_idx", "process_exec_id"] = "process_id") -> Dict[str, Dict[str, Set[str]]]:
        """
        Get a dictionary of all missing configurations (bind paths, env vars, scheduler flags)
        for each process execution in the pipeline.
        
        Args:
            by: Whether to return missing configs by 'process_id' or 'step_idx'
            
        Returns:
            Dict[str, Dict[str, Set[str]]]: A dictionary mapping process IDs or step indices to
            dictionaries of missing configuration types and their corresponding sets of missing items.
        """
        missing_configs: Dict[str, Dict[str, Set[str]]] = {}
        for step_idx, step in enumerate(self.steps):
            for proc_exec in step.process_execs:
                config: dict = proc_exec.get_configuration_status()
                missing: Dict[str, List[str]] = {
                    "bind_paths": config.get("bind_paths", {}).get("missing", []),
                    "environment_variables": config.get("environment_variables", {}).get("missing", []),
                    "scheduler_flags": config.get("scheduler_flags", {}).get("missing", [])
                }
                if any(missing.values()):
                    key: str = proc_exec.process.process_id if by == "process_id" else str(step_idx)
                    if key not in missing_configs:
                        missing_configs[key] = {}
                    for config_type, items in missing.items():
                        if items:
                            if config_type not in missing_configs[key]:
                                missing_configs[key][config_type] = set()
                            missing_configs[key][config_type].update(items)
        return missing_configs
    
    def add_bind_path(self, container_path: str, host_path: str, process_id: Optional[str] = None,step_idx: Optional[int] = None, exec_id: Optional[str] = None) -> None:
        """
        Add a bind-mount path to a specific process execution in a step.
        
        Args:
            container_path: The path inside the container
            host_path: The path on the host machine
            process_id: The ID of the process to modify. If None, use step_idx and exec_id.
            step_idx: The index of the step in the pipeline. If None, apply to all steps.
            exec_id: The execution ID of the specific process to modify. If None and step_ids is not None, apply to all processes in the step.
            
        Raises:
            IndexError: If step_idx is out of range
            ValueError: If exec_id is not found in the specified step
        """
        if process_id is not None:
            # Apply to all process execs with the given process_id
            proc_execs: list[NeuProcessExec] = []
            for step in self.steps:
                for proc_exec in step.process_execs:
                    if proc_exec.process.process_id == process_id:
                        proc_execs.append(proc_exec)
            if not proc_execs:
                raise ValueError(f"process_id '{process_id}' not found in the pipeline")
            for proc_exec in proc_execs:
                proc_exec.set_bind_path_value(container_path, host_path)
            return

        if step_idx is not None:
            if step_idx < 0 or step_idx >= len(self.steps):
                raise IndexError("step_idx out of range")

        # If step_idx is None, apply to all steps
        if step_idx is None:
            for idx in range(len(self.steps)):
                self.add_bind_path(container_path, host_path, idx, exec_id)
            return
        
        step: NeuPipelineStep = self.steps[step_idx]
        
        # If exec_id is None, add the bind path to all process execs in the step
        if exec_id is None:
            for proc_exec in step.process_execs:
                proc_exec.set_bind_path_value(container_path, host_path)
            return
        for proc_exec in step.process_execs:
            if proc_exec.exec_id == exec_id:
                proc_exec.set_bind_path_value(container_path, host_path)
                return
        raise ValueError(f"exec_id '{exec_id}' not found in step {step_idx}")
    
    def add_env_var(self, var_name: str, var_value: str, process_id: Optional[str] = None, step_idx: Optional[int] = None, exec_id: Optional[str] = None) -> None:
        """
        Add an environment variable to a specific process execution in a step.
        
        Args:
            var_name: The name of the environment variable.
            var_value: The value of the environment variable to set.
            process_id: The ID of the process to modify. If None, use step_idx and exec_id.
            step_idx: The index of the step in the pipeline. If None, apply to all steps.
            exec_id: The execution ID of the specific process to modify. If None and step_ids is not None, apply to all processes in the step.
            
        Raises:
            IndexError: If step_idx is out of range
            ValueError: If exec_id is not found in the specified step
        """
        if process_id is not None:
            # Apply to all process execs with the given process_id
            proc_execs: list[NeuProcessExec] = []
            for step in self.steps:
                for proc_exec in step.process_execs:
                    if proc_exec.process.process_id == process_id:
                        proc_execs.append(proc_exec)
            if not proc_execs:
                raise ValueError(f"process_id '{process_id}' not found in the pipeline")
            for proc_exec in proc_execs:
                proc_exec.set_env_var_value(var_name, var_value)
            return

        if step_idx is not None:
            if step_idx < 0 or step_idx >= len(self.steps):
                raise IndexError("step_idx out of range")
        
        # If step_idx is None, apply to all steps
        if step_idx is None:
            for idx in range(len(self.steps)):
                self.add_env_var(var_name, var_value, idx, exec_id)
            return
        
        step: NeuPipelineStep = self.steps[step_idx]
        
        # If exec_id is None, add the env var to all process execs in the step
        if exec_id is None:
            for proc_exec in step.process_execs:
                proc_exec.set_env_var_value(var_name, var_value)
            return
        for proc_exec in step.process_execs:
            if proc_exec.exec_id == exec_id:
                proc_exec.set_env_var_value(var_name, var_value)
                return
        raise ValueError(f"exec_id '{exec_id}' not found in step {step_idx}")

    def add_scheduler_flags(self, flags: dict, process_id: Optional[str] = None, step_idx: Optional[int] = None, exec_id: Optional[str] = None) -> None:
        """
        Add scheduler flags to a specific process execution in a step.
        
        Args:
            flags: A dictionary of scheduler flags to set
            process_id: The ID of the process to modify. If None, use step_idx and exec_id.
            step_idx: The index of the step in the pipeline. If None, apply to all steps.
            exec_id: The execution ID of the specific process to modify. If None and step_ids is not None, apply to all processes in the step.
            
        Raises:
            IndexError: If step_idx is out of range
            ValueError: If exec_id is not found in the specified step
        """
        if process_id is not None:
            # Apply to all process execs with the given process_id
            proc_execs: list[NeuProcessExec] = []
            for step in self.steps:
                for proc_exec in step.process_execs:
                    if proc_exec.process.process_id == process_id:
                        proc_execs.append(proc_exec)
            if not proc_execs:
                raise ValueError(f"process_id '{process_id}' not found in the pipeline")
            for proc_exec in proc_execs:
                proc_exec.set_scheduler_flags(flags)
            return
        
        if step_idx is not None:
            if step_idx < 0 or step_idx >= len(self.steps):
                raise IndexError("step_idx out of range")
        
        # If step_idx is None, apply to all steps
        if step_idx is None:
            for idx in range(len(self.steps)):
                self.add_scheduler_flags(flags, idx, exec_id)
            return
        
        step: NeuPipelineStep = self.steps[step_idx]
        
        # If exec_id is None, add the flags to all process execs in the step
        if exec_id is None:
            for proc_exec in step.process_execs:
                proc_exec.set_scheduler_flags(flags)
            return
        for proc_exec in step.process_execs:
            if proc_exec.exec_id == exec_id:
                proc_exec.set_scheduler_flags(flags)
                return
        raise ValueError(f"exec_id '{exec_id}' not found in step {step_idx}")

    def apply_configuration(
            self, 
            process_id: Optional[str] = None, 
            step_idx: Optional[int] = None, 
            exec_id: Optional[str] = None, 
            bind_paths: Optional[Dict[str, str]] = None,
            env_vars: Optional[Dict[str, str]] = None,
            scheduler_flags: Optional[Dict[str, str]] = None
        ) -> None:
        """
        Apply configuration settings to a specific process execution in a step. Overwrites existing settings.
        Args:
            process_id: The ID of the process to modify. If None, use step_idx and exec_id.
            step_idx: The index of the step in the pipeline. If None, apply to all steps.
            exec_id: The execution ID of the specific process to modify. If None and step_ids is not None, apply to all processes in the step.
            bind_paths: A dictionary of bind-mount paths to set
            env_vars: A dictionary of environment variables to set
            scheduler_flags: A dictionary of scheduler flags to set
        """
        if bind_paths:
            for container_path, host_path in bind_paths.items():
                self.add_bind_path(container_path, host_path, process_id, step_idx, exec_id)
        if env_vars:
            for key, value in env_vars.items():
                self.add_env_var(key, value, process_id, step_idx, exec_id)
        if scheduler_flags:
            self.add_scheduler_flags(scheduler_flags, step_idx, exec_id, process_id)
    
    @staticmethod
    def get_available_scopes(bids_root: Path | str) -> Set[str]:
        """Get the set of available scopes in the BIDS dataset."""
        available_scopes: Set[str] = {"raw", "derivatives"}
        # Get all pipeline names in the bids_layout derivatives
        derivative_pipeline_names: Set[str] = set()
        bids_layout: BIDSLayout = BIDSLayout(str(bids_root), derivatives=True)
        for ds in bids_layout.derivatives:
            derivative_pipeline_names.add(ds.replace("derivatives/", ""))
        available_scopes.update(derivative_pipeline_names)
        
        return available_scopes
    
    @staticmethod
    def is_scope_valid(scope: str, bids_root: Path | str) -> bool:
        """Check if a given scope is valid in the BIDS dataset."""
        available_scopes: Set[str] = NeuPipeline.get_available_scopes(bids_root)
        
        return scope in available_scopes
    
    def apply_standard_exec_params(self) -> None:
        """Apply standard execution parameters to all processes in the pipeline."""
        
        if not self.is_scope_valid(self.starting_bids_scope, self.bids_root):
            raise ValueError(f"starting_scope '{self.starting_bids_scope}' is not valid in the BIDS dataset")
        for step_idx, step in enumerate(self.steps):
            for proc_exec in step.process_execs:
                if step_idx == 0:
                    bids_filters_str: str = proc_exec.env_var_values.get("BIDS_FILTERS", "{}")
                    bids_filters: dict = json.loads(bids_filters_str) if bids_filters_str else {}
                    bids_filters["scope"] = self.starting_bids_scope
                    proc_exec.set_env_var_value("BIDS_FILTERS", json.dumps(bids_filters))
                else:
                    bids_filters_str: str = proc_exec.env_var_values.get("BIDS_FILTERS", "{}")
                    bids_filters: dict = json.loads(bids_filters_str) if bids_filters_str else {}
                    bids_filters["scope"] = self.about.name # This scope is not expected to be currently available. It will be created as the pipeline runs.
                    proc_exec.set_env_var_value("BIDS_FILTERS", json.dumps(bids_filters))
                
                # Apply the pipeline's scheduler to each process exec
                proc_exec.scheduler = self.scheduler
                
                # Set standard environment variables - PIPELINE_NAME, PIPELINE_ID, PROCESS_ID, PROCESS_EXEC_ID
                proc_exec.set_env_var_value("PIPELINE_NAME", self.about.name)
                proc_exec.set_env_var_value("PIPELINE_ID", self.pipeline_id)
                proc_exec.set_env_var_value("PROCESS_ID", proc_exec.process.process_id)
                proc_exec.set_env_var_value("PROCESS_EXEC_ID", proc_exec.exec_id)
                
                # Set standard bind-mount paths - /data, 
                proc_exec.set_bind_path_value("/data", str(self.bids_root))
                
                # Check if all the required configuration is set
                if not proc_exec.check_configuration_complete():
                    print(f"WARNING: ProcessExec {proc_exec.exec_id} in step '{step.name}' is missing configuration.")
                else:
                    proc_exec.generate_command()
                    # print(f"ProcessExec {proc_exec.exec_id} in step '{step.name}' is fully configured.")
    
    def create_pipeline_dir(self) -> Path:
        """Create the pipeline directory structure."""
        # Create the main pipeline directory
        pipeline_dir = self.pipeline_dir_path
        pipeline_dir.mkdir(parents=True, exist_ok=False)
        
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
            
            lines.append("Process Executions:")
            for j, proc_exec in enumerate(step.process_execs):
                lines.append(f"- **Process Execution {j+1}:** {proc_exec.exec_id}")
        
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
    
    def pre_execution(self) -> None:
        """Perform any necessary actions before executing the first step."""
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
                self.logger.info(f"Created dataset_description.json at {dataset_description_path}")

    @staticmethod
    def load_metrics(filepath: str, numeric_only: bool = False, allow_nested: bool = True) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Load metrics from a sidecar file and provide associated metadata such as -
            - function name
            - process ID
            - process exec ID
            - processing time
            - processing date
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
        separator: str = "."
        try:
            with open(filepath, "r") as f:
                data: dict = json.load(f)
                if "metrics" in data and isinstance(data["metrics"], dict):
                    file_metrics = data["metrics"]
                    file_metrics = flatten_dict(file_metrics, sep=separator) if allow_nested else file_metrics
                    # Add a 'metric' prefix to each metric name to avoid collisions
                    file_metrics = {f"metric{separator}{k}": v for k, v in file_metrics.items()}
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
                        "input_file": data.get("InputFile", ""),
                        "output_file": data.get("OutputFile", ""),
                        **bids_entities
                    }
        except Exception as e:
            print(f"Error loading metrics from {filepath}: {e}")

        return metrics, about
    
    @staticmethod
    def aggregate_metrics(sidecar_filepaths: list[str | Path]) -> pd.DataFrame:
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
            metrics, about = NeuPipeline.load_metrics(str(filepath), numeric_only=True)
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
                    sheet_name = f"{step.name[:20]}-{process_name[:20]}".replace(" ", "_")
                    df_merged.to_excel(writer, sheet_name=sheet_name, index=False)
                    
        return summary_path
    
    def post_execution(self) -> None:
        """Perform any necessary actions after executing all steps.
        """
        # Generate summary report
        summary_path = self.generate_summary()
        self.logger.info(f"Generated pipeline summary at {summary_path}")
        
        # Print final status
        self.print_pipeline_status()

    async def async_execute_via_python(self, resume: bool = True) -> str:
        """Asynchronously execute the pipeline step-by-step via Python.
        
        Args:
            resume: If True, resume execution from the last successful step.
        Returns:
            str: A message indicating the result of the execution.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute_via_python, resume)
    
    def execute_via_python(self, resume: bool = True) -> str:
        """Execute the pipeline step-by-step via Python.
        
        Args:
            resume: If True, resume execution from the last successful step.
        Returns:
            str: A message indicating the result of the execution.
        """
        # Ensure pipeline directory and bash script exist
        if not self.script_path.exists():
            self.create_pipeline_dir()
            
        # Ensure all environments are created
        for step in self.steps:
            checked_processes = set()
            for proc_exec in step.process_execs:
                if proc_exec.execution_mode == ExecutionMode.CONTAINER:
                    if proc_exec.process.process_id not in checked_processes:
                        if not proc_exec.process.is_image_built():
                            raise RuntimeError(f"Container image for process {proc_exec.process.process_id} is not built. Please build the image before execution.")
                        checked_processes.add(proc_exec.process.process_id)
                    elif proc_exec.execution_mode == ExecutionMode.VENV:
                        if proc_exec.process.process_id not in checked_processes:
                            if not proc_exec.process.is_venv_created():
                                raise RuntimeError(f"Virtual environment for process {proc_exec.process.process_id} is not created. Please create the venv before execution.")
                            checked_processes.add(proc_exec.process.process_id)

        logger: logging.Logger = self.logger
        
        self.pre_execution()

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
            
            def execute_and_monitor_process(proc_exec: NeuProcessExec) -> bool:
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
        
        self.post_execution()
            
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
    def from_pipeline_id(cls, pipeline_id: str, username: Optional[str] = None) -> 'NeuPipeline':
        """Create a NeuPipeline instance from a pipeline ID."""
        paths = NeuroAnalystPaths(username=username)
        model_path = Path(paths.pipelines) / pipeline_id / "model.json"
        
        return cls.from_model_file(model_path)
    
    @classmethod
    def get_all_pipelines(cls, username: Optional[str]) -> list['NeuPipeline']:
        """List all available pipelines."""
        paths = NeuroAnalystPaths(username=username)
        pipelines_dir: Path = paths.pipelines
        
        pipeline_list = []
        if pipelines_dir.exists():
            for pipeline_dir in pipelines_dir.iterdir():
                if pipeline_dir.is_dir():
                    try:
                        pipeline = cls.from_pipeline_id(pipeline_dir.name, username=username)
                        pipeline_list.append(pipeline)
                    except Exception as e:
                        print(f"Warning: Could not load pipeline from {pipeline_dir}: {e}")
        
        return pipeline_list
