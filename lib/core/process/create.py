from ...utils.generate import generate_id
from ...utils.exceptions import DBRecordMissing
from ...utils.db import Connection, insert_to_db, find_one_from_db
from ...utils.form import FormField, FormSchema
from ...utils.constants import COLLECTION_PROCESS_IMAGES, COLLECTION_PROCESS_EXECS, COLLECTION_SUMMARIES

from datetime import datetime
from pathlib import Path, PosixPath
from string import Template
import subprocess, json, inspect
from typing import Optional, Any, get_type_hints

from pydantic import BaseModel, DirectoryPath, FilePath, Field, field_validator

class WorkingDirectory(BaseModel):
    root_dir: DirectoryPath = Field(title="Root Directory. This is the directory where the process will be executed.")
    main_file: FilePath = Field(title="Main File. This is the file that will be executed.")
    requirements_file: FilePath = Field(title="Requirements File. This is the file that contains the dependencies for the process.")
    main_exec_prefix: str = Field(title="Main Execution Prefix. For example, to run a Python script, this would be 'python'.")
    requirements_exec_prefix: str = Field(title="Requirements Execution Prefix. For example, to install a bash script, this would be 'bash'.")
    
    @classmethod
    def from_user(cls, root_dir: str, main_file: str, requirements_file: str, main_exec_prefix: str, requirements_exec_prefix: str) -> "WorkingDirectory":
        # Check if the root directory exists
        root_dir: PosixPath = Path(root_dir)
        if not root_dir.exists():
            raise ValueError(f"Root directory does not exist: {root_dir}")
        # Remove dirpaths from main_file and requirements_file
        main_file, requirements_file = Path(main_file).name, Path(requirements_file).name
        # Append root_dir to main_file and requirements_file and check if they exist
        main_file, requirements_file = root_dir / main_file, root_dir / requirements_file
        if not main_file.exists():
            raise ValueError(f"Main file does not exist: {main_file}")
        if not requirements_file.exists():
            raise ValueError(f"Requirements file does not exist: {requirements_file}")
        
        # Strip whitespaces from main_exec_prefix and requirements_exec_prefix
        main_exec_prefix, requirements_exec_prefix = main_exec_prefix.strip(), requirements_exec_prefix.strip()
        
        return cls(
            root_dir=root_dir,
            main_file=main_file,
            requirements_file=requirements_file,
            main_exec_prefix=main_exec_prefix,
            requirements_exec_prefix=requirements_exec_prefix
        )

class ContainerVolumes(BaseModel, extra="allow"):
    data_dir: str = Field(title="Data Directory. The directory where the BIDS dataset is stored.", default="/bids_dir/")
    output_dir: str = Field(title="Output Directory. The directory where the output will be stored.", default="/output_dir/")

