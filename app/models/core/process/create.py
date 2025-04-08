from ....utils.generate import generate_id
from ....utils.exceptions import DBRecordMissing
from ....utils.db import Connection, insert_to_db, find_one_from_db, check_connection
from ....utils.form import FormField, FormSchema
from ....utils.constants import *
from ....utils.envs import set_neuroanalyst_root_dirs, get_neuroanalyst_root_dirs

from datetime import datetime
from pathlib import Path, PosixPath
from string import Template
import subprocess, json, inspect, os, shutil, logging
from typing import Optional, Any, get_type_hints

from pydantic import BaseModel, DirectoryPath, FilePath, Field, field_validator

logger = logging.getLogger(__name__)

class WorkingDirectory(BaseModel):
    root_dir: DirectoryPath = Field(title="Root Directory. This is the directory where the process will be executed.")
    main_file: FilePath = Field(title="Main File. This is the file that will be executed.")
    requirements_file: FilePath = Field(title="Requirements File. This is the file that contains the dependencies for the process.")
    main_exec_prefix: str = Field(title="Main Execution Prefix. For example, to run a Python script, this would be 'python'.")
    requirements_exec_prefix: str = Field(title="Requirements Execution Prefix. For example, to install a bash script, this would be 'bash'.")
    
    @field_validator("root_dir", mode="after")
    def resolve_path(value: DirectoryPath):
        return value.resolve()
    
    @classmethod
    def from_user(cls, process_workdir_name: str, main_file: str, requirements_file: str, main_exec_prefix: str, requirements_exec_prefix: str) -> "WorkingDirectory":
        """
        Create a WorkingDirectory object from user input.
        Args:
            process_workdir_name (str): The name of the working directory. Should be in $NEUROANALYST_WORKDIR.
            main_file (str): The main file to execute.
            requirements_file (str): The requirements file to execute.
            main_exec_prefix (str): The prefix to execute the main file.
            requirements_exec_prefix (str): The prefix to execute the requirements file.
        Returns:
            WorkingDirectory: The WorkingDirectory object.
        """
        set_neuroanalyst_root_dirs()
        workdir: str = get_neuroanalyst_root_dirs("workdir")
        root_dir: PosixPath = Path(workdir) / process_workdir_name
        # Check if the root directory exists
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
    
    
    # ! OLD - Now using method that only takes name of the working directory and assumes that it is already located in $NEUROANALYST_WORKDIR
    # @classmethod
    # def from_user(cls, root_dir: str, main_file: str, requirements_file: str, main_exec_prefix: str, requirements_exec_prefix: str) -> "WorkingDirectory":
    #     # Check if the root directory exists
    #     root_dir: PosixPath = Path(root_dir)
    #     if not root_dir.exists():
    #         raise ValueError(f"Root directory does not exist: {root_dir}")
    #     # Remove dirpaths from main_file and requirements_file
    #     main_file, requirements_file = Path(main_file).name, Path(requirements_file).name
    #     # Append root_dir to main_file and requirements_file and check if they exist
    #     main_file, requirements_file = root_dir / main_file, root_dir / requirements_file
    #     if not main_file.exists():
    #         raise ValueError(f"Main file does not exist: {main_file}")
    #     if not requirements_file.exists():
    #         raise ValueError(f"Requirements file does not exist: {requirements_file}")
        
    #     # Strip whitespaces from main_exec_prefix and requirements_exec_prefix
    #     main_exec_prefix, requirements_exec_prefix = main_exec_prefix.strip(), requirements_exec_prefix.strip()
        
    #     return cls(
    #         root_dir=root_dir,
    #         main_file=main_file,
    #         requirements_file=requirements_file,
    #         main_exec_prefix=main_exec_prefix,
    #         requirements_exec_prefix=requirements_exec_prefix
        # )

class ContainerVolumes(BaseModel, extra="allow"):
    data_dir: str = Field(title="Data Directory. The directory where the BIDS dataset is stored.", default="/bids_dir/")
    # output_dir: str = Field(title="Output Directory. The directory where the output will be stored.", default="/output_dir/")

