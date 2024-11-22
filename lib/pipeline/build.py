from ..process.create import ProcessExec
from ..process.test import check_process_exec_status
from ..utils.generate import generate_id

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

class Pipeline(BaseModel):
    id: str = Field(title="The ID of the pipeline.", default_factory=lambda: generate_id("PL", 6, "-"))
    name: str
    description: str
    # version: str
    steps: list[PipelineStep]
    
    def execute(self):
        for i, step in enumerate(self.steps, 1):
            print(f"Executing step {i}: {step.name}\n\n\n")
            step.execute()
            
            # Stop pipeline if a step fails
            if step.status == PipelineStatus.FAILED:
                self.snapshot_to_db()
                raise Exception(f"Pipeline step {step.id} failed.")
        
        print(f"Pipeline {self.id} completed successfully.")
        self.snapshot_to_db()
        
    def snapshot_to_db(self):
        with open(f"database/{self.id}.json", "w") as f:
            f.write(self.model_dump_json(indent=4))