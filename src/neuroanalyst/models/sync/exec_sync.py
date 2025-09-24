"""
NeuProcessExec Sync Module

This module provides synchronization functionality for NeuProcessExec instances between HPC and DB.
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
from ..process.exec.core import NeuProcessExec
from .core import SyncBase, SyncDirection, SyncStrategy, SyncConfig


class NeuProcessExecSync(SyncBase):
    """
    Class for synchronizing NeuProcessExec data between HPC and DB.
    
    This class provides methods to:
    1. Load NeuProcessExec data from HPC
    2. Load NeuProcessExec data from DB
    3. Compare differences between HPC and DB data
    4. Sync data from HPC to DB
    5. Sync data from DB to HPC
    """
    
    def __init__(self, **data):
        """Initialize the NeuProcessExecSync instance."""
        super().__init__(**data)
        self.mongo_client = MongoDBClient()
        self.mongo_client.connect()
    
    def load_from_hpc(self, exec_id: str) -> Optional[NeuProcessExec]:
        """
        Load NeuProcessExec data from HPC storage.
        
        Args:
            exec_id: ID of the execution instance to load
            
        Returns:
            NeuProcessExec instance if found, None otherwise
        """
        self.logger.info(f"Loading NeuProcessExec {exec_id} from HPC storage")
        
        # Check if exec directory exists
        exec_dir_path = PATHS.get_process_exec_path(exec_id)
        if not exec_dir_path.exists():
            self.logger.warning(f"Exec directory {exec_dir_path} does not exist")
            return None
        
        # Load model.json from the exec directory
        model_path = exec_dir_path / "model.json"
        if not model_path.exists():
            self.logger.warning(f"Model file {model_path} does not exist")
            return None
        
        try:
            # Load NeuProcessExec from model.json
            with open(model_path, "r") as f:
                model_data = json.load(f)
            
            exec_instance = NeuProcessExec.model_validate(model_data)
            return exec_instance
        
        except Exception as e:
            self.logger.error(f"Error loading execution instance from HPC storage: {e}")
            return None
    
    def load_from_db(self, exec_id: str) -> Optional[NeuProcessExec]:
        """
        Load NeuProcessExec data from DB.
        
        Args:
            exec_id: ID of the execution instance to load
            
        Returns:
            NeuProcessExec instance if found, None otherwise
        """
        self.logger.info(f"Loading NeuProcessExec {exec_id} from DB")
        
        # Find document in MongoDB
        exec_doc = self.mongo_client.find_one(
            CollectionNames.EXECUTIONS, 
            {"exec_id": exec_id}
        )
        
        if not exec_doc:
            self.logger.warning(f"Execution instance {exec_id} not found in DB")
            return None
        
        try:
            # Reconstruct NeuProcessExec from metadata
            if "metadata" in exec_doc:
                exec_instance = NeuProcessExec.model_validate(exec_doc["metadata"])
                return exec_instance
            else:
                self.logger.warning(f"Execution instance {exec_id} has no metadata in DB")
                return None
            
        except Exception as e:
            self.logger.error(f"Error loading execution instance from DB: {e}")
            return None
    
    def compare_diff(self, exec_id: str) -> Dict[str, Any]:
        """
        Compare differences between HPC and DB data for an execution instance.
        
        Args:
            exec_id: ID of the execution instance to compare
            
        Returns:
            Dictionary with differences
        """
        self.logger.info(f"Comparing differences for execution instance {exec_id}")
        
        # Load data from both sources
        hpc_exec = self.load_from_hpc(exec_id)
        db_exec = self.load_from_db(exec_id)
        
        if not hpc_exec and not db_exec:
            self.logger.warning(f"Execution instance {exec_id} not found in HPC or DB")
            return {"error": "Execution instance not found in HPC or DB"}
        
        if not hpc_exec:
            self.logger.warning(f"Execution instance {exec_id} not found in HPC")
            return {"error": "Execution instance not found in HPC", "exists_in": "db"}
        
        if not db_exec:
            self.logger.warning(f"Execution instance {exec_id} not found in DB")
            return {"error": "Execution instance not found in DB", "exists_in": "hpc"}
        
        # Convert both to dictionaries for comparison
        hpc_data = hpc_exec.model_dump()
        db_data = db_exec.model_dump()
        
        # Compare dictionaries
        return self.compare_dicts(hpc_data, db_data)
    
    def sync_to_db(self, exec_instance: Union[NeuProcessExec, str]) -> str:
        """
        Sync NeuProcessExec data from HPC to DB.
        
        Args:
            exec_instance: NeuProcessExec instance or execution ID
            
        Returns:
            MongoDB document ID or error message
        """
        self.logger.info(f"Syncing execution instance to DB")
        
        # If exec_id is provided, load from HPC first
        if isinstance(exec_instance, str):
            exec_obj = self.load_from_hpc(exec_instance)
            if not exec_obj:
                error_msg = f"Execution instance {exec_instance} not found in HPC"
                self.logger.error(error_msg)
                return error_msg
            exec_instance = exec_obj
        
        # Create MongoDB document
        exec_doc = {
            "exec_id": exec_instance.exec_id,
            "process_id": exec_instance.process.process_id if hasattr(exec_instance, 'process') else None,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "status": exec_instance.status.value if hasattr(exec_instance, 'status') else None,
            "execution_mode": exec_instance.execution_mode.value if hasattr(exec_instance, 'execution_mode') else None,
            "scheduler": exec_instance.scheduler.value if hasattr(exec_instance, 'scheduler') else None,
            "bind_values": exec_instance.bind_values,
            "env_values": exec_instance.env_values,
            "metadata": exec_instance.model_dump()
        }
        
        # Check if document already exists
        existing_doc = self.mongo_client.find_one(
            CollectionNames.EXECUTIONS, 
            {"exec_id": exec_instance.exec_id}
        )
        
        if existing_doc:
            # Update existing document
            self.logger.info(f"Updating existing document for execution instance {exec_instance.exec_id}")
            exec_doc["updated_at"] = datetime.datetime.now().isoformat()
            result = self.mongo_client.update_one(
                CollectionNames.EXECUTIONS,
                {"exec_id": exec_instance.exec_id},
                {"$set": exec_doc}
            )
            return str(existing_doc["_id"])
        else:
            # Insert new document
            self.logger.info(f"Creating new document for execution instance {exec_instance.exec_id}")
            doc_id = self.mongo_client.insert_one(CollectionNames.EXECUTIONS, exec_doc)
            return doc_id
    
    def sync_from_db(self, exec_id: str) -> bool:
        """
        Sync NeuProcessExec data from DB to HPC.
        
        Args:
            exec_id: ID of the execution instance to sync
            
        Returns:
            True if sync was successful, False otherwise
        """
        self.logger.info(f"Syncing execution instance {exec_id} from DB to HPC")
        
        # Load execution instance from DB
        exec_instance = self.load_from_db(exec_id)
        if not exec_instance:
            self.logger.error(f"Execution instance {exec_id} not found in DB")
            return False
        
        try:
            # Create the exec directory if it doesn't exist
            exec_dir_path = PATHS.get_process_exec_path(exec_id)
            exec_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Save model.json
            model_path = exec_dir_path / "model.json"
            with open(model_path, "w") as f:
                json.dump(exec_instance.model_dump(), f, indent=4)
            
            # Additional logic to handle execution artifacts if needed
            
            self.logger.info(f"Successfully synced execution instance {exec_id} from DB to HPC")
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing execution instance from DB to HPC: {e}")
            return False
