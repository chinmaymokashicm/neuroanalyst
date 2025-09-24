"""
Database Dependency Module

This module provides FastAPI dependency functions for accessing the MongoDB database.
"""

from fastapi import Depends
from typing import Generator, Optional

from ..models.database.mongo_client import MongoDBClient


def get_db_client(db_name: Optional[str] = None) -> Generator[MongoDBClient, None, None]:
    """
    Get a MongoDB client as a FastAPI dependency.
    
    Args:
        db_name: Optional database name to use
        
    Returns:
        Generator yielding a MongoDBClient instance
    """
    client = MongoDBClient(db_name)
    try:
        client.connect()
        yield client
    finally:
        client.close()
