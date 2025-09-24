"""
NeuroAnalyst Constants Module

This module defines all the constants and environment variables used throughout
the NeuroAnalyst framework. These constants are primarily derived from environment
variables set by the setup.sh and set_envs.sh scripts.

The environment variables define the directory structure and paths for:
- Singularity/Apptainer images (base and process images)
- Working directories for temporary files
- Report outputs
- Logs
- BIDS datasets
- Documentation
"""

import os
from pathlib import Path
from typing import Optional


class NeuroAnalystPaths:
    """
    Central configuration class for all NeuroAnalyst paths and directories.
    
    This class reads environment variables set by the setup process and provides
    easy access to all important directories used by the framework.
    """
    
    def __init__(self):
        # Base home directory for NeuroAnalyst
        self._home = os.getenv('NEUROANALYST_HOME', os.path.expanduser('~/neuroanalyst'))
        
        # Core directories
        self._images = os.getenv('NEUROANALYST_IMAGES', 
                                os.path.join(self._home, 'apptainer', 'images'))
        self._docs = os.getenv('NEUROANALYST_DOCS', 
                              os.path.join(self._home, 'apptainer', 'docs'))
        self._workdir = os.getenv('NEUROANALYST_WORKDIR', 
                                 os.path.join(self._home, 'working_dirs'))
        self._pipelines = os.getenv('NEUROANALYST_PIPELINES',
                                   os.path.join(self._home, 'pipelines'))
        self._reports = os.getenv('NEUROANALYST_REPORTS', 
                                 os.path.join(self._home, 'reports'))
        self._logs = os.getenv('NEUROANALYST_LOGS', 
                              os.path.join(self._home, 'logs'))
        self._datasets = os.getenv('NEUROANALYST_DATASETS', 
                                  os.path.join(self._home, 'datasets'))
        self._venvs = os.getenv('NEUROANALYST_VENVS', 
                               os.path.join(self._home, 'virtual_environments'))
        self._process_execs = os.getenv('NEUROANALYST_PROCESS_EXECS',
                                      os.path.join(self._home, 'process_execs'))
        
        # MongoDB configuration
        self._db_host = os.getenv('NEUROANALYST_DB_HOST', 'localhost')
        self._db_port = int(os.getenv('NEUROANALYST_DB_PORT', '27017'))
        self._db_name = os.getenv('NEUROANALYST_DB_NAME', 'neuroanalyst')
    
    @property
    def home(self) -> Path:
        """Base NeuroAnalyst home directory."""
        return Path(self._home)
    
    @property
    def images(self) -> Path:
        """Directory for Singularity/Apptainer images (base and process images)."""
        return Path(self._images)
    
    @property
    def base_images(self) -> Path:
        """Directory for base Singularity images."""
        return self.images / 'base'
    
    @property
    def docs(self) -> Path:
        """Directory for Apptainer/Singularity documentation and def files."""
        return Path(self._docs)
    
    @property
    def workdir(self) -> Path:
        """Working directory for temporary files during processing."""
        return Path(self._workdir)
    
    @property
    def pipelines(self) -> Path:
        """Directory for storing pipeline scripts and related files."""
        return Path(self._pipelines)
    
    @property
    def reports(self) -> Path:
        """Directory for generated reports and outputs."""
        return Path(self._reports)
    
    @property
    def logs(self) -> Path:
        """Directory for log files."""
        return Path(self._logs)
    
    @property
    def datasets(self) -> Path:
        """Directory for BIDS datasets."""
        return Path(self._datasets)
    
    @property
    def venvs(self) -> Path:
        """Directory for virtual environments."""
        return Path(self._venvs)
    
    @property
    def process_execs(self) -> Path:
        """Directory for process execution instances."""
        return Path(self._process_execs)
    
    @property
    def db_host(self) -> str:
        """MongoDB host."""
        return self._db_host
    
    @property
    def db_port(self) -> int:
        """MongoDB port."""
        return self._db_port
    
    @property
    def db_name(self) -> str:
        """MongoDB database name."""
        return self._db_name
    
    def create_directories(self) -> None:
        """
        Create all necessary directories if they don't exist.
        
        This method ensures that all the required directory structure
        is in place for NeuroAnalyst to function properly.
        """
        directories = [
            self.home,
            self.images,
            self.base_images,
            # self.images,
            self.docs,
            self.workdir,
            self.reports,
            self.logs,
            self.datasets,
            self.venvs,
            self.process_execs
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_process_workdir(self, process_id: str) -> Path:
        """
        Get a working directory for a specific NeuProcess.
        
        Args:
            process_id: Unique identifier for the process
            
        Returns:
            Path to the process-specific working directory
        """
        return self.workdir / process_id
    
    def get_pipeline_workdir(self, pipeline_id: str) -> Path:
        """
        Get a working directory for a specific NeuPipeline.
        
        Args:
            pipeline_id: Unique identifier for the pipeline
            
        Returns:
            Path to the pipeline-specific working directory
        """
        return self.workdir / 'pipelines' / pipeline_id
    
    def get_process_image_path(self, process_name: str, version: Optional[str] = None) -> Path:
        """
        Get the path for a NeuProcess image.
        
        Args:
            process_name: Name of the process
            version: Version of the process (optional)
            
        Returns:
            Path to the process image file
        """
        if version:
            filename = f"{process_name}_v{version}.sif"
        else:
            filename = f"{process_name}.sif"
        return self.images / filename
    
    def get_base_image_path(self, base_image_name: str) -> Path:
        """
        Get the path for a base image.
        
        Args:
            base_image_name: Name of the base image
            
        Returns:
            Path to the base image file
        """
        return self.base_images / f"{base_image_name}.sif"
    
    def get_venv_path(self, process_exec_id: str) -> Path:
        """
        Get the path for a process execution virtual environment.
        
        Args:
            process_exec_id: Unique identifier for the process execution
            
        Returns:
            Path to the virtual environment directory
        """
        return self.venvs / process_exec_id
    
    def get_process_exec_path(self, exec_id: str) -> Path:
        """
        Get the path for a process execution instance.
        
        Args:
            exec_id: Unique identifier for the execution instance
            
        Returns:
            Path to the process execution directory
        """
        return self.process_execs / exec_id
    
    def get_log_file_path(self, component: str, process_id: Optional[str] = None) -> Path:
        """
        Get a log file path for a specific component.
        
        Args:
            component: Component name (e.g., 'neuprocess', 'pipeline', 'wrapper')
            process_id: Optional process/pipeline ID for specific logs
            
        Returns:
            Path to the log file
        """
        if process_id:
            filename = f"{component}_{process_id}.log"
        else:
            filename = f"{component}.log"
        return self.logs / filename


# Global instance for easy access throughout the framework
PATHS = NeuroAnalystPaths()


# Additional constants for the framework
class NeuroAnalystConfig:
    """Configuration constants for NeuroAnalyst framework."""
    
    # Singularity/Apptainer constants
    SINGULARITY_EXTENSION = '.sif'
    DEFINITION_EXTENSION = '.def'
    
    # File extensions
    PYTHON_EXTENSION = '.py'
    SHELL_EXTENSION = '.sh'
    JSON_EXTENSION = '.json'
    
    # Template file names - Simplified naming
    MAIN_TEMPLATE = 'main.py.template'
    MAIN_BULK_TEMPLATE = 'main_bulk.py.template'
    README_TEMPLATE = 'readme.md.template'
    INSTALL_TEMPLATE = 'install.sh.template'
    CONTAINER_TEMPLATE = 'container.def.template'
    EXECUTE_TEMPLATE = 'execute.sh.template'
    
    # Default file names for NeuProcess
    MAIN_SCRIPT_NAME = 'main.py'
    INSTALL_SCRIPT_NAME = 'install_requirements.sh'
    EXECUTE_SCRIPT_NAME = 'execute.sh'
    README_NAME = 'README.md'
    CONFIG_NAME = 'neuprocess_config.json'
    MODEL_DUMP_NAME = 'neuprocess_dir_model.json'
    
    # BIDS constants
    DERIVATIVES_DIR = 'derivatives'
    BIDS_SIDECAR_SUFFIX = '.json'
    
    # Processing constants
    DEFAULT_PYTHON_VERSION = '3.12'
    DEFAULT_BASE_IMAGE = 'ubuntu:22.04'
    
    # Security and permissions
    BIDS_MOUNT_MODE = 'ro'  # Read-only mount for BIDS datasets
    DERIVATIVES_MOUNT_MODE = 'rw'  # Read-write mount for derivatives
    
    # Parallel processing
    DEFAULT_N_PROCS = 4
    
    # Logging
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


# Global config instance
CONFIG = NeuroAnalystConfig()


def ensure_directories() -> None:
    """
    Ensure all required NeuroAnalyst directories exist.
    
    This function should be called during initialization to ensure
    the directory structure is properly set up.
    """
    PATHS.create_directories()


def get_template_path(template_name: str) -> Path:
    """
    Get the path to a template file.
    
    Args:
        template_name: Name of the template file
        
    Returns:
        Path to the template file
    """
    # Assuming templates are in the app/models/process/templates directory
    base_path = Path(__file__).parent.parent / 'models' / 'process' / 'templates'
    return base_path / template_name


def validate_environment() -> bool:
    """
    Validate that all required environment variables are set.
    
    Returns:
        True if all required environment variables are set, False otherwise
    """
    required_vars = [
        'NEUROANALYST_HOME',
        'NEUROANALYST_IMAGES',
        'NEUROANALYST_WORKDIR',
        'NEUROANALYST_REPORTS',
        'NEUROANALYST_LOGS',
        'NEUROANALYST_DATASETS',
        'NEUROANALYST_PROCESS_EXECS',
        'NEUROANALYST_DB_HOST',
        'NEUROANALYST_DB_PORT',
        'NEUROANALYST_DB_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Please run setup.sh to configure the environment properly.")
        return False
    
    return True


# Validate environment on import
if not validate_environment():
    print("Environment validation failed. Some features may not work correctly.")
