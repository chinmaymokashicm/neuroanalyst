"""
Connection to a MongoDB database
"""
from ...utils.db import MONGO_URI, DB_NAME
from ...utils.exceptions import DBRecordMissing

from typing import Optional
import re

from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.database import Database

class Connection(BaseModel, arbitrary_types_allowed=True):
    client: MongoClient = Field(title="The MongoDB client object")
    db: Database = Field(title="The MongoDB database object")
    
    @classmethod
    def from_defaults(cls):
        client: MongoClient = MongoClient(MONGO_URI)
        db: Database = client[DB_NAME]
        return cls(client=client, db=db)
    
    @classmethod
    def from_user(cls, mongo_uri: str, db_name: str):
        client: MongoClient = MongoClient(mongo_uri)
        db: Database = client[db_name]
        return cls(client=client, db=db)