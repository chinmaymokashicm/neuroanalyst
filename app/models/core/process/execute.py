"""
Execute Process Image by spawning Docker containers.
"""
from .create import ProcessImageDocker, ProcessImageApptainer
from ....utils.constants import COLLECTION_PROCESS_IMAGES, COLLECTION_PROCESS_EXECS, COLLECTION_SUMMARIES, DEFAULT_CONTAINER_ENVS
from ....utils.db import Connection, find_one_from_db, insert_to_db, check_connection
from ....utils.exceptions import DBRecordMissing
from ....utils.generate import generate_id
from ....utils.dataset import get_sidecar_info_from_dataset
from ....utils.envs import get_neuroanalyst_root_dirs

from typing import Any, Optional
from pathlib import Path, PosixPath
import subprocess, json, logging
from copy import deepcopy

from pydantic import BaseModel, Field
from bids import BIDSLayout

logger = logging.getLogger(__name__)

class ProcessExecConfig(BaseModel):
    output_volumes: dict[str, str] = Field(title="Output Volumes. The volumes to mount to the container.", default={"data_dir": None})
    environment_var_values: dict[str, Any] = Field(title="Environment Variable Values. The values of the environment variables to set in the container.", default={env_name: None for env_name in DEFAULT_CONTAINER_ENVS})

