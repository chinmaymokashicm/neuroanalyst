from ..utils.generate import generate_id

from datetime import datetime
from pathlib import Path, PosixPath
from string import Template
import subprocess, json
from typing import Optional

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
    name: str = Field(title="Name. The name of the process.")
    tag: str = Field(title="Tag. The tag of the process.")
    description: str = Field(title="Description. A brief description of the process.", default="")
    created_at: datetime = Field(title="Created At. The date and time when the process was created.", default=datetime.now())
    version: str = Field(title="Version. The version of the process.", default="0.0.1")
    base_docker_image: str = Field(title="Base Docker Image. The base Docker image to use for the process.")
    working_directory: WorkingDirectory = Field(title="Working Directory. Information about the directory where the process will be executed.")
    stages: list[str] = Field(title="Stages. The stages of the process.")
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
    
    @field_validator("base_docker_image")
    def check_base_docker_image(cls, value):
        if value == "":
            raise ValueError("Base image must be non-empty.")
    
        # Check if Docker is installed
        try:
            print("Checking if Docker is installed...")
            subprocess.run(["docker", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            raise EnvironmentError("Docker is not installed or not properly set up.")

        # Check if the Docker image is available locally
        try:
            print(f"Checking if Docker image {value} is available locally...")
            result = subprocess.run(["docker", "images", "-q", value], check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if not result.stdout:
                # If the image is not available locally, try to pull it
                try:
                    subprocess.run(["docker", "pull", value], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    raise ValueError(f"Docker image {value} is not available.")
        except subprocess.CalledProcessError:
            raise ValueError("An error occurred while checking if the Docker image is available locally.")

        return value
    
    @field_validator("container_volumes")
    def check_container_volumes(cls, value):
        if value is None or value == {}:
            return ContainerVolumes()
        if isinstance(value, dict):
            return ContainerVolumes(**value)
        return value
    
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
            process_image_id=generate_id("PI", 6, "-"),
            tag=self.tag,
            iter_mount_volume_command=iter_mount_volume_command,
            iter_env_command=iter_env_command
        )

        return documentation
    
    def create_image_workdir(self):
        process_image_id: str = generate_id("PI", 6, "-")
        dest_dir: PosixPath = Path(f"{process_image_id}/")
        
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
            json.dump(config, f)
        
        readme: str = self.get_documentation()
        with open(dest_dir / "README.md", "w") as f:
            f.write(readme)
        print(f"README.md created at {dest_dir}")
            
        print(f"Process image {self.name} / {self.tag} directory created at {dest_dir}")
        return process_image_id, dest_dir
        
    def build_image(self, dest_dir: str):
        # Build the Docker image
        try:
            print("Building Docker image...")
            command: str = f"cd {dest_dir}; docker build -t '{self.tag}' ."
            subprocess.run(command, check=True, shell=True)
        except subprocess.CalledProcessError:
            raise ValueError("An error occurred while building the Docker image.")

def spawn_container(
    process_image_id: str, 
    process_image_name: str, 
    output_volumes: dict[str, str],
    environment_var_values: dict[str, str] = {}
    ) -> tuple[str, str]:
    
    process_image_dirpath: PosixPath = Path(process_image_id)
    if not process_image_dirpath.exists():
        raise ValueError(f"Process image directory does not exist: {process_image_dirpath}")
    # Generate random container name
    container_name: str = generate_id("PC", 6, "-")
    
    # Load input volumes
    with open(process_image_dirpath / "config.json", "r") as f:
        config: dict = json.load(f)
        config_container_volumes: dict[str, str] = config["container_volumes"]
        config_environment_variables: list[str] = config["environment_variables"]
    
    volume_tag_pairs: list[tuple[str, str]] = []
    
    # Check if all container volumes are matched in the output volumes, if not raise an error
    for container_volume_name, container_volume_path in config_container_volumes.items():
        if container_volume_name not in output_volumes:
            raise ValueError(f"Output volume for {container_volume_name} not specified.")
        output_volume_path: str = output_volumes[container_volume_name]
        if container_volume_name == "output_dir":
            output_volume_path = f"{output_volume_path}/{container_name}"
        volume_tag_pairs.append((output_volume_path, container_volume_path))
    
    # If any output volume is not matched in the container volumes, raise a warning
    for container_volume_name in output_volumes:
        if container_volume_name not in config_container_volumes:
            print(f"Warning: Output volume for {container_volume_name} not used.")    
    
    env_values: dict[str, str] = {}
        
    # Match provided environment variables with the ones in the config
    for env_var_name in config_environment_variables:
        if env_var_name in environment_var_values:
            env_values[env_var_name] = environment_var_values[env_var_name]
        else:
            env_values[env_var_name] = ""
            print(f"Warning: Environment variable {env_var_name} not set.")
    
    # Create the Docker command and use the volumes
    command: str = f"docker run --name {container_name} -d"
    for volume_tag_pair in volume_tag_pairs:
        command += f" -v {volume_tag_pair[0]}:{volume_tag_pair[1]}"
    for env_var_name, env_var_value in env_values.items():
        if isinstance(env_var_value, dict):
            env_var_value = json.dumps(env_var_value)
            command += f" -e {env_var_name}='{env_var_value}'"
        else:
            command += f" -e {env_var_name}={env_var_value}"
    command += f" {process_image_name}"
    
    # Run the Docker command
    try:
        print("Spawning Docker container...")
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        raise ValueError(f"An error occurred while spawning the Docker container: {e}")
    
    return container_name, command