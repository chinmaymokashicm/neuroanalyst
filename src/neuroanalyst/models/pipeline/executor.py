import subprocess, time, re
from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum

class ProcessStatus(str, Enum):
    """Status of a process execution in a pipeline."""
    NOT_STARTED = "NOT_STARTED"  # Process has not been started yet
    RUNNING = "RUNNING"          # Process is currently running
    COMPLETE = "COMPLETE"        # Process completed successfully
    FAILED = "FAILED"            # Process failed with an error

class BaseExecutor(ABC):
    def __init__(self, cmd: str):
        self.cmd = cmd
        self.job_id: Optional[str] = None
        self.status: Optional[ProcessStatus] = ProcessStatus.NOT_STARTED

    @abstractmethod
    def submit(self): ...
    @abstractmethod
    def poll_status(self): ...
    @abstractmethod
    def is_done(self) -> bool: ...
    @abstractmethod
    def is_success(self) -> bool: ...

    def wait_until_done(self, poll_interval=10):
        """Waits for job to complete, polling scheduler."""
        while not self.is_done():
            time.sleep(poll_interval)
        return self.is_success()

class LSFExecutor(BaseExecutor):
    def submit(self):
        result = subprocess.run(self.cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"LSF submission failed: {result.stderr}")
        match = re.search(r"Job <(\d+)> is submitted", result.stdout)
        if not match:
            raise RuntimeError(f"Could not parse job ID from LSF output: {result.stdout}")
        self.job_id = match.group(1)
        self.status = ProcessStatus.RUNNING

    def poll_status(self):
        if not self.job_id:
            raise RuntimeError("Job ID is not set. Cannot poll status.")
        poll_cmd = f"bjobs -noheader {self.job_id}"
        result = subprocess.run(poll_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            self.status = ProcessStatus.FAILED
            return
        if "DONE" in result.stdout:
            self.status = ProcessStatus.COMPLETE
        elif "EXIT" in result.stdout:
            self.status = ProcessStatus.FAILED
        elif "RUN" in result.stdout:
            self.status = ProcessStatus.RUNNING
        else:
            self.status = ProcessStatus.NOT_STARTED

    def is_done(self) -> bool:
        return self.status in (ProcessStatus.COMPLETE, ProcessStatus.FAILED)

    def is_success(self) -> bool:
        if self.status == ProcessStatus.COMPLETE:
            return True
        elif self.status == ProcessStatus.FAILED:
            return False
        else:
            raise RuntimeError("Job is not yet complete. Cannot determine success.")
        
class SLURMExecutor(BaseExecutor):
    def submit(self):
        result = subprocess.run(self.cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"SLURM submission failed: {result.stderr}")
        match = re.search(r"Submitted batch job (\d+)", result.stdout)
        if not match:
            raise RuntimeError(f"Could not parse job ID from SLURM output: {result.stdout}")
        self.job_id = match.group(1)
        self.status = ProcessStatus.RUNNING

    def poll_status(self):
        if not self.job_id:
            raise RuntimeError("Job ID is not set. Cannot poll status.")
        poll_cmd = f"sacct -j {self.job_id} --format=State --noheader"
        result = subprocess.run(poll_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            self.status = ProcessStatus.FAILED
            return
        state = result.stdout.strip()
        if "COMPLETED" in state:
            self.status = ProcessStatus.COMPLETE
        elif "FAILED" in state or "CANCELLED" in state or "TIMEOUT" in state:
            self.status = ProcessStatus.FAILED
        elif "RUNNING" in state or "PENDING" in state:
            self.status = ProcessStatus.RUNNING
        else:
            self.status = ProcessStatus.NOT_STARTED

    def is_done(self) -> bool:
        return self.status in (ProcessStatus.COMPLETE, ProcessStatus.FAILED)

    def is_success(self) -> bool:
        if self.status == ProcessStatus.COMPLETE:
            return True
        elif self.status == ProcessStatus.FAILED:
            return False
        else:
            raise RuntimeError("Job is not yet complete. Cannot determine success.")

class PBSExecutor(BaseExecutor):
    def submit(self):
        result = subprocess.run(self.cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"PBS submission failed: {result.stderr}")
        match = re.search(r"(\d+)\.server", result.stdout)
        if not match:
            raise RuntimeError(f"Could not parse job ID from PBS output: {result.stdout}")
        self.job_id = match.group(1)
        self.status = ProcessStatus.RUNNING

    def poll_status(self):
        if not self.job_id:
            raise RuntimeError("Job ID is not set. Cannot poll status.")
        poll_cmd = f"qstat -f {self.job_id}"
        result = subprocess.run(poll_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            self.status = ProcessStatus.FAILED
            return
        if "job_state = C" in result.stdout:
            self.status = ProcessStatus.COMPLETE
        elif "job_state = F" in result.stdout:
            self.status = ProcessStatus.FAILED
        elif "job_state = R" in result.stdout:
            self.status = ProcessStatus.RUNNING
        elif "job_state = Q" in result.stdout:
            self.status = ProcessStatus.NOT_STARTED
        else:
            self.status = ProcessStatus.NOT_STARTED

    def is_done(self) -> bool:
        return self.status in (ProcessStatus.COMPLETE, ProcessStatus.FAILED)

    def is_success(self) -> bool:
        if self.status == ProcessStatus.COMPLETE:
            return True
        elif self.status == ProcessStatus.FAILED:
            return False
        else:
            raise RuntimeError("Job is not yet complete. Cannot determine success.")
        
class LocalExecutor(BaseExecutor):
    def submit(self):
        self.process = subprocess.Popen(self.cmd, shell=True)
        self.status = ProcessStatus.RUNNING

    def poll_status(self):
        if self.process.poll() is None:
            self.status = ProcessStatus.RUNNING
        elif self.process.returncode == 0:
            self.status = ProcessStatus.COMPLETE
        else:
            self.status = ProcessStatus.FAILED

    def is_done(self) -> bool:
        return self.status in (ProcessStatus.COMPLETE, ProcessStatus.FAILED)

    def is_success(self) -> bool:
        if self.status == ProcessStatus.COMPLETE:
            return True
        elif self.status == ProcessStatus.FAILED:
            return False
        else:
            raise RuntimeError("Job is not yet complete. Cannot determine success.")