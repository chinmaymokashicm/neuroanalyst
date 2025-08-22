"""
Core module for NeuProcessDir - creates directory structure from NeuProcessLogic.

This module provides the main functionality for wrapping NeuProcessLogic functions
into complete directory structures with scripts for parallel execution using PyBIDS.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, computed_field

from ....utils import PATHS, CONFIG, generate_available_process_id
from ..logic.core import NeuProcessLogic
from ..logic.code.python import encode_logic
from ..wrapper.core import neuprocess_decorator, NeuProcessDecoratorConfig


class NeuProcessDirConfig(BaseModel):
    """Configuration for creating NeuProcessDir."""
    
    # Python environment configuration
    python_packages: List[str] = Field(
        default_factory=list, 
        description="List of Python packages to install"
    )
    base_packages: List[str] = Field(
        default_factory=lambda: [
            "pybids", "nibabel", "numpy", "pandas", "scipy", 
            "matplotlib", "seaborn", "scikit-learn"
        ],
        description="Base Python packages always included"
    )
    
    # Execution configuration
    parallel_execution: bool = Field(default=True, description="Enable parallel execution")
    max_workers: Optional[int] = Field(default=CONFIG.DEFAULT_N_PROCS, description="Maximum number of parallel workers")
    
    # BIDS configuration
    bids_validate: bool = Field(default=False, description="Whether to validate BIDS compliance")
    derivatives_dir: Optional[str] = Field(default=CONFIG.DERIVATIVES_DIR, description="Custom derivatives directory name")
    
    # Container configuration  
    base_container_image: str = Field(
        default=CONFIG.DEFAULT_BASE_IMAGE, 
        description="Base container image"
    )
    container_mounts: List[str] = Field(
        default_factory=list,
        description="Additional container mount points"
    )
    
    @field_validator("python_packages")
    def validate_packages(cls, v, values):
        """Ensure base packages are included."""
        base_packages = values.data.get("base_packages", [])
        all_packages = list(set(base_packages + v))
        return all_packages


class NeuProcessDir(BaseModel):
    """
    A complete directory structure for a NeuProcess with all necessary files.
    """
    
    logic: NeuProcessLogic = Field(..., description="The NeuProcessLogic to wrap")
    config: NeuProcessDirConfig = Field(..., description="Configuration for the directory")
    process_id: Optional[str] = Field(default=None, description="Unique process ID (auto-generated if not provided)")
    output_directory: Optional[Path] = Field(default=None, description="Output directory path")
    
    def model_post_init(self, __context):
        """Initialize the process ID if not provided."""
        if self.process_id is None:
            # Import here to avoid circular imports
            from ....utils.id_generators import generate_id
            self.process_id = generate_id("process_id")
    
    @property
    def process_name(self) -> str:
        """Get the process name from the logic's about.name."""
        return self.logic.about.name
    
    @property
    def author(self) -> str:
        """Get the author from logic's about.author or fallback to 'Unknown'."""
        return self.logic.about.author or "Unknown"
    
    @property
    def description(self) -> str:
        """Get the description from logic's about.description or fallback."""
        return self.logic.about.description or f"Process directory for {self.process_name}"
    
    @property
    def version(self) -> str:
        """Get the version from logic's about.version or fallback."""
        return self.logic.about.version or "1.0.0"
    
    def create_directory(self, output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Create the complete directory structure.
        
        Args:
            output_path: Path where to create the directory. If None, uses PATHS.workdir
            
        Returns:
            Path to the created directory
        """
        if output_path is None:
            output_path = PATHS.workdir
        else:
            output_path = Path(output_path)
        
        # Generate unique process ID if not set, using the constants-based generator
        if self.process_id is None:
            self.process_id = generate_available_process_id(output_path)
        
        # Create main directory using process_id
        main_dir = output_path / self.process_id
        main_dir.mkdir(parents=True, exist_ok=True)
        
        # Store the output directory
        self.output_directory = main_dir
        
        # Create all necessary files
        self._create_main_script(main_dir)
        self._create_requirements_script(main_dir)
        self._create_config_file(main_dir)
        self._create_readme(main_dir)
        self._create_singularity_def(main_dir)
        self._create_execute_script(main_dir)
        
        print(f"✅ NeuProcessDir created at: {main_dir}")
        return main_dir
    
    def _get_template_path(self) -> Path:
        """Get the path to the templates directory using constants."""
        return Path(__file__).parent.parent / "templates"
    
    def _load_template(self, template_name: str) -> str:
        """Load a template file and return its content."""
        template_path = self._get_template_path() / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r') as f:
            return f.read()
    
    def _format_template(self, template_content: str, **kwargs) -> str:
        """Format template content with variables, handling double braces correctly."""
        # Use string.Template for safer substitution that doesn't conflict with f-strings
        import string
        
        # Replace template variables marked with {variable_name}
        # First escape existing double braces to preserve them
        template_content = template_content.replace('{{', '<<<DOUBLE_BRACE_OPEN>>>')
        template_content = template_content.replace('}}', '<<<DOUBLE_BRACE_CLOSE>>>')
        
        # Now do the template substitution
        template_content = template_content.format(**kwargs)
        
        # Restore the double braces
        template_content = template_content.replace('<<<DOUBLE_BRACE_OPEN>>>', '{{')
        template_content = template_content.replace('<<<DOUBLE_BRACE_CLOSE>>>', '}}')
        
        return template_content
    
    def _create_main_script(self, directory: Path) -> None:
        """Create the main.py execution script using template."""
        
        # Generate the function code from NeuProcessLogic
        encoded_result = encode_logic(self.logic)
        if not encoded_result.is_valid:
            raise ValueError(f"Failed to encode logic: {encoded_result.validation_errors}")
        
        # Load template
        template_content = self._load_template(CONFIG.MAIN_SCRIPT_TEMPLATE)
        
        # Prepare template variables
        template_vars = {
            'process_name': self.process_name,
            'pipeline_name': self.process_name,  # alias for backward compatibility
            'author': self.author,
            'description': self.description,
            'version': self.version,
            'process_id': self.process_id,
            'created_timestamp': datetime.now().isoformat(),
            'encoded_function_code': encoded_result.code,
            'function_name': self.logic.about.name
        }
        
        # Format template
        main_script_content = self._format_template(template_content, **template_vars)
        
        # Write script file
        main_script_path = directory / CONFIG.MAIN_SCRIPT_NAME
        with open(main_script_path, 'w') as f:
            f.write(main_script_content)
        
        # Make the script executable
        os.chmod(main_script_path, 0o755)
        print(f"✅ Created {CONFIG.MAIN_SCRIPT_NAME} script")
    
    def _create_requirements_script(self, directory: Path) -> None:
        """Create the install_requirements.sh script using template."""
        
        # Prepare package list
        all_packages = self.config.base_packages + self.config.python_packages
        packages_list = ' '.join(f'"{pkg}"' for pkg in all_packages)
        
        # Load template
        template_content = self._load_template(CONFIG.REQUIREMENTS_TEMPLATE)
        
        # Prepare template variables
        template_vars = {
            'process_name': self.process_name,
            'pipeline_name': self.process_name,  # alias for backward compatibility
            'author': self.author,
            'created_timestamp': datetime.now().isoformat(),
            'python_packages': packages_list
        }
        
        # Format template
        requirements_content = self._format_template(template_content, **template_vars)
        
        # Write script file
        requirements_path = directory / CONFIG.INSTALL_SCRIPT_NAME
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
        
        # Make the script executable
        os.chmod(requirements_path, 0o755)
        print(f"✅ Created {CONFIG.INSTALL_SCRIPT_NAME} script")
    
    def _create_config_file(self, directory: Path) -> None:
        """Create configuration JSON file."""
        
        config_data = {
            "process_info": {
                "process_id": self.process_id,
                "process_name": self.process_name,
                "author": self.author,
                "description": self.description,
                "version": self.version,
                "created": datetime.now().isoformat()
            },
            "processing_logic": {
                "function_name": self.logic.about.name,
                "function_description": self.logic.about.description,
                "language": self.logic.language.value,
                "arguments": [arg.model_dump() for arg in self.logic.arguments]
            },
            "execution_config": {
                "parallel_execution": self.config.parallel_execution,
                "max_workers": self.config.max_workers,
                "bids_validate": self.config.bids_validate,
                "derivatives_dir": self.config.derivatives_dir
            },
            "environment": {
                "base_container_image": self.config.base_container_image,
                "python_packages": self.config.python_packages,
                "base_packages": self.config.base_packages,
                "container_mounts": self.config.container_mounts
            }
        }
        
        config_path = directory / CONFIG.CONFIG_NAME
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ Created {CONFIG.CONFIG_NAME}")
    
    def _create_readme(self, directory: Path) -> None:
        """Create README.md documentation using template."""
        
        # Load template
        template_content = self._load_template(CONFIG.README_TEMPLATE)
        
        # Prepare function arguments documentation
        function_arguments = ""
        for arg in self.logic.arguments:
            function_arguments += f"- **{arg.name}** (`{arg.type}`): {arg.description}"
            if arg.is_optional:
                function_arguments += " *(optional)*"
            function_arguments += "\n"
        
        # Prepare package list
        all_packages = sorted(set(self.config.base_packages + self.config.python_packages))
        python_packages_list = "\n".join(f"- {pkg}" for pkg in all_packages)
        
        # Prepare template variables
        template_vars = {
            'pipeline_name': self.process_name,
            'author': self.author,
            'version': self.version,
            'description': self.description,
            'process_id': self.process_id,
            'created_date': datetime.now().strftime("%Y-%m-%d"),
            'function_name': self.logic.about.name,
            'function_description': self.logic.about.description,
            'function_arguments': function_arguments,
            'base_container_image': self.config.base_container_image,
            'python_packages_list': python_packages_list
        }
        
        # Format template
        readme_content = self._format_template(template_content, **template_vars)
        
        # Write README file
        readme_path = directory / CONFIG.README_NAME
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Created {CONFIG.README_NAME} documentation")
    
    def _create_singularity_def(self, directory: Path) -> None:
        """Create Singularity definition file using template."""
        
        # Load template
        template_content = self._load_template(CONFIG.SINGULARITY_TEMPLATE)
        
        # Prepare template variables
        template_vars = {
            'base_container_image': self.config.base_container_image,
            'author': self.author,
            'version': self.version,
            'description': self.description,
            'pipeline_name': self.process_name,
            'process_id': self.process_id,
            'created_timestamp': datetime.now().isoformat()
        }
        
        # Format template
        def_content = self._format_template(template_content, **template_vars)
        
        # Write definition file using process_id for filename
        def_path = directory / f"{self.process_id}{CONFIG.DEFINITION_EXTENSION}"
        with open(def_path, 'w') as f:
            f.write(def_content)
        
        print(f"✅ Created {self.process_id}{CONFIG.DEFINITION_EXTENSION}")
    
    def _create_execute_script(self, directory: Path) -> None:
        """Create execution script for HPC environments using template."""
        
        # Load template
        template_content = self._load_template(CONFIG.EXECUTE_TEMPLATE)
        
        # Prepare template variables
        template_vars = {
            'pipeline_name': self.process_name,
            'author': self.author,
            'process_id': self.process_id,
            'created_timestamp': datetime.now().isoformat(),
            'default_max_workers': CONFIG.DEFAULT_N_PROCS
        }
        
        # Format template
        execute_content = self._format_template(template_content, **template_vars)
        
        # Write script file
        execute_path = directory / CONFIG.EXECUTE_SCRIPT_NAME
        with open(execute_path, 'w') as f:
            f.write(execute_content)
        
        # Make the script executable
        os.chmod(execute_path, 0o755)
        print(f"✅ Created {CONFIG.EXECUTE_SCRIPT_NAME} script")


def create_neuprocess_directory(
    logic: NeuProcessLogic,
    config: NeuProcessDirConfig,
    output_path: Union[str, Path]
) -> NeuProcessDir:
    """
    Convenience function to create a NeuProcessDir and generate the directory structure.
    
    Args:
        logic: The NeuProcessLogic to wrap
        config: Configuration for the directory
        output_path: Path where to create the directory
        
    Returns:
        NeuProcessDir instance with the created directory
    """
    neuprocess_dir = NeuProcessDir(logic=logic, config=config)
    neuprocess_dir.create_directory(output_path)
    return neuprocess_dir
