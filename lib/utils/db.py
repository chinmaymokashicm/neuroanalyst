"""
Connection to a MongoDB database
"""
from .constants import MONGO_URI, DB_NAME
from .exceptions import DBRecordMissing

from typing import Optional

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
    
def insert_to_db(collection_name: str, record: dict, connection: Optional[Connection] = None):
    try:
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[collection_name]
        collection.insert_one(record)
        print(f"Record inserted into collection {collection_name}")
    except Exception as e:
        raise Exception(f"Failed to insert record into collection {collection_name}. Error: {e}")
    
def update_db_record(collection_name: str, filter: dict, update: dict, connection: Optional[Connection] = None):
    try:
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[collection_name]
        collection.update_one(filter, {"$set": update})
        print(f"Record updated in collection {collection_name}")
    except Exception as e:
        raise Exception(f"Failed to update record in collection {collection_name}. Error: {e}")
    
def find_one_from_db(collection_name: str, filter: dict, field_name: Optional[str] = None, connection: Optional[Connection] = None) -> dict:
    try:
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[collection_name]
        record = collection.find_one(filter)
        if record is None:
            raise DBRecordMissing(f"Record not found in collection {collection_name} with filter {filter}")
        return record if field_name is None else record[field_name]
    except Exception as e:
        raise Exception(f"Failed to find record in collection {collection_name}. Error: {e}")