class ProcessImageApptainer(BaseModel):
    id: str = Field(title="ID. The unique identifier of the process image.", default_factory=lambda: generate_id("PR", 6, "-"))
    name: str = Field(title="Name. The name of the process.")
    author: str = Field(title="Author. Author of the process.")
    tag: str = Field(title="Tag. The tag of the process.")
    version: str = Field(title="Version. The version of the process.", default="0.1.0")
    description: str = Field(title="Description. A brief description of the process.", default="")
    created_at: datetime = Field(title="Created At. The date and time when the process was created.", default=datetime.now())
    base_docker_image: str = Field(title="Base Docker Image. The base Docker image to use for the process.")
    working_directory: WorkingDirectory = Field(title="Working Directory. Information about the directory where the process will be executed.")
    test_command: Optional[str] = Field(title="Run test command on container build. If None, skips test.", default=None)
    container_volumes: Optional[ContainerVolumes | dict] = Field(title="Container Volumes. The volumes to mount to the container.", default_factory=ContainerVolumes)
    environment_variables: list[str] = Field(title="Environment Variables. The environment variables to set in the container.", default=DEFAULT_CONTAINER_ENVS)
    
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
    def from_db(cls, id: str, connection: Optional[Connection] = None):
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[COLLECTION_PROCESS_IMAGES]
        
        if collection is None or collection.count_documents({"id": id}) == 0:
            raise DBRecordMissing(f"Process image with ID {id} does not exist in the database.")
        
        process_image_config: dict = find_one_from_db(COLLECTION_PROCESS_IMAGES, {"id": id})
        
        return cls(**process_image_config)
    
    @classmethod
    def from_user(cls, name: str, tag: str, author: str, description: str, base_docker_image: str, working_directory: dict, container_volumes: Optional[dict] = None, environment_variables: list[str] = DEFAULT_CONTAINER_ENVS) -> "ProcessImageApptainer":
        try:
            working_directory: WorkingDirectory = WorkingDirectory.from_user(**working_directory)
        except ValueError as e:
            raise ValueError(f"Error while creating working directory: {e}")
        container_volumes: ContainerVolumes = ContainerVolumes(**container_volumes) if container_volumes is not None else ContainerVolumes()
        
        return cls(
            name=name,
            tag=tag,
            author=author,
            description=description,
            base_docker_image=base_docker_image,
            working_directory=working_directory,
            container_volumes=container_volumes,
            environment_variables=environment_variables,
        )
        
    @staticmethod
    def get_ui_form_fields() -> list[dict]:
        return [
            {"name": "name", "description": "Name of the process", "type": "str", "required": True},
            {"name": "tag", "description": "Tag of the process", "type": "str", "required": True},
            {"name": "description", "description": "Description", "type": "str", "required": True},
            {"name": "base_docker_image", "description": "Base Docker image", "type": "str", "required": True},
            {"name": "root_dir", "description": "Working directory", "type": "str", "required": True},
            {"name": "main_file", "description": "Main script to execute to logic", "type": "str", "required": True},
            {"name": "requirements_file", "description": "Dependency installation script", "type": "str", "required": True},
            {"name": "main_exec_prefix", "description": "Prefix to execute the main file", "type": "str", "required": True},
            {"name": "requirements_exec_prefix", "description": "Prefix to install the requirements", "type": "str", "required": True},
            {"name": "container_volumes", "description": "The volumes to mount in the container", "type": "dict", "required": False, "default": {"data_dir": "/bids_dir/"}},
            {"name": "environment_variables", "description": "The environment variables to set in the container", "type": "list", "required": False, "default": ["BIDS_FILTERS"]},
        ]
        
    @staticmethod
    def get_textual_ui_form_fields() -> list[dict]:
        return [
            {"name": "name", "description": "Name of the process", "type": "input", "required": True},
            {"name": "tag", "description": "Tag of the process", "type": "input", "required": True},
            {"name": "description", "description": "Description", "type": "input", "required": True},
            {"name": "base_docker_image", "description": "Base Docker image", "type": "input", "required": True},
            {"name": "root_dir", "description": "Working directory", "type": "select", "required": True},
            {"name": "main_file", "description": "Main script to execute to logic", "type": "select", "required": True},
            {"name": "requirements_file", "description": "Dependency installation script", "type": "select", "required": True},
            {"name": "main_exec_prefix", "description": "Prefix to execute the main file", "type": "select", "required": True},
            {"name": "requirements_exec_prefix", "description": "Prefix to install the requirements", "type": "select", "required": True},
            {"name": "container_volumes", "description": "The volumes to mount in the container", "type": "dict", "required": False, "default": {"data_dir": "/bids_dir/"}},
            {"name": "environment_variables", "description": "The environment variables to set in the container", "type": "list", "required": False, "default": ["BIDS_FILTERS"]},
        ]
    
    @staticmethod
    def get_ui_form_schema():
        """
        Return the form schema for creating a process image from the UI.
        """
        # Load from get_form_fields
        return FormSchema(
            fields=[FormField(**field) for field in ProcessImageDocker.get_ui_form_fields()]
        )
        
    def get_definition(self) -> str:
        with open(Path(TEMPLATES_DIR) / "sif.def", "r") as f:
            template = Template(f.read())
            definition = template.substitute(
                base_image=self.base_docker_image,
                # working_dir=self.working_directory.root_dir,
                requirements_file=self.working_directory.requirements_file.name,
                requirements_exec_prefix=self.working_directory.requirements_exec_prefix,
                main_file=self.working_directory.main_file.name,
                main_exec_prefix=self.working_directory.main_exec_prefix,
                author=self.author,
                version=self.version,
                tag=self.tag
            )
        return definition
    
    def get_documentation(self) -> str:
        with open(Path(TEMPLATES_DIR) / "README.md", "r") as f:
            template = Template(f.read())

        container_volumes_bullets = "\n".join(
            [f"- **{key.replace('_', ' ').title()}**: {value}" for key, value in self.container_volumes.model_dump().items()]
        )

        iter_mount_volume_command = "\\\n  ".join(
            # [f"-v <{host}>:{container}" for host, container in self.container_volumes.model_dump().items()]
            [f"<{host}>:{container}" for host, container in self.container_volumes.model_dump().items()]
        )

        iter_env_command = " \\\n  ".join(
            [f'"{env}=<ENV_VALUE>"' for env in self.environment_variables]
        )
        
        documentation = template.substitute(
            name=self.name,
            description=self.description,
            version=self.version,
            author=self.author,
            created_at=self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            base_docker_image=self.base_docker_image,
            container_volumes_bullets=container_volumes_bullets,
            environment_variables=" ".join(self.environment_variables),
            process_image_id=self.id,
            tag=self.tag,
            iter_mount_volume_command=iter_mount_volume_command,
            iter_env_command=iter_env_command
        )

        return documentation
    
    def get_config(self) -> dict[str, Any]:
        return {
            "container_volumes": self.container_volumes.model_dump(),
            "environment_variables": self.environment_variables
        }
    
    def __copy_work_dir(self, dest_dir: PosixPath | str):
        # Copy the working directory to the destination directory
        dest_dir: PosixPath = Path(dest_dir)
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)
        # subprocess.run(["cp", "-r", self.working_directory.root_dir, dest_dir], check=True)
        src_dir: PosixPath = self.working_directory.root_dir
        for item in src_dir.iterdir():
            s = src_dir / item.name
            d = dest_dir / item.name
            if s.is_dir():
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        
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
            "container_volumes": form_dict["container_volumes"],
            "environment_variables": form_dict["environment_variables"]
        }
    
    def create_image_workdir(self) -> tuple[str, PosixPath]:
        if self.id is None:
            raise ValueError("Process image ID is not set.")
        
        set_neuroanalyst_root_dirs()
        
        docs_dir: str = get_neuroanalyst_root_dirs("docs")
        
        dest_dir: PosixPath = Path(docs_dir) / self.id
        
        # Copy the working directory to the destination directory if it does not exist
        if dest_dir.exists():
            raise ValueError(f"Directory {dest_dir} already exists.")
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        self.__copy_work_dir(dest_dir)
        
        # Create the Apptainer definition
        definition: str = self.get_definition()
        with open(dest_dir / f"{self.id}.def", "w") as f:
            f.write(definition)
            
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
        print(f"README.md created at {dest_dir}/README.md")
            
        print(f"Process image {self.name} [{self.tag}] directory created at {dest_dir}")
        return self.id, dest_dir
    
    def to_db(self, connection: Optional[Connection] = None):
        insert_to_db(COLLECTION_PROCESS_IMAGES, self.model_dump(mode="json"), connection)
    
    def build_image(self, overwrite: bool = True, save_to_db: bool = True) -> None:
        # !Run this in Celery worker
        # Steps-
        # 0. Create work directory
        # 1. Change directory to docs
        # 2. Create .sif image
        # 3. Move to images
        
        # Check connection first if save_to_db is set to True
        if save_to_db:
            check_connection()
        
        self.create_image_workdir()
        
        docs_dir: str = get_neuroanalyst_root_dirs("docs")
        images_dir: str = get_neuroanalyst_root_dirs("images")
        
        if not Path(docs_dir).exists():
            Path(docs_dir).mkdir(parents=True, exist_ok=True)
        if not Path(images_dir).exists():
            Path(images_dir).mkdir(parents=True, exist_ok=True)
        
        command: str = f"cd {docs_dir}/{self.id} && apptainer build "
        if overwrite:
            command += "--force "
        command += f"{self.id}.sif {self.id}.def && mv {self.id}.sif {images_dir}"
        try:
            subprocess.run(command, check=True, shell=True)
            # Save process image configuration to the database
            if save_to_db:
                self.to_db()
        except subprocess.CalledProcessError as e:
            raise ValueError(f"An error occurred while building the Apptainer image: {e}")
        
        # # Push subprocess stdout to logger
        # logger.info(f"Building process image {self.name} [{self.tag}] with command: {command}")
        # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # while True:
        #     output = process.stdout.readline()
        #     if output == b"" and process.poll() is not None:
        #         break
        #     if output:
        #         logger.info(output.strip().decode())
        # rc = process.poll()
        # if rc != 0:
        #     raise ValueError(f"An error occurred while building the Apptainer image: {rc}")
        # # Check if the image was created
        # if not Path(images_dir).exists():
        #     raise ValueError(f"Image {self.id}.sif was not created.")

        # # Save process image configuration to the database
        # if save_to_db:
        #     self.to_db()












