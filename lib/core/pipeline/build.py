from ..process.create import ProcessExec
from ..process.test import check_process_exec_status
from ...utils.db import Connection, insert_to_db, update_db_record, find_one_from_db
from ...utils.constants import COLLECTION_PIPELINES
from ...utils.generate import generate_id

from typing import Optional
from enum import Enum
import asyncio
import time
from asyncio import sleep

from pydantic import BaseModel, Field

class PipelineStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class PipelineStep(BaseModel):
    id: str = Field(title="The ID of the pipeline step.", default_factory=lambda: generate_id("PS", 6, "-"))
    name: str = Field(title="The name of the pipeline step.")
    process_execs: list[ProcessExec] = Field(title="List of process execution plans.")
    status: PipelineStatus = Field(title="The status of the pipeline step.", default=PipelineStatus.CREATED)
    
    def execute(self):
        self.status = PipelineStatus.RUNNING
        
        # Trigger run all processes in parallel
        for process_exec in self.process_execs:
            try:
                process_exec.execute()
            except Exception as e:
                self.status = PipelineStatus.FAILED
                raise Exception(f"Failed to execute process execution {process_exec.id}. Error: {e}")
        
        # Monitor for all processes to complete
        while self.status == PipelineStatus.RUNNING:
            print(f"Checking status of process execution {process_exec.id} for {self.id}")
            time.sleep(5)
            process_exec_statuses = [check_process_exec_status(process_exec.id)["status"] for process_exec in self.process_execs]
            if "FAILED" in process_exec_statuses:
                print(f"Process execution FAILED for {self.id}")
                self.status = PipelineStatus.FAILED
            elif all([status == "COMPLETED" for status in process_exec_statuses]):
                print(f"Process execution COMPLETED for {self.id}")
                self.status = PipelineStatus.COMPLETED
        
        # Copy summaries to database
        for process_exec in self.process_execs:
            process_exec.copy_summaries_to_db()

class Pipeline(BaseModel):
    id: str = Field(title="The ID of the pipeline.", default_factory=lambda: generate_id("PL", 6, "-"))
    name: str = Field(title="The name of the pipeline.")
    description: str = Field(title="The description of the pipeline.")
    # version: str
    steps: list[PipelineStep] = Field(title="List of pipeline steps.")
    checkpoint_steps: list[int] = Field(title="List of steps after which to pause the pipeline", default=[])
    
    def stop_all_processes(self):
        for step in self.steps:
            for process_exec in step.process_execs:
                print(f"Stopping process execution {process_exec.id}")
                process_exec.stop_container()
    
    def execute(self):
        try:
            print(f"Executing pipeline {self.id}: {self.name}")
            self.to_db()
            for i, step in enumerate(self.steps, 1):
                if step.status == PipelineStatus.FAILED:
                    raise Exception(f"Pipeline step {step.id} in {self.id} failed.")
                if step.status == PipelineStatus.COMPLETED:
                    print(f"Skipping step {i}: {step.name} as it has already completed.")
                    continue
                
                print(f"Executing step {i}: {step.name}")
                step.execute()
                
                # Stop pipeline if a step fails
                if step.status == PipelineStatus.FAILED:
                    self.update_step_status_in_db(i - 1, step.status)
                    raise Exception(f"Pipeline step {step.id} in {self.id} failed.")
                
                # Update pipeline step in database
                self.update_step_in_db(i - 1, step)
                
                # Stop pipeline if a checkpoint is reached
                if i in self.checkpoint_steps:
                    print(f"Checkpoint reached at step {i}. Pausing pipeline.")
                    return
            
            print(f"Pipeline {self.id} completed successfully.")
        
        except KeyboardInterrupt:
            print(f"Pipeline {self.id} interrupted.")
            # Kill all Docker containers
            self.stop_all_processes()
        
    def from_db(self, pipeline_id: str, connection: Optional[Connection] = None):
        pipeline_dict = find_one_from_db(COLLECTION_PIPELINES, {"id": pipeline_id}, connection)
        return Pipeline(**pipeline_dict)
    
    def to_db(self, connection: Optional[Connection] = None):
        insert_to_db(COLLECTION_PIPELINES, self.model_dump(mode="json"), connection)
    
    def update_step_in_db(self, step_id: str, step: PipelineStep, connection: Optional[Connection] = None):
        update_db_record(COLLECTION_PIPELINES, {"id": self.id}, {f"steps.{step_id}": step.model_dump(mode="json")}, connection)
        
    def stop_pipeline(self):
        self.stop_all_processes()
        print(f"Pipeline {self.id} stopped.")