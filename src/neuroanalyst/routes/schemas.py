"""
API Schema Models

This module contains Pydantic models for request and response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

# Common schemas
class SchedulerType(str, Enum):
    """
    Types of job schedulers supported
    """
    LOCAL = "local"
    LSF = "lsf"
    SLURM = "slurm"
    PBS = "pbs"

class ProcessLogicLevel(str, Enum):
    """
    Levels at which NeuProcessLogic can operate
    """
    FILE = "file"
    BULK = "bulk"

# Response schemas
class BaseResponse(BaseModel):
    """
    Base response model for all API endpoints
    """
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Descriptive message about the operation")
    
class ErrorResponse(BaseModel):
    """
    Error response model
    """
    detail: str = Field(..., description="Error detail message")
    
# Detailed schemas for specific resource types could be added here
# as needed for more complex operations