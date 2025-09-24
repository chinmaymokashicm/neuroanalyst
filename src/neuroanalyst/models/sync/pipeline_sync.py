"""
NeuPipeline Sync Module

This module provides synchronization functionality for NeuPipeline instances between HPC and DB.
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
from ..pipeline.core import NeuPipeline
from .core import SyncBase, SyncDirection, SyncStrategy, SyncConfig


class NeuPipelineSync(SyncBase):
    """
    Class for synchronizing NeuPipeline data between HPC and DB.
    
    This class provides methods to:
    1. Load NeuPipeline data from HPC
    2. Load NeuPipeline data from DB
    3. Compare differences between HPC and DB data
    4. Sync data from HPC to DB
    5. Sync data from DB to HPC
    """
    
    def __init__(self, **data):
        """Initialize the NeuPipelineSync instance."""
        super().__init__(**data)
        self.mongo_client = MongoDBClient()
        self.mongo_client.connect()
    
    def load_from_hpc(self, pipeline_id: str) -> Optional[NeuPipeline]:
        """
        Load NeuPipeline data from HPC storage.
        
        Args:
            pipeline_id: ID of the pipeline to load
            
        Returns:
            NeuPipeline instance if found, None otherwise
        """
        self.logger.info(f"Loading NeuPipeline {pipeline_id} from HPC storage")
        
        # Check if pipeline directory exists
        pipeline_dir_path = PATHS.pipelines / pipeline_id
        if not pipeline_dir_path.exists():
            self.logger.warning(f"Pipeline directory {pipeline_dir_path} does not exist")
            return None
        
        # Load model.json from the pipeline directory
        model_path = pipeline_dir_path / "model.json"
        if not model_path.exists():
            self.logger.warning(f"Model file {model_path} does not exist")
            return None
        
        try:
            # Load NeuPipeline from model.json
            with open(model_path, "r") as f:
                model_data = json.load(f)
            
            pipeline = NeuPipeline.model_validate(model_data)
            return pipeline
        
        except Exception as e:
            self.logger.error(f"Error loading pipeline from HPC storage: {e}")
            return None
    
    def load_from_db(self, pipeline_id: str) -> Optional[NeuPipeline]:
        """
        Load NeuPipeline data from DB.
        
        Args:
            pipeline_id: ID of the pipeline to load
            
        Returns:
            NeuPipeline instance if found, None otherwise
        """
        self.logger.info(f"Loading NeuPipeline {pipeline_id} from DB")
        
        # Find document in MongoDB
        pipeline_doc = self.mongo_client.find_one(
            CollectionNames.PIPELINES, 
            {"pipeline_id": pipeline_id}
        )
        
        if not pipeline_doc:
            self.logger.warning(f"Pipeline {pipeline_id} not found in DB")
            return None
        
        try:
            # Reconstruct NeuPipeline from metadata
            if "metadata" in pipeline_doc:
                pipeline = NeuPipeline.model_validate(pipeline_doc["metadata"])
                return pipeline
            else:
                self.logger.warning(f"Pipeline {pipeline_id} has no metadata in DB")
                return None
            
        except Exception as e:
            self.logger.error(f"Error loading pipeline from DB: {e}")
            return None
    
    def compare_diff(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Compare differences between HPC and DB data for a pipeline.
        
        Args:
            pipeline_id: ID of the pipeline to compare
            
        Returns:
            Dictionary with differences
        """
        self.logger.info(f"Comparing differences for pipeline {pipeline_id}")
        
        # Load data from both sources
        hpc_pipeline = self.load_from_hpc(pipeline_id)
        db_pipeline = self.load_from_db(pipeline_id)
        
        if not hpc_pipeline and not db_pipeline:
            self.logger.warning(f"Pipeline {pipeline_id} not found in HPC or DB")
            return {"error": "Pipeline not found in HPC or DB"}
        
        if not hpc_pipeline:
            self.logger.warning(f"Pipeline {pipeline_id} not found in HPC")
            return {"error": "Pipeline not found in HPC", "exists_in": "db"}
        
        if not db_pipeline:
            self.logger.warning(f"Pipeline {pipeline_id} not found in DB")
            return {"error": "Pipeline not found in DB", "exists_in": "hpc"}
        
        # Convert both to dictionaries for comparison
        hpc_data = hpc_pipeline.model_dump()
        db_data = db_pipeline.model_dump()
        
        # Compare dictionaries
        return self.compare_dicts(hpc_data, db_data)
    
    def sync_to_db(self, pipeline: Union[NeuPipeline, str]) -> str:
        """
        Sync NeuPipeline data from HPC to DB.
        
        Args:
            pipeline: NeuPipeline instance or pipeline ID
            
        Returns:
            MongoDB document ID or error message
        """
        self.logger.info(f"Syncing pipeline to DB")
        
        # If pipeline_id is provided, load from HPC first
        if isinstance(pipeline, str):
            pipeline_instance = self.load_from_hpc(pipeline)
            if not pipeline_instance:
                error_msg = f"Pipeline {pipeline} not found in HPC"
                self.logger.error(error_msg)
                return error_msg
            pipeline = pipeline_instance
        
        # Create MongoDB document
        pipeline_doc = {
            "pipeline_id": pipeline.pipeline_id,
            "name": pipeline.name,
            "description": pipeline.description,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "scheduler": pipeline.scheduler.value if hasattr(pipeline, 'scheduler') else None,
            "status": pipeline.status.value if hasattr(pipeline, 'status') else None,
            "metadata": pipeline.model_dump()
        }
        
        # Check if document already exists
        existing_doc = self.mongo_client.find_one(
            CollectionNames.PIPELINES, 
            {"pipeline_id": pipeline.pipeline_id}
        )
        
        if existing_doc:
            # Update existing document
            self.logger.info(f"Updating existing document for pipeline {pipeline.pipeline_id}")
            pipeline_doc["updated_at"] = datetime.datetime.now().isoformat()
            result = self.mongo_client.update_one(
                CollectionNames.PIPELINES,
                {"pipeline_id": pipeline.pipeline_id},
                {"$set": pipeline_doc}
            )
            return str(existing_doc["_id"])
        else:
            # Insert new document
            self.logger.info(f"Creating new document for pipeline {pipeline.pipeline_id}")
            doc_id = self.mongo_client.insert_one(CollectionNames.PIPELINES, pipeline_doc)
            return doc_id
    
    def sync_from_db(self, pipeline_id: str) -> bool:
        """
        Sync NeuPipeline data from DB to HPC.
        
        Args:
            pipeline_id: ID of the pipeline to sync
            
        Returns:
            True if sync was successful, False otherwise
        """
        self.logger.info(f"Syncing pipeline {pipeline_id} from DB to HPC")
        
        # Load pipeline from DB
        pipeline = self.load_from_db(pipeline_id)
        if not pipeline:
            self.logger.error(f"Pipeline {pipeline_id} not found in DB")
            return False
        
        try:
            # Create the pipeline directory if it doesn't exist
            pipeline_dir_path = PATHS.pipelines / pipeline_id
            pipeline_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Save model.json
            model_path = pipeline_dir_path / "model.json"
            with open(model_path, "w") as f:
                json.dump(pipeline.model_dump(), f, indent=4)
            
            # Generate pipeline script if needed
            if not (pipeline_dir_path / f"{pipeline_id}.sh").exists():
                self.logger.info(f"Generating pipeline script for {pipeline_id}")
                pipeline.generate_execution_script()
            
            self.logger.info(f"Successfully synced pipeline {pipeline_id} from DB to HPC")
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing pipeline from DB to HPC: {e}")
            return False
