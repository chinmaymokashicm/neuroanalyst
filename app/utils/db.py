"""
Connection to a MongoDB database
"""
from .constants import MONGO_URI, DB_NAME
from .exceptions import DBRecordMissing, MongoDBConnectionError

from typing import Optional
import re, logging

from bids import BIDSLayout
from bids.layout.models import BIDSJSONFile
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

class Connection(BaseModel, arbitrary_types_allowed=True):
    client: MongoClient = Field(title="The MongoDB client object")
    db: Database = Field(title="The MongoDB database object")
    
    @classmethod
    def from_defaults(cls):
        client: MongoClient = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3)
        db: Database = client[DB_NAME]
        return cls(client=client, db=db)
    
    @classmethod
    def from_user(cls, mongo_uri: str, db_name: str):
        client: MongoClient = MongoClient(mongo_uri)
        db: Database = client[db_name]
        return cls(client=client, db=db)

def check_connection(connection: Optional[Connection] = None) -> dict:
    connection = Connection.from_defaults() if connection is None else connection
    return connection.client.server_info()

def find_one_from_db(collection_name: str, filter: dict = {}, field_names: list[str] = [], connection: Optional[Connection] = None) -> dict:
    try:
        check_connection()
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[collection_name]
        record = collection.find_one(filter, {"_id": 0})
        if record is None:
            raise DBRecordMissing(f"Record not found in collection {collection_name} with filter {filter}")
        # return record if field_names is None else record[field_names]
        return record if field_names == [] else {field: record[field] for field in field_names}
    except ServerSelectionTimeoutError as e:
        logger.exception(f"MongoDB connection error: {e}")
        return {}
    except Exception as e:
        exception_message: str = f"Failed to find record in collection {collection_name}. Error: {e}"
        logger.exception(exception_message)
        raise Exception(exception_message)

def find_many_from_db(collection_name: str, filter: dict = {}, field_names: list[str] = [], connection: Optional[Connection] = None) -> list[dict]:
    try:
        check_connection()
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[collection_name]
        records = collection.find(filter, {"_id": 0})
        if records is None:
            raise DBRecordMissing(f"No records found in collection {collection_name} with filter {filter}")
        return [record for record in records] if field_names == [] else [{field: record[field] for field in field_names} for record in records]
    except ServerSelectionTimeoutError as e:
        logger.exception(f"MongoDB connection error: {e}")
        return []
    except Exception as e:
        raise Exception(f"Failed to find records in collection {collection_name}. Error: {e}")
    
def search_by_keyword(collection_name: str, keyword: str, connection: Optional[Connection] = None) -> list[dict]:
    try:
        check_connection()
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[collection_name]
        regex_pattern: re.Pattern = re.compile(f".*{keyword}.*", re.IGNORECASE)
        query: dict = { "$or": [] }
        first_record = collection.find_one()
        if first_record is None:
            raise DBRecordMissing(f"Collection {collection_name} is empty")
        for field in first_record.keys():
            query["$or"].append({ field: { "$regex": regex_pattern } })
        records = collection.find(query, {"_id": 0})
        if records is None:
            raise DBRecordMissing(f"No records found in collection {collection_name} with keyword {keyword}")
        return [record for record in records]
    except ServerSelectionTimeoutError as e:
        logger.exception(f"MongoDB connection error: {e}")
        return []
    except Exception as e:
        raise Exception(f"Failed to search records in collection {collection_name} with keyword {keyword}. Error: {e}")

def insert_to_db(collection_name: str, record: dict, connection: Optional[Connection] = None) -> None:
    try:
        check_connection()
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[collection_name]
        collection.insert_one(record)
        logger.info(f"Record inserted into collection {collection_name}")
    except ServerSelectionTimeoutError as e:
        logger.exception(f"MongoDB connection error: {e}")
    except Exception as e:
        exception_message: str = f"Failed to insert record into collection {collection_name}. Error: {e}"
        logger.exception(exception_message)
        raise Exception(exception_message)
    
def update_db_record(collection_name: str, filter: dict, update: dict, connection: Optional[Connection] = None) -> None:
    try:
        check_connection()
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[collection_name]
        # collection.update_one(filter, {"$set": update}, upsert=True)
        collection.update_one(filter, {"$set": update})
        logger.info(f"Record updated in collection {collection_name}")
    except ServerSelectionTimeoutError as e:
        logger.exception(f"MongoDB connection error: {e}")
    except Exception as e:
        exception_message: str = f"Failed to update record in collection {collection_name}. Error: {e}"
        logger.exception(exception_message)
        raise Exception(exception_message)
    
def delete_db_record(collection_name: str, filter: dict, connection: Optional[Connection] = None) -> None:
    try:
        check_connection()
        connection: Connection = Connection.from_defaults() if connection is None else connection
        collection = connection.db[collection_name]
        collection.delete_one(filter)
        logger.info(f"Record deleted from collection {collection_name}")
    except ServerSelectionTimeoutError as e:
        logger.exception(f"MongoDB connection error: {e}")
    except Exception as e:
        exception_message: str = f"Failed to delete record from collection {collection_name}. Error: {e}"
        logger.exception(exception_message)
        raise Exception(exception_message)