class ProcessExecApptainer(BaseModel):
    id: str = Field(title="ID. The unique identifier of the process execution.", default_factory=lambda: generate_id("PE", 6, "-"))
    process_exec_config: ProcessExecConfig = Field(title="Process Execution Configuration. The configuration for executing the process.")
    process_image: ProcessImageApptainer = Field(title="Process Image. The process image to execute.")
    command: Optional[str] = Field(title="Command. The command to execute the process.", default=None)
    
    def generate_apptainer_run_command(self, additional_volumes: Optional[dict] = None, additional_envs: Optional[dict] = None) -> str:
        if additional_volumes is None:
            additional_volumes = {}
        updated_process_exec_config_output_volumes: dict = {**self.process_exec_config.output_volumes, **additional_volumes}
        
        if additional_envs is None:
            additional_envs = {}
        updated_process_exec_config_env_vars: dict = {**self.process_exec_config.environment_var_values, **additional_envs}
            
        # Load input volumes
        config_container_volumes: dict[str, str] = self.process_image.container_volumes.model_dump()
        config_environment_variables: list[str] = self.process_image.environment_variables
        
        volume_tag_pairs: list[tuple[str, str]] = []
        
        # Check if all container volumes are matched in the output volumes, if not raise an error
        for container_volume_name, container_volume_path in config_container_volumes.items():
            # if container_volume_name not in self.process_exec_config.output_volumes:
            if container_volume_name not in updated_process_exec_config_output_volumes:
                raise ValueError(f"Output volume for {container_volume_name} not specified.")
            # output_volume_path: str = self.process_exec_config.output_volumes[container_volume_name]
            output_volume_path: str = updated_process_exec_config_output_volumes[container_volume_name]
            # Get absolute path for output volume
            output_volume_path: str = str(Path(output_volume_path).resolve())
            if container_volume_name == "output_dir":
                output_volume_path = f"{output_volume_path}/{id}"
            # Add quotes if value contains spaces
            if " " in output_volume_path:
                output_volume_path = "'" + output_volume_path + "'"
            if " " in container_volume_path:
                container_volume_path = "'" + container_volume_path + "'"
            volume_tag_pairs.append((output_volume_path, container_volume_path))
            
        # If any output volume is not matched in the container volumes, raise a warning
        # for container_volume_name in self.process_exec_config.output_volumes:
        for container_volume_name in updated_process_exec_config_output_volumes:
            if container_volume_name not in config_container_volumes:
                logger.warning(f"Output volume for {container_volume_name} not used.")
                
        env_values: dict[str, str] = {}
        
        # Match provided environment variables with the ones in the config
        for env_var_name in config_environment_variables:
            # if env_var_name in self.process_exec_config.environment_var_values:
            if env_var_name in updated_process_exec_config_env_vars:
                # env_values[env_var_name] = self.process_exec_config.environment_var_values[env_var_name]
                env_var_value = updated_process_exec_config_env_vars[env_var_name]
                if not isinstance(env_var_value, dict) and " " in str(env_var_value):
                    env_var_value = "'" + env_var_value + "'"
                env_values[env_var_name] = env_var_value
            else:
                # env_values[env_var_name] = ""
                logger.warning(f"Environment variable {env_var_name} not set.")
                
        # Get environment variables provided in process exec but not defined in process definition
        remaining_envs: list[str] = list(set(updated_process_exec_config_env_vars.keys()) - set(config_environment_variables))
        logger.warning(f"These environment variables were not defined in the process image but are provided while execution- {remaining_envs}")
        for env_name in remaining_envs:
            env_value = updated_process_exec_config_env_vars[env_name]
            if not isinstance(env_value, dict) and " " in str(env_value):
                env_value = "'" + env_value + "'"
            env_values[env_name] = env_value
                
        # Create the Apptainer command using the container name, volume tag pairs, and environment variables
        neuroanalyst_images_dir: str = get_neuroanalyst_root_dirs("images")
        command: str = f"cd {neuroanalyst_images_dir} && apptainer run --contain"
        # command: str = f"cd {neuroanalyst_images_dir} && apptainer instance start"
        for volume_tag_pair in volume_tag_pairs:
            command += f" -B {volume_tag_pair[0]}:{volume_tag_pair[1]}"
        for env_var_name, env_var_value in env_values.items():
            if isinstance(env_var_value, dict):
                env_var_value = json.dumps(env_var_value)
                command += f" --env {env_var_name}='{env_var_value}'"
            else:
                command += f" --env {env_var_name}={env_var_value}"
        command += f" {self.process_image.id}.sif"
        # command += f" {self.process_image.id}.sif {self.id}"
        
        return command
    
    @classmethod
    def from_db(cls, id: str, connection: Optional[Connection] = None):
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[COLLECTION_PROCESS_EXECS]
        
        if collection is None or collection.count_documents({"id": id}) == 0:
            raise DBRecordMissing(f"Process execution with ID {id} does not exist in the database.")
        
        process_exec_dict: dict = find_one_from_db(COLLECTION_PROCESS_EXECS, {"id": id})
        
        return cls(**process_exec_dict)
    
    @classmethod
    def from_user(cls, process_exec_config: ProcessExecConfig, process_image_id: Optional[str] = None, process_image: Optional[ProcessImageApptainer] = None):
        # Load process image configuration from the database
        if process_image_id is not None:
            process_image_config: dict = find_one_from_db(COLLECTION_PROCESS_IMAGES, {"id": process_image_id})
            process_image: ProcessImageApptainer = ProcessImageApptainer(**process_image_config)
        
        if process_image is None:
            raise ValueError("Process image not provided. Either provide a process image ID or a process image object.")
        
        id: str = generate_id(process_image.id, 6, "-")
        
        # command: str = cls.generate_apptainer_run_command(
        #     process_image=process_image,
        #     process_exec_config=process_exec_config,
        #     id=id
        # )
        
        return cls(id=id, process_exec_config=process_exec_config, process_image=process_image)
    
    def to_db(self, connection: Optional[Connection] = None):
        insert_to_db(COLLECTION_PROCESS_EXECS, self.model_dump(mode="json"), connection)
        
    def get_metrics(self, bids_layout: BIDSLayout) -> list[dict]:
        return get_sidecar_info_from_dataset(bids_layout, process_exec_id=self.id)
        
    # def copy_summaries_to_db(self, connection: Optional[Connection] = None):
    #     output_dirpath: PosixPath = Path("outputs") / self.id
    #     if not output_dirpath.exists():
    #         raise DBRecordMissing(f"Output directory {output_dirpath} does not exist.")
    #     summaries: dict[str, dict] = {"process_exec_id": self.id, "process_name": self.process_image.name, "results": {}}
    #     for output_file in output_dirpath.iterdir():
    #         if output_file.is_file() and output_file.suffix == ".json":
    #             with open(output_file, "r") as f:
    #                 feature: dict = json.load(f)
    #             summaries["results"][output_file.stem] = feature
    #     insert_to_db(COLLECTION_SUMMARIES, summaries, connection)
        
    # def stop_container(self):
    #     if self.docker_container_id is None:
    #         raise ValueError("Docker container ID is not set.")
    #     try:
    #         print(f"Stopping Docker container {self.docker_container_id}...")
    #         subprocess.run(f"docker stop {self.docker_container_id}", check=True, shell=True)
    #     except subprocess.CalledProcessError:
    #         raise ValueError(f"An error occurred while stopping the Docker container {self.docker_container_id}.")
        
    def execute(self, save_to_db: bool = True, additional_volumes: Optional[dict] = None, additional_envs: Optional[dict] = []):
        # ! Run this in Celery worker
        
        # Check connection first if save_to_db is set to True
        if save_to_db:
            check_connection()
        
        if self.command is None:
            self.command = self.generate_apptainer_run_command(additional_volumes=additional_volumes, additional_envs=additional_envs)
        # Run the Apptainer command and capture the output
        try:
            logger.info("Spawning Apptainer container...")
            output = subprocess.check_output(self.command, shell=True, universal_newlines=True)
            logger.info(f"Apptainer container spawned with output: \n{output}")
            # Save process execution configuration to the database
            if save_to_db:
                self.to_db()
        except subprocess.CalledProcessError as e:
            raise ValueError(f"An error occurred while spawning the Docker container: {e}")






