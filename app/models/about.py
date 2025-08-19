"""
About information supplemented to other objects/classes.
"""

from typing import Optional

from pydantic import BaseModel, Field

class About(BaseModel):
    name: str = Field(..., description="Name of the object")
    description: Optional[str] = Field(None, description="Description of the object")
    version: Optional[str] = Field(None, description="Version of the object")
    tag: Optional[str] = Field(None, description="Tag of the object")