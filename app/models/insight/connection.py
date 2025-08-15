from ...utils.constants import *

from typing import Optional, Any
import logging, json
from pathlib import Path

from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient
import numpy as np

logger = logging.getLogger(__name__)

class LLMConnection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    client: AsyncOpenAI
    provider: OpenAIProvider
    model: OpenAIModel
    
    @classmethod
    def from_defaults(cls) -> "LLMConnection":
        client = AsyncOpenAI(
            base_url=OPENAI_CLIENT_BASE_URL,
            default_headers=OPENAI_CLIENT_DEFAULT_HEADERS
        )
        provider = OpenAIProvider(openai_client=client)
        model = OpenAIModel(OPENAI_DEFAULT_MODEL, provider=provider)
        
        return cls(
            client=client,
            provider=provider,
            model=model
        )
        
class VectorDBConnection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    client: MilvusClient
    embedding_model: SentenceTransformer = Field(default_factory=lambda: SentenceTransformer("BAAI/bge-large-en"))
    embedding_dimension: int = Field(default=1024)
    
    @classmethod
    def from_defaults(cls) -> "VectorDBConnection":
        if not Path(MILVUS_VECTOR_DB_URI).parent.exists():
            Path(MILVUS_VECTOR_DB_URI).parent.mkdir(parents=True, exist_ok=True)
        client = MilvusClient(uri=MILVUS_VECTOR_DB_URI)
        logger.info(f"Connecting to Milvus at {MILVUS_VECTOR_DB_URI}")
        
        return cls(
            client=client
        )

    def set_collections(self) -> None:
        collection_names: list[str] = [
            MILVUS_PIPELINE_REPORTS_COLLECTION,
            MILVUS_PAPERS_COLLECTION,
            MILVUS_SPECS_COLLECTION,
            MILVUS_ANSWERS_COLLECTION
        ]
        
        # Create collections if they do not exist
        for collection_name in collection_names:
            if not self.client.has_collection(collection_name):
                self.client.create_collection(
                    collection_name=collection_name,
                    dimension=self.embedding_dimension,
                    metric_type="IP"
                )
                logger.info(f"Collection {collection_name} created.")
            else:   
                logger.info(f"Collection {collection_name} already exists.")
    
    def create_embeddings(self, records: list[dict], label_fields: Optional[list[str]] = None) -> list[dict]:
        """
        Create embeddings from list of dicts (usually from a DB).
        Separate labels from embeddings.
        """
        embedding_records: list[dict] = []
        for record in records:
            if not isinstance(record, dict):
                raise ValueError(f"Records must be a list of dictionaries.")
            record_to_vectorize: dict = {key: value for key, value in record.items() if key not in label_fields}
            labels: dict = {key: value for key, value in record.items() if key in label_fields}
            embedding_records.append({
                "vector": self.embedding_model.encode(json.dumps(record_to_vectorize)),
                "record": record_to_vectorize,
                **labels
            })
            
        return embedding_records