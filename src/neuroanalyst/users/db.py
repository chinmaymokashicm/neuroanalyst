from ..utils.constants import PATHS

from typing import Optional
from pathlib import Path
import sqlite3

from pydantic import BaseModel, Field, model_validator

USER_DB_PATH = Path("~/.neuroanalyst/user_db.sqlite3").expanduser()

class SQLiteTable(BaseModel):
    name: str = Field(..., description="Name of the database table")
    column_names: list[str] = Field(..., description="Columns and their types for the table")
    column_types: list[str] = Field(..., description="Data types for each column")
    primary_keys: list[str] = Field(..., description="List of primary key columns")
    
    @model_validator(mode="before")
    @classmethod
    def validate_columns(cls, values):
        # Check if primary keys are in columns
        cols = values.get("column_names", [])
        pks = values.get("primary_keys", [])
        for pk in pks:
            if pk not in cols:
                raise ValueError(f"Primary key '{pk}' not found in column names.")
        return values

    def create_table_sql(self, conn: sqlite3.Connection) -> str:
        cols_with_types = ", ".join([f"{col} {dtype}" for col, dtype in self.columns.items()])
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.name} (
            {cols_with_types},
            PRIMARY KEY ({", ".join(self.primary_keys)})
        )
        """
        return sql
    
    def insert_sql(self) -> str:
        placeholders = ", ".join(["?" for _ in self.column_names])
        sql = f"""
        INSERT INTO {self.name} ({", ".join(self.column_names)})
        VALUES ({placeholders})
        """
        return sql

class SQLiteDB(BaseModel):
    db_name: str = Field(default=str(USER_DB_PATH), description="Path to the user database file")
    conn: Optional[sqlite3.Connection] = Field(description="SQLite database connection", default=None)
    cursor: Optional[sqlite3.Cursor] = Field(description="SQLite database cursor", default=None)
    
    class Config:
        arbitrary_types_allowed = True

    def connect(self):
        """Establish a connection to the SQLite database."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()