class ProcessImage(BaseModel):
    id: str = Field(title="ID. The unique identifier of the process image.", default_factory=lambda: generate_id("PR", 6, "-"))
    name: str = Field(title="Name. The name of the process.")
    tag: str = Field(title="Tag. The tag of the process.")
    version: str = Field(title="Version. The version of the process.", default="0.1.0")
    description: str = Field(title="Description. A brief description of the process.", default="")
    created_at: datetime = Field(title="Created At. The date and time when the process was created.", default=datetime.now())
    base_docker_image: str = Field(title="Base Docker Image. The base Docker image to use for the process.")
    working_directory: WorkingDirectory = Field(title="Working Directory. Information about the directory where the process will be executed.")
    stages: list[str] = Field(title="Stages. The stages of the process.")
    expected_outputs: list[str] = Field(title="Expected Outputs. The expected JSON outputs of the process.")
    container_volumes: Optional[ContainerVolumes | dict] = Field(title="Container Volumes. The volumes to mount to the container.", default_factory=ContainerVolumes)
    environment_variables: list[str] = Field(title="Environment Variables. The environment variables to set in the container.", default=["BIDS_FILTERS"])
    
    @field_validator("tag")
    def check_tag(cls, value):
        if len(value) == 0:
            raise ValueError("Tag must be non-empty.")
        # Check if first character is a lowercase letter
        if not value[0].islower():
            raise ValueError("Tag must start with a lowercase letter.")
        # Check if all characters are alphanumeric or hyphens
        if not all(c.isalnum() or c == "-" for c in value):
            raise ValueError("Tag must contain only alphanumeric characters and hyphens.")
        return value
    
    @field_validator("container_volumes")
    def check_container_volumes(cls, value):
        if value is None or value == {}:
            return ContainerVolumes()
        if isinstance(value, dict):
            return ContainerVolumes(**value)
        return value
    
    @classmethod
    def from_user(cls, name: str, tag: str, description: str, base_docker_image: str, working_directory: dict, stages: list[str], expected_outputs: list[str], container_volumes: Optional[dict] = None, environment_variables: list[str] = ["BIDS_FILTERS"]) -> "ProcessImage":
        try:
            working_directory: WorkingDirectory = WorkingDirectory.from_user(**working_directory)
        except ValueError as e:
            raise ValueError(f"Error while creating working directory: {e}")
        container_volumes: ContainerVolumes = ContainerVolumes(**container_volumes) if container_volumes is not None else ContainerVolumes()
        
        return cls(
            name=name,
            tag=tag,
            description=description,
            base_docker_image=base_docker_image,
            working_directory=working_directory,
            stages=stages,
            expected_outputs=expected_outputs,
            container_volumes=container_volumes,
            environment_variables=environment_variables
        )
        
    @staticmethod
    def get_ui_form_fields() -> list[dict]:
        return [
            {"name": "name", "description": "Name of the process", "type": "str", "required": True},
            {"name": "tag", "description": "Tag of the process", "type": "str", "required": True},
            {"name": "description", "description": "Description", "type": "str", "required": True},
            {"name": "base_docker_image", "description": "Base Docker image", "type": "str", "required": True},
            # {"name": "root_dir", "description": "Working directory", "type": "directory", "required": True},
            {"name": "root_dir", "description": "Working directory", "type": "str", "required": True},
            {"name": "main_file", "description": "Main script to execute to logic", "type": "str", "required": True},
            {"name": "requirements_file", "description": "Dependency installation script", "type": "str", "required": True},
            {"name": "main_exec_prefix", "description": "Prefix to execute the main file", "type": "str", "required": True},
            {"name": "requirements_exec_prefix", "description": "Prefix to install the requirements", "type": "str", "required": True},
            {"name": "stages", "description": "Stages of the process", "type": "list", "required": True},
            {"name": "expected_outputs", "description": "The expected JSON outputs of the process", "type": "list", "required": True},
            {"name": "container_volumes", "description": "The volumes to mount in the container", "type": "dict", "required": False, "default": {"data_dir": "/bids_dir/", "output_dir": "/output_dir/"}},
            {"name": "environment_variables", "description": "The environment variables to set in the container", "type": "list", "required": False, "default": ["BIDS_FILTERS"]},
        ]
    
    @staticmethod
    def get_ui_form_schema():
        """
        Return the form schema for creating a process image from the UI.
        """
        # Load from get_form_fields
        return FormSchema(
            fields=[FormField(**field) for field in ProcessImage.get_ui_form_fields()]
        )
        
    @staticmethod
    def get_ui_submission_preview(form_dict: dict) -> dict:
        working_directory: dict = {
            "root_dir": form_dict["root_dir"],
            "main_file": form_dict["main_file"],
            "requirements_file": form_dict["requirements_file"],
            "main_exec_prefix": form_dict["main_exec_prefix"],
            "requirements_exec_prefix": form_dict["requirements_exec_prefix"]
        }
        # stages: list[str] = [item.strip() for item in form_dict["stages"].split(",")]
        # expected_outputs: list[str] = [item.strip() for item in form_dict["expected_outputs"].split(",")]
        return {
            "name": form_dict["name"],
            "tag": form_dict["tag"],
            "description": form_dict["description"],
            "base_docker_image": form_dict["base_docker_image"],
            "working_directory": working_directory,
            "stages": form_dict["stages"],
            "expected_outputs": form_dict["expected_outputs"],
            "container_volumes": form_dict["container_volumes"],
            "environment_variables": form_dict["environment_variables"]
        }
        
    
    @classmethod
    def from_db(cls, id: str, connection: Optional[Connection] = None):
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[COLLECTION_PROCESS_IMAGES]
        
        if collection is None or collection.count_documents({"id": id}) == 0:
            raise DBRecordMissing(f"Process image with ID {id} does not exist in the database.")
        
        process_image_config: dict = find_one_from_db(COLLECTION_PROCESS_IMAGES, {"id": id})
        
        return cls(**process_image_config)
    
    def verify_base_docker_image(self):
        # Check if Docker is installed
        try:
            print("Checking if Docker is installed...")
            subprocess.run(["docker", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            raise EnvironmentError("Docker is not installed or not properly set up.")

        # Check if the Docker image is available locally
        try:
            print(f"Checking if Docker image {self.base_docker_image} is available locally...")
            result = subprocess.run(["docker", "images", "-q", self.base_docker_image], check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if not result.stdout:
                # If the image is not available locally, try to pull it
                try:
                    subprocess.run(["docker", "pull", self.base_docker_image], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    raise ValueError(f"Docker image {self.base_docker_image} is not available.")
        except subprocess.CalledProcessError:
            raise ValueError("An error occurred while checking if the Docker image is available locally.")
    
    def get_dockerfile(self) -> str:
        with open("lib/process/templates/Dockerfile", "r") as f:
            template = Template(f.read())
            dockerfile = template.substitute(
                base_image=self.base_docker_image,
                requirements_file=self.working_directory.requirements_file.name,
                requirements_exec_prefix=self.working_directory.requirements_exec_prefix,
                main_file=self.working_directory.main_file.name,
                main_exec_prefix=self.working_directory.main_exec_prefix,
                stages=",".join(self.stages)
            )
        return dockerfile
    
    def copy_work_dir(self, dest_dir: PosixPath):
        # Copy the working directory to the destination directory
        subprocess.run(["cp", "-r", self.working_directory.root_dir, dest_dir], check=True)
        
    def get_documentation(self) -> str:
        with open("lib/process/templates/README.md", "r") as f:
            template = Template(f.read())

        container_volumes_bullets = "\n".join(
            [f"- **{key.replace('_', ' ').title()}**: {value}" for key, value in self.container_volumes.model_dump().items()]
        )

        iter_mount_volume_command = " \\\n  ".join(
            [f"-v <{host}>:{container}" for host, container in self.container_volumes.model_dump().items()]
        )

        iter_env_command = " \\\n  ".join(
            [f"-e {env}=<ENV_VALUE>" for env in self.environment_variables]
        )

        documentation = template.substitute(
            name=self.name,
            description=self.description,
            version=self.version,
            created_at=self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            base_docker_image=self.base_docker_image,
            stages=", ".join(self.stages),
            container_volumes_bullets=container_volumes_bullets,
            environment_variables=" ".join(self.environment_variables),
            process_image_id=self.id,
            tag=self.tag,
            iter_mount_volume_command=iter_mount_volume_command,
            iter_env_command=iter_env_command
        )

        return documentation
    
    def create_image_workdir(self) -> tuple[str, PosixPath]:
        if self.id is None:
            raise ValueError("Process image ID is not set.")
        dest_dir: PosixPath = Path(f"{self.id}/")
        
        # Copy the working directory to the destination directory
        self.copy_work_dir(dest_dir)
        
        # Create the Dockerfile
        dockerfile: str = self.get_dockerfile()
        with open(dest_dir / "Dockerfile", "w") as f:
            f.write(dockerfile)
        
        # Copy other necessary files
        subprocess.run(["cp", "lib/process/templates/execute.sh", dest_dir], check=True)
        subprocess.run(["cp", "lib/process/templates/update_progress.sh", dest_dir], check=True)
            
        config: dict = {
            "container_volumes": self.container_volumes.model_dump(),
            "environment_variables": self.environment_variables
        }
    
        # Set config to config.json
        with open(dest_dir / "config.json", "w") as f:
            json.dump(config, f, indent=4)
        
        readme: str = self.get_documentation()
        with open(dest_dir / "README.md", "w") as f:
            f.write(readme)
        print(f"README.md created at {dest_dir}")
            
        print(f"Process image {self.name} / {self.tag} directory created at {dest_dir}")
        return self.id, dest_dir
        
    def to_db(self, connection: Optional[Connection] = None):
        insert_to_db(COLLECTION_PROCESS_IMAGES, self.model_dump(mode="json"), connection)
    
    def build_image(self, dest_dir: PosixPath):
        # Verify the base Docker image
        self.verify_base_docker_image()
        
        # Build the Docker image
        try:
            print("Building Docker image...")
            command: str = f"cd {dest_dir}; docker build -t '{self.tag}' --label project=neuroanalyst --label process_id={dest_dir.name} ."
            subprocess.run(command, check=True, shell=True)
        except subprocess.CalledProcessError:
            raise ValueError("An error occurred while building the Docker image.")

        # Save process image configuration to the database
        self.to_db()