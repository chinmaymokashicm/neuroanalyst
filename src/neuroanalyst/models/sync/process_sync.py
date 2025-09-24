"""
NeuProcess Sync Module

This module provides synchronization functionality for NeuProcess instances between HPC and DB.
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple

from pydantic import Field

from ...utils.constants import PATHS
from ..database import MongoDBClient, CollectionNames
from ..process.process.core import NeuProcess
from .core import SyncBase, SyncDirection, SyncStrategy, SyncConfig


class NeuProcessSync(SyncBase):
    """
    Class for synchronizing NeuProcess data between HPC and DB.
    
    This class provides methods to:
    1. Load NeuProcess data from HPC
    2. Load NeuProcess data from DB
    3. Compare differences between HPC and DB data
    4. Sync data from HPC to DB
    5. Sync data from DB to HPC
    """
    
    def __init__(self, **data):
        """Initialize the NeuProcessSync instance."""
        super().__init__(**data)
        self.mongo_client = MongoDBClient()
        self.mongo_client.connect()
    
    def load_from_hpc(self, process_id: str) -> Optional[NeuProcess]:
        """
        Load NeuProcess data from HPC storage.
        
        Args:
            process_id: ID of the process to load
            
        Returns:
            NeuProcess instance if found, None otherwise
        """
        self.logger.info(f"Loading NeuProcess {process_id} from HPC storage")
        
        # Check if process directory exists
        process_dir_path = PATHS.workdir / process_id
        if not process_dir_path.exists():
            self.logger.warning(f"Process directory {process_dir_path} does not exist")
            return None
        
        # Load model.json from the process directory
        model_path = process_dir_path / "model.json"
        if not model_path.exists():
            self.logger.warning(f"Model file {model_path} does not exist")
            return None
        
        try:
            # Load NeuProcessDir from model.json
            from ..process.dir.core import NeuProcessDir
            with open(model_path, "r") as f:
                model_data = json.load(f)
            
            process_dir = NeuProcessDir.model_validate(model_data)
            
            # Create NeuProcess instance
            process = NeuProcess(
                process_id=process_id,
                process_dir=process_dir
            )
            
            return process
        
        except Exception as e:
            self.logger.error(f"Error loading process from HPC storage: {e}")
            return None
    
    def load_from_db(self, process_id: str) -> Optional[NeuProcess]:
        """
        Load NeuProcess data from DB.
        
        Args:
            process_id: ID of the process to load
            
        Returns:
            NeuProcess instance if found, None otherwise
        """
        self.logger.info(f"Loading NeuProcess {process_id} from DB")
        
        # Find document in MongoDB
        process_doc = self.mongo_client.find_one(
            CollectionNames.PROCESSES, 
            {"process_id": process_id}
        )
        
        if not process_doc:
            self.logger.warning(f"Process {process_id} not found in DB")
            return None
        
        try:
            # Reconstruct NeuProcessDir from metadata
            from ..process.dir.core import NeuProcessDir
            
            if "process_dir_metadata" in process_doc:
                process_dir = NeuProcessDir.model_validate(process_doc["process_dir_metadata"])
            else:
                self.logger.warning(f"Process {process_id} has no process_dir_metadata in DB")
                return None
            
            # Create NeuProcess instance
            process = NeuProcess(
                process_id=process_id,
                process_dir=process_dir
            )
            
            # Set additional fields from DB if available
            if "bind_paths" in process_doc:
                process.bind_paths = process_doc["bind_paths"]
            
            if "env_vars" in process_doc:
                process.env_vars = process_doc["env_vars"]
            
            return process
            
        except Exception as e:
            self.logger.error(f"Error loading process from DB: {e}")
            return None
    
    def compare_diff(self, process_id: str) -> Dict[str, Any]:
        """
        Compare differences between HPC and DB data for a process.
        
        Args:
            process_id: ID of the process to compare
            
        Returns:
            Dictionary with differences
        """
        self.logger.info(f"Comparing differences for process {process_id}")
        
        # Load data from both sources
        hpc_process = self.load_from_hpc(process_id)
        db_process = self.load_from_db(process_id)
        
        if not hpc_process and not db_process:
            self.logger.warning(f"Process {process_id} not found in HPC or DB")
            return {"error": "Process not found in HPC or DB"}
        
        if not hpc_process:
            self.logger.warning(f"Process {process_id} not found in HPC")
            return {"error": "Process not found in HPC", "exists_in": "db"}
        
        if not db_process:
            self.logger.warning(f"Process {process_id} not found in DB")
            return {"error": "Process not found in DB", "exists_in": "hpc"}
        
        # Convert both to dictionaries for comparison
        hpc_data = hpc_process.model_dump()
        db_data = db_process.model_dump()
        
        # Compare dictionaries
        return self.compare_dicts(hpc_data, db_data)
    
    def sync_to_db(self, process: Union[NeuProcess, str]) -> str:
        """
        Sync NeuProcess data from HPC to DB.
        
        Args:
            process: NeuProcess instance or process ID
            
        Returns:
            MongoDB document ID or error message
        """
        self.logger.info(f"Syncing process to DB")
        
        # If process_id is provided, load from HPC first
        if isinstance(process, str):
            process_instance = self.load_from_hpc(process)
            if not process_instance:
                error_msg = f"Process {process} not found in HPC"
                self.logger.error(error_msg)
                return error_msg
            process = process_instance
        
        # Create MongoDB document
        process_doc = {
            "process_id": process.process_id,
            "name": process.process_dir.name,
            "description": process.process_dir.description,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "bind_paths": process.bind_paths,
            "env_vars": process.env_vars,
            "has_image": process.has_singularity_image(),
            "has_venv": process.has_virtual_environment(),
            "metadata": process.model_dump(exclude={"process_dir"}),
            "process_dir_metadata": process.process_dir.model_dump()
        }
        
        # Check if document already exists
        existing_doc = self.mongo_client.find_one(
            CollectionNames.PROCESSES, 
            {"process_id": process.process_id}
        )
        
        if existing_doc:
            # Update existing document
            self.logger.info(f"Updating existing document for process {process.process_id}")
            process_doc["updated_at"] = datetime.datetime.now().isoformat()
            result = self.mongo_client.update_one(
                CollectionNames.PROCESSES,
                {"process_id": process.process_id},
                {"$set": process_doc}
            )
            return str(existing_doc["_id"])
        else:
            # Insert new document
            self.logger.info(f"Creating new document for process {process.process_id}")
            doc_id = self.mongo_client.insert_one(CollectionNames.PROCESSES, process_doc)
            return doc_id
    
    def sync_from_db(self, process_id: str) -> bool:
        """
        Sync NeuProcess data from DB to HPC.
        
        Args:
            process_id: ID of the process to sync
            
        Returns:
            True if sync was successful, False otherwise
        """
        self.logger.info(f"Syncing process {process_id} from DB to HPC")
        
        # Load process from DB
        process = self.load_from_db(process_id)
        if not process:
            self.logger.error(f"Process {process_id} not found in DB")
            return False
        
        try:
            # Create the process directory if it doesn't exist
            process_dir_path = PATHS.workdir / process_id
            process_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Save model.json
            model_path = process_dir_path / "model.json"
            with open(model_path, "w") as f:
                json.dump(process.process_dir.model_dump(), f, indent=4)
            
            # Generate process directory contents
            process.process_dir.generate_working_directory(str(process_dir_path))
            
            # If image exists in DB metadata but not in HPC, sync it
            if "has_image" in process.metadata and process.metadata["has_image"]:
                if not process.has_singularity_image():
                    self.logger.info(f"Building Singularity image for process {process_id}")
                    process.build_singularity_image()
            
            # If venv exists in DB metadata but not in HPC, sync it
            if "has_venv" in process.metadata and process.metadata["has_venv"]:
                if not process.has_virtual_environment():
                    self.logger.info(f"Creating virtual environment for process {process_id}")
                    process.create_virtual_environment()
            
            self.logger.info(f"Successfully synced process {process_id} from DB to HPC")
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing process from DB to HPC: {e}")
            return False