class ProcessImageDocker(BaseModel):
    id: str = Field(title="ID. The unique identifier of the process image.", default_factory=lambda: generate_id("PR", 6, "-"))
    name: str = Field(title="Name. The name of the process.")
    tag: str = Field(title="Tag. The tag of the process.")
    version: str = Field(title="Version. The version of the process.", default="0.1.0")
    description: str = Field(title="Description. A brief description of the process.", default="")
    created_at: datetime = Field(title="Created At. The date and time when the process was created.", default=datetime.now())
    base_docker_image: str = Field(title="Base Docker Image. The base Docker image to use for the process.")
    working_directory: WorkingDirectory = Field(title="Working Directory. Information about the directory where the process will be executed.")
    # stages: list[str] = Field(title="Stages. The stages of the process.")
    # expected_outputs: list[str] = Field(title="Expected Outputs. The expected JSON outputs of the process.")
    container_volumes: Optional[ContainerVolumes | dict] = Field(title="Container Volumes. The volumes to mount to the container.", default_factory=ContainerVolumes)
    environment_variables: list[str] = Field(title="Environment Variables. The environment variables to set in the container.", default=["BIDS_FILTERS"])
    platform: Optional[str] = Field(title="Platform. The platform to build the Docker image for.")
    
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
    def from_user(cls, name: str, tag: str, description: str, base_docker_image: str, working_directory: dict, platform: Optional[str],
                #   stages: list[str], 
                #   expected_outputs: list[str], 
                  container_volumes: Optional[dict] = None, environment_variables: list[str] = ["BIDS_FILTERS"]) -> "ProcessImageDocker":
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
            # stages=stages,
            # expected_outputs=expected_outputs,
            container_volumes=container_volumes,
            environment_variables=environment_variables,
            platform=platform
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
            # {"name": "stages", "description": "Stages of the process", "type": "list", "required": True},
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
            fields=[FormField(**field) for field in ProcessImageDocker.get_ui_form_fields()]
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
            # "stages": form_dict["stages"],
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
            else:
                print(f"Docker image {self.base_docker_image} is available locally.")
        except subprocess.CalledProcessError:
            raise ValueError("An error occurred while checking if the Docker image is available locally.")
    
    def get_dockerfile(self) -> str:
        with open(Path(TEMPLATES_DIR) / "Dockerfile", "r") as f:
            template = Template(f.read())
            dockerfile = template.substitute(
                base_image=self.base_docker_image,
                requirements_file=self.working_directory.requirements_file.name,
                requirements_exec_prefix=self.working_directory.requirements_exec_prefix,
                main_file=self.working_directory.main_file.name,
                main_exec_prefix=self.working_directory.main_exec_prefix,
                # stages=",".join(self.stages)
            )
        return dockerfile
    
    def __copy_work_dir(self, dest_dir: PosixPath | str):
        # Copy the working directory to the destination directory
        subprocess.run(["cp", "-r", self.working_directory.root_dir, dest_dir], check=True)
        
    def get_documentation(self) -> str:
        with open(Path(TEMPLATES_DIR) / "README.md", "r") as f:
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
            # stages=", ".join(self.stages),
            container_volumes_bullets=container_volumes_bullets,
            environment_variables=" ".join(self.environment_variables),
            process_image_id=self.id,
            tag=self.tag,
            iter_mount_volume_command=iter_mount_volume_command,
            iter_env_command=iter_env_command
        )

        return documentation
    
    def create_image_workdir(self, dest_root_dir: PosixPath | str) -> tuple[str, PosixPath]:
        if self.id is None:
            raise ValueError("Process image ID is not set.")
        dest_dir: PosixPath = Path(dest_root_dir) / self.id
        
        # Copy the working directory to the destination directory if it does not exist
        if dest_dir.exists():
            raise ValueError(f"Directory {dest_dir} already exists.")
        dest_root_dir.mkdir(parents=True, exist_ok=True)
        self.__copy_work_dir(dest_dir)
        
        # Create the Dockerfile
        dockerfile: str = self.get_dockerfile()
        with open(dest_dir / "Dockerfile", "w") as f:
            f.write(dockerfile)
        
        # Copy other necessary files
        subprocess.run(["cp", str(Path(TEMPLATES_DIR) / "execute.sh"), dest_dir], check=True)
        subprocess.run(["cp", str(Path(TEMPLATES_DIR) / "update_progress.sh"), dest_dir], check=True)
            
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
            
        print(f"Process image {self.name} [{self.tag}] directory created at {dest_dir}")
        return self.id, dest_dir
        
    def to_db(self, connection: Optional[Connection] = None):
        insert_to_db(COLLECTION_PROCESS_IMAGES, self.model_dump(mode="json"), connection)
    
    def build_image(self, dest_dir: PosixPath | str, platform: Optional[str] = None, save_to_db: bool = True) -> None:
        # !Run this in Celery worker
        if platform is None:
            platform = self.platform
        
        # Verify the base Docker image
        self.verify_base_docker_image()
        
        # Build the Docker image - compatible with all platforms
        print("Building Docker image...")
        command: str = f"cd {dest_dir}; docker build"
        if platform is not None:
            command += f' --platform "{platform}"'
        command += f" -t '{self.tag}' --label project=neuroanalyst --label process_id={dest_dir.name} ."
        print(f"Command: {command}")
        try:
            subprocess.run(command, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            raise ValueError(f"An error occurred while building the Docker image: {e}")

        # Save process image configuration to the database
        if save_to_db:
            self.to_db()