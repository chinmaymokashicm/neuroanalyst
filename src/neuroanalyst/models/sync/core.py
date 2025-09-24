"""
Sync Module Core

This module defines the core functionality for synchronizing data between HPC and database.
It provides base classes, enums, and utilities for the sync operations.
"""

import os
import json
import logging
import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple

from pydantic import BaseModel, Field, validator

from ...utils.constants import PATHS


class SyncDirection(str, Enum):
    """Enum for sync direction."""
    HPC_TO_DB = "hpc_to_db"  # Sync from HPC to DB
    DB_TO_HPC = "db_to_hpc"  # Sync from DB to HPC


class SyncStrategy(str, Enum):
    """Enum for sync strategy."""
    AD_HOC = "ad_hoc"       # On-demand sync
    PERIODIC = "periodic"   # Scheduled sync


class SyncConfig(BaseModel):
    """Configuration model for sync operations."""
    
    strategy: SyncStrategy = Field(
        default=SyncStrategy.AD_HOC,
        description="Sync strategy (ad-hoc or periodic)"
    )
    
    interval: Optional[str] = Field(
        default="1h",
        description="Sync interval for periodic strategy (e.g., 1h, 30m)"
    )
    
    batch_size: int = Field(
        default=100,
        description="Maximum number of items to sync in a batch"
    )
    
    retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts for failed sync"
    )
    
    compression: bool = Field(
        default=True,
        description="Whether to compress data before transfer"
    )
    
    @validator('interval')
    def validate_interval(cls, v, values):
        """Validate that interval is provided for periodic strategy."""
        if values.get('strategy') == SyncStrategy.PERIODIC and not v:
            raise ValueError("Interval must be provided for periodic sync strategy")
        return v


class SyncBase(BaseModel):
    """Base class for all sync operations."""
    
    config: SyncConfig = Field(
        default_factory=SyncConfig,
        description="Sync configuration"
    )
    
    logger: Optional[logging.Logger] = Field(
        default=None,
        description="Logger instance",
        exclude=True
    )
    
    def __init__(self, **data):
        """Initialize the sync base class with logger."""
        super().__init__(**data)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def compare_dicts(self, hpc_data: Dict[str, Any], db_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two dictionaries and return the differences.
        
        Args:
            hpc_data: Data from HPC
            db_data: Data from DB
            
        Returns:
            Dictionary with differences
        """
        diff = {}
        
        # Check all keys in hpc_data
        for key, value in hpc_data.items():
            # Skip internal MongoDB keys
            if key.startswith('_'):
                continue
                
            if key not in db_data:
                diff[key] = {"source": "hpc", "value": value, "status": "only_in_hpc"}
            elif isinstance(value, dict) and isinstance(db_data[key], dict):
                nested_diff = self.compare_dicts(value, db_data[key])
                if nested_diff:
                    diff[key] = nested_diff
            elif value != db_data[key]:
                diff[key] = {
                    "hpc_value": value,
                    "db_value": db_data[key],
                    "status": "different"
                }
        
        # Check for keys in db_data that are not in hpc_data
        for key, value in db_data.items():
            # Skip internal MongoDB keys
            if key.startswith('_'):
                continue
                
            if key not in hpc_data:
                diff[key] = {"source": "db", "value": value, "status": "only_in_db"}
        
        return diff