class ProcessExecDocker(BaseModel):
    """
    Process Execution. This class represents the execution of a Process Image.
    """
    id: str = Field(title="ID. The unique identifier of the process execution.")
    process_exec_config: ProcessExecConfig = Field(title="Process Execution Configuration. The configuration for executing the process.")
    process_image: ProcessImageDocker = Field(title="Process Image. The process image to execute.")
    command: Optional[str] = Field(title="Command. The command to execute the process.", default=None)
    docker_container_id: Optional[str] = Field(title="Docker Container ID. The ID of the Docker container spawned for the process execution.", default=None)
    
    @staticmethod
    def generate_docker_run_command(process_image: ProcessImageDocker, process_exec_config: ProcessExecConfig, id: str) -> str:
        # Load input volumes
        config_container_volumes: dict[str, str] = process_image.container_volumes.model_dump()
        config_environment_variables: list[str] = process_image.environment_variables
        
        volume_tag_pairs: list[tuple[str, str]] = []
        
        # Check if all container volumes are matched in the output volumes, if not raise an error
        for container_volume_name, container_volume_path in config_container_volumes.items():
            if container_volume_name not in process_exec_config.output_volumes:
                raise ValueError(f"Output volume for {container_volume_name} not specified.")
            output_volume_path: str = process_exec_config.output_volumes[container_volume_name]
            # Get absolute path for output volume
            output_volume_path: str = str(Path(output_volume_path).resolve())
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
        # command: str = f"docker run --name {id} -d"
        command: str = f"docker run"
        if process_image.platform is not None:
            command += f" --platform {process_image.platform}"
        command += f" --name {id} -d"
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
    def from_user(cls, process_exec_config: ProcessExecConfig, process_image_id: Optional[str] = None, process_image: Optional[ProcessImageDocker] = None):
        # Load process image configuration from the database
        if process_image_id is not None:
            process_image_config: dict = find_one_from_db(COLLECTION_PROCESS_IMAGES, {"id": process_image_id})
            process_image: ProcessImageDocker = ProcessImageDocker(**process_image_config)
        
        if process_image is None:
            raise ValueError("Process image not provided. Either provide a process image ID or a process image object.")
        
        id: str = generate_id(process_image.id, 6, "-")
        
        command: str = cls.generate_docker_run_command(
            process_image=process_image,
            process_exec_config=process_exec_config,
            id=id
        )
        
        return cls(id=id, process_exec_config=process_exec_config, process_image=process_image, command=command)
    
    def to_db(self, connection: Optional[Connection] = None):
        insert_to_db(COLLECTION_PROCESS_EXECS, self.model_dump(mode="json"), connection)
        
    # def copy_summaries_to_db(self, connection: Optional[Connection] = None):
    #     output_dirpath: PosixPath = Path("outputs") / self.id
    #     if not output_dirpath.exists():
    #         raise DBRecordMissing(f"Output directory {output_dirpath} does not exist.")
    #     summaries: dict[str, dict] = {"process_exec_id": self.id, "process_name": self.process_image.name, "results": {}}
    #     for output_file in output_dirpath.iterdir():
    #         if output_file.is_file() and output_file.suffix == ".json":
    #             with open(output_file, "r") as f:
    #                 feature: dict = json.load(f)
    #             summaries["results"][output_file.stem] = feature
    #     insert_to_db(COLLECTION_SUMMARIES, summaries, connection)
        
    def stop_container(self):
        if self.docker_container_id is None:
            raise ValueError("Docker container ID is not set.")
        try:
            print(f"Stopping Docker container {self.docker_container_id}...")
            subprocess.run(f"docker stop {self.docker_container_id}", check=True, shell=True)
        except subprocess.CalledProcessError:
            raise ValueError(f"An error occurred while stopping the Docker container {self.docker_container_id}.")
        
    def execute(self, save_to_db: bool = True):
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
            print(f"\n\n\n\nDocker container spawned with ID: {self.docker_container_id}\n\n\n\n")
        except subprocess.CalledProcessError as e:
            raise ValueError(f"An error occurred while spawning the Docker container: {e}")

        # Save process execution configuration to the database
        if save_to_db:
            self.to_db()