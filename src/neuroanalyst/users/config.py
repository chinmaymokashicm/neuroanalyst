from ..utils.id_generators import generate_id
from ..utils.security import hash_password, generate_api_key, generate_encryption_key, decrypt_message
from .db import SQLiteDB, SQLiteTable

from pydantic import BaseModel, DirectoryPath, Field

class User(BaseModel):
    """
    User configuration settings for NeuroAnalyst. This will be used to store user-specific work in their home directory.
    This can later be extended to include more user preferences.
    """
    _id: str = Field(default_factory=lambda: generate_id("user"), description="Unique identifier for the user configuration")
    name: str = Field(..., description="Name of the user")
    password: str = Field(..., description="Password for the user (hashed)")
    api_key: str = Field(..., description="API key for accessing NeuroAnalyst services")
    encryption_key: bytes = Field(..., description="Encryption key for securing user data")
    
    @classmethod
    def from_user(cls, name: str, password: str) -> "User":
        """Create a UserConfig instance from user name and password."""
        hashed_password = hash_password(password)
        api_key = generate_api_key()
        encryption_key = generate_encryption_key()
        return cls(
            name=name,
            password=hashed_password,
            api_key=api_key,
            encryption_key=encryption_key
        )
    
    def to_db(self):
        db = SQLiteDB()
        db.connect()
        table: SQLiteTable = SQLiteTable(
            name="users",
            column_names=["_id", "name", "password", "api_key", "encryption_key"],
            column_types=["TEXT", "TEXT", "TEXT", "TEXT", "BLOB"],
            primary_keys=["_id"]
        )
        create_sql: str = table.create_table_sql(db.conn)
        db.cursor.execute(create_sql)
        insert_sql: str = table.insert_sql()
        db.cursor.execute(insert_sql, (
            self._id,
            self.name,
            self.password,
            self.api_key,
            self.encryption_key
        ))
        db.conn.commit()
        db.close()

    def decrypt_action_token(self, token: str) -> str:
        """Decrypt an action token using the user's encryption key."""
        return decrypt_message(token, self.encryption_key)