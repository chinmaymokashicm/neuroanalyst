from ..utils.generate import generate_id
from ..utils.exceptions import DBRecordMissing
from ..utils.db import Connection, insert_to_db, find_one_from_db
from ..utils.constants import COLLECTION_PROCESS_IMAGES, COLLECTION_PROCESS_EXECS, COLLECTION_SUMMARIES

from datetime import datetime
from pathlib import Path, PosixPath
from string import Template
import subprocess, json
from typing import Optional, Any

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
    container_volumes: Optional[ContainerVolumes | dict] = Field(title="Container Volumes. The volumes to mount in the container.", default_factory=ContainerVolumes)
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
        return id, dest_dir
        
    def to_db(self, connection: Optional[Connection] = None):
        insert_to_db(COLLECTION_PROCESS_IMAGES, self.model_dump(mode="json"), connection)
    
    def build_image(self, dest_dir: str):
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

class ProcessExecConfig(BaseModel):
    output_volumes: dict[str, str] = Field(title="Output Volumes. The volumes to mount in the container.")
    environment_var_values: dict[str, Any] = Field(title="Environment Variable Values. The values of the environment variables to set in the container.", default_factory=dict)
    
class ProcessExec(BaseModel):
    id: str = Field(title="ID. The unique identifier of the process execution.")
    process_exec_config: ProcessExecConfig = Field(title="Process Execution Configuration. The configuration for executing the process.")
    process_image: ProcessImage = Field(title="Process Image. The process image to execute.")
    command: Optional[str] = Field(title="Command. The command to execute the process.", default=None)
    docker_container_id: Optional[str] = Field(title="Docker Container ID. The ID of the Docker container spawned for the process execution.", default=None)
    
    @staticmethod
    def generate_docker_run_command(process_image: ProcessImage, process_exec_config: ProcessExecConfig, id: str) -> str:
        # Load input volumes
        config_container_volumes: dict[str, str] = process_image.container_volumes.model_dump()
        config_environment_variables: list[str] = process_image.environment_variables
        
        volume_tag_pairs: list[tuple[str, str]] = []
        
        # Check if all container volumes are matched in the output volumes, if not raise an error
        for container_volume_name, container_volume_path in config_container_volumes.items():
            if container_volume_name not in process_exec_config.output_volumes:
                raise ValueError(f"Output volume for {container_volume_name} not specified.")
            output_volume_path: str = process_exec_config.output_volumes[container_volume_name]
            if container_volume_name == "output_dir":
                output_volume_path = f"{output_volume_path}/{id}"
            volume_tag_pairs.append((output_volume_path, container_volume_path))
            
        # If any output volume is not matched in the container volumes, raise a warning
        for container_volume_name in process_exec_config.output_volumes:
            if container_volume_name not in config_container_volumes:
                print(f"Warning: Output volume for {container_volume_name} not used.")
                
        env_values: dict[str, str] = {}
        
        # Match provided environment variables with the ones in the config
        for env_var_name in config_environment_variables:
            if env_var_name in process_exec_config.environment_var_values:
                env_values[env_var_name] = process_exec_config.environment_var_values[env_var_name]
            else:
                env_values[env_var_name] = ""
                print(f"Warning: Environment variable {env_var_name} not set.")
                
        # Create the Docker command using the container name, volume tag pairs, and environment variables
        command: str = f"docker run --name {id} -d"
        for volume_tag_pair in volume_tag_pairs:
            command += f" -v {volume_tag_pair[0]}:{volume_tag_pair[1]}"
        for env_var_name, env_var_value in env_values.items():
            if isinstance(env_var_value, dict):
                env_var_value = json.dumps(env_var_value)
                command += f" -e {env_var_name}='{env_var_value}'"
            else:
                command += f" -e {env_var_name}={env_var_value}"
        command += f" {process_image.tag}"
        
        return command
    
    @classmethod
    def from_db(cls, id: str, connection: Optional[Connection] = None):
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[COLLECTION_PROCESS_EXECS]
        
        if collection is None or collection.count_documents({"id": id}) == 0:
            raise DBRecordMissing(f"Process execution with ID {id} does not exist in the database.")
        
        process_exec_config: dict = find_one_from_db(COLLECTION_PROCESS_EXECS, {"id": id})
        
        return cls(**process_exec_config)
    
    @classmethod
    def from_user(cls, process_exec_config: ProcessExecConfig, process_image_id: str):
        # Load process image configuration from the database
        process_image_config: dict = find_one_from_db(COLLECTION_PROCESS_IMAGES, {"id": process_image_id})
        process_image: ProcessImage = ProcessImage(**process_image_config)
        
        id: str = generate_id(process_image.id, 6, "-")
        
        command: str = cls.generate_docker_run_command(
            process_image=process_image,
            process_exec_config=process_exec_config,
            id=id
        )
        
        return cls(id=id, process_exec_config=process_exec_config, process_image=process_image, command=command)
    
    def to_db(self, connection: Optional[Connection] = None):
        insert_to_db(COLLECTION_PROCESS_EXECS, self.model_dump(mode="json"), connection)
        
    def copy_summaries_to_db(self, connection: Optional[Connection] = None):
        output_dirpath: PosixPath = Path("outputs") / self.id
        if not output_dirpath.exists():
            raise DBRecordMissing(f"Output directory {output_dirpath} does not exist.")
        summaries: dict[str, dict] = {"process_exec_id": self.id, "process_name": self.process_image.name, "results": {}}
        for output_file in output_dirpath.iterdir():
            if output_file.is_file() and output_file.suffix == ".json":
                with open(output_file, "r") as f:
                    feature: dict = json.load(f)
                summaries["results"][output_file.stem] = feature
        insert_to_db(COLLECTION_SUMMARIES, summaries, connection)
        
    def execute(self):
        if self.command is None:
            self.command = self.generate_docker_run_command(
                process_image=self.process_image,
                process_exec_config=self.process_exec_config,
                id=self.id
            )
        # Run the Docker command and capture the output
        try:
            print("Spawning Docker container...")
            output = subprocess.check_output(self.command, shell=True, universal_newlines=True)
            self.docker_container_id = output.strip()  # Extract the container ID from the output
            print(f"Docker container spawned with ID: {self.docker_container_id}")
        except subprocess.CalledProcessError as e:
            raise ValueError(f"An error occurred while spawning the Docker container: {e}")

        # Save process execution configuration to the database
        self.to_db()