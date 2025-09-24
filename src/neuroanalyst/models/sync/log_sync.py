"""
Log Sync Module

This module provides synchronization functionality for component logs between HPC and DB.
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
from .core import SyncBase, SyncDirection, SyncStrategy, SyncConfig


class LogSync(SyncBase):
    """
    Class for synchronizing log data between HPC and DB.
    
    This class provides methods to:
    1. Load log data from HPC
    2. Load log data from DB
    3. Compare differences between HPC and DB data
    4. Sync log data from HPC to DB
    5. Sync log data from DB to HPC
    """
    
    def __init__(self, **data):
        """Initialize the LogSync instance."""
        super().__init__(**data)
        self.mongo_client = MongoDBClient()
        self.mongo_client.connect()
    
    def load_from_hpc(self, component_id: str, component_type: str) -> Optional[Dict[str, Any]]:
        """
        Load log data from HPC storage.
        
        Args:
            component_id: ID of the component (process, exec, pipeline)
            component_type: Type of the component ('process', 'exec', 'pipeline')
            
        Returns:
            Dictionary with log data if found, None otherwise
        """
        self.logger.info(f"Loading logs for {component_type} {component_id} from HPC storage")
        
        # Determine log file path based on component type
        log_dir_path = PATHS.logs / component_type / component_id
        
        if component_type == 'process':
            log_files = ["stdout.log", "stderr.log", "exec.log"]
        elif component_type == 'exec':
            log_files = ["stdout.log", "stderr.log", "exec.log"]
        elif component_type == 'pipeline':
            log_files = ["pipeline.log", "execution.log"]
        else:
            self.logger.error(f"Invalid component type: {component_type}")
            return None
        
        # Check if log directory exists
        if not log_dir_path.exists():
            self.logger.warning(f"Log directory {log_dir_path} does not exist")
            return None
        
        # Load logs
        log_data = {
            "component_id": component_id,
            "component_type": component_type,
            "logs": {}
        }
        
        for log_file in log_files:
            log_path = log_dir_path / log_file
            if log_path.exists():
                try:
                    with open(log_path, "r") as f:
                        content = f.read()
                    log_data["logs"][log_file] = content
                except Exception as e:
                    self.logger.error(f"Error reading log file {log_path}: {e}")
        
        if not log_data["logs"]:
            self.logger.warning(f"No log files found for {component_type} {component_id}")
            return None
        
        # Add metadata
        log_data["last_updated_hpc"] = datetime.datetime.now().isoformat()
        log_data["log_files"] = list(log_data["logs"].keys())
        
        return log_data
    
    def load_from_db(self, component_id: str, component_type: str) -> Optional[Dict[str, Any]]:
        """
        Load log data from DB.
        
        Args:
            component_id: ID of the component (process, exec, pipeline)
            component_type: Type of the component ('process', 'exec', 'pipeline')
            
        Returns:
            Dictionary with log data if found, None otherwise
        """
        self.logger.info(f"Loading logs for {component_type} {component_id} from DB")
        
        # Find log document in MongoDB
        log_doc = self.mongo_client.find_one(
            CollectionNames.LOGS, 
            {"component_id": component_id, "component_type": component_type}
        )
        
        if not log_doc:
            self.logger.warning(f"Logs for {component_type} {component_id} not found in DB")
            return None
        
        return log_doc
    
    def compare_diff(self, component_id: str, component_type: str) -> Dict[str, Any]:
        """
        Compare differences between HPC and DB log data.
        
        Args:
            component_id: ID of the component
            component_type: Type of the component
            
        Returns:
            Dictionary with differences
        """
        self.logger.info(f"Comparing log differences for {component_type} {component_id}")
        
        # Load data from both sources
        hpc_log_data = self.load_from_hpc(component_id, component_type)
        db_log_data = self.load_from_db(component_id, component_type)
        
        if not hpc_log_data and not db_log_data:
            self.logger.warning(f"Logs for {component_type} {component_id} not found in HPC or DB")
            return {"error": "Logs not found in HPC or DB"}
        
        if not hpc_log_data:
            self.logger.warning(f"Logs for {component_type} {component_id} not found in HPC")
            return {"error": "Logs not found in HPC", "exists_in": "db"}
        
        if not db_log_data:
            self.logger.warning(f"Logs for {component_type} {component_id} not found in DB")
            return {"error": "Logs not found in DB", "exists_in": "hpc"}
        
        # Prepare for comparison
        diff = {
            "component_id": component_id,
            "component_type": component_type,
            "log_files": {
                "only_in_hpc": [],
                "only_in_db": [],
                "in_both": []
            },
            "content_diff": {}
        }
        
        # Compare log files
        hpc_log_files = list(hpc_log_data["logs"].keys())
        db_log_files = list(db_log_data["logs"].keys())
        
        for log_file in hpc_log_files:
            if log_file in db_log_files:
                diff["log_files"]["in_both"].append(log_file)
                
                # Compare content
                hpc_content = hpc_log_data["logs"][log_file]
                db_content = db_log_data["logs"][log_file]
                
                if hpc_content != db_content:
                    hpc_lines = hpc_content.splitlines()
                    db_lines = db_content.splitlines()
                    
                    # Check if HPC has more log lines (newer)
                    if len(hpc_lines) > len(db_lines):
                        diff["content_diff"][log_file] = {
                            "status": "hpc_newer",
                            "hpc_lines": len(hpc_lines),
                            "db_lines": len(db_lines),
                            "extra_lines": len(hpc_lines) - len(db_lines)
                        }
                    elif len(db_lines) > len(hpc_lines):
                        diff["content_diff"][log_file] = {
                            "status": "db_newer",
                            "hpc_lines": len(hpc_lines),
                            "db_lines": len(db_lines),
                            "extra_lines": len(db_lines) - len(hpc_lines)
                        }
                    else:
                        diff["content_diff"][log_file] = {
                            "status": "content_different",
                            "hpc_lines": len(hpc_lines),
                            "db_lines": len(db_lines)
                        }
            else:
                diff["log_files"]["only_in_hpc"].append(log_file)
        
        for log_file in db_log_files:
            if log_file not in hpc_log_files:
                diff["log_files"]["only_in_db"].append(log_file)
        
        return diff
    
    def sync_to_db(self, component_id: str, component_type: str) -> str:
        """
        Sync log data from HPC to DB.
        
        Args:
            component_id: ID of the component
            component_type: Type of the component
            
        Returns:
            MongoDB document ID or error message
        """
        self.logger.info(f"Syncing logs for {component_type} {component_id} to DB")
        
        # Load log data from HPC
        log_data = self.load_from_hpc(component_id, component_type)
        if not log_data:
            error_msg = f"Logs for {component_type} {component_id} not found in HPC"
            self.logger.error(error_msg)
            return error_msg
        
        # Add timestamp
        log_data["updated_at"] = datetime.datetime.now().isoformat()
        
        # Check if document already exists
        existing_doc = self.mongo_client.find_one(
            CollectionNames.LOGS, 
            {"component_id": component_id, "component_type": component_type}
        )
        
        if existing_doc:
            # Update existing document
            self.logger.info(f"Updating existing log document for {component_type} {component_id}")
            result = self.mongo_client.update_one(
                CollectionNames.LOGS,
                {"component_id": component_id, "component_type": component_type},
                {"$set": log_data}
            )
            return str(existing_doc["_id"])
        else:
            # Insert new document
            self.logger.info(f"Creating new log document for {component_type} {component_id}")
            doc_id = self.mongo_client.insert_one(CollectionNames.LOGS, log_data)
            return doc_id
    
    def sync_from_db(self, component_id: str, component_type: str) -> bool:
        """
        Sync log data from DB to HPC.
        
        Args:
            component_id: ID of the component
            component_type: Type of the component
            
        Returns:
            True if sync was successful, False otherwise
        """
        self.logger.info(f"Syncing logs for {component_type} {component_id} from DB to HPC")
        
        # Load log data from DB
        log_data = self.load_from_db(component_id, component_type)
        if not log_data:
            self.logger.error(f"Logs for {component_type} {component_id} not found in DB")
            return False
        
        try:
            # Determine log directory path
            log_dir_path = PATHS.logs / component_type / component_id
            
            # Create log directory if it doesn't exist
            log_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Write log files
            for log_file, content in log_data["logs"].items():
                log_path = log_dir_path / log_file
                with open(log_path, "w") as f:
                    f.write(content)
            
            self.logger.info(f"Successfully synced logs for {component_type} {component_id} from DB to HPC")
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing logs from DB to HPC: {e}")
            return False
