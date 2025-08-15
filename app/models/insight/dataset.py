"""
Work with generating insights wrt BIDS datasets
"""
from .connection import LLMConnection, VectorDBConnection
from ...utils.db import find_one_from_db, find_many_from_db
from ...utils.constants import *

from pathlib import Path, PosixPath
import logging

from pydantic import BaseModel, Field, DirectoryPath
import numpy as np

# vector_db_connection: VectorDBConnection = VectorDBConnection.from_defaults()

def get_metrics_embeddings(pipeline_id: str) -> np.ndarray:
    """
    Get the embeddings for the metrics
    """
    records: list[dict] = find_many_from_db(COLLECTION_SUMMARIES, {"pipeline_id": pipeline_id})
    metrics: list[dict] = [record["metrics"] for record in records]
    # Create chunks by splitting the records by attaching each metric dict to the rest of the record, returning a list of dicts of length equal to the number of metrics
    metrics_embeddings: list[dict] = []
    for record in records:
        for metric in record["metrics"]:
            metrics_embeddings.append({**record, **metric})
    
    return metrics_embeddings