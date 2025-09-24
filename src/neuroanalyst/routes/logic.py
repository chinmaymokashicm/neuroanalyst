"""
NeuroAnalyst Logic Router

This module defines the FastAPI router for the NeuProcessLogic endpoints.
It provides endpoints to encode and decode user-defined functions.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

from ..models.process.logic.core import NeuProcessLogic, NeuProcessKind
from ..models.process.logic.code.python.encoder import PythonEncoder
from ..models.database.mongo_client import MongoDBClient
from ..models.database.collections import CollectionNames
from .dependencies import get_db_client

# Create router
router = APIRouter()


class LogicEncodeRequest(BaseModel):
    """Request model for encoding a user-defined function."""
    function_string: str
    name: Optional[str] = None
    description: Optional[str] = None
    function_type: str = "file"  # or "bulk"


class LogicDecodeRequest(BaseModel):
    """Request model for decoding a pydantic model to a function."""
    model_data: Dict[str, Any]


@router.post("/encode", response_model=Dict[str, Any])
async def encode_logic(request: LogicEncodeRequest):
    """
    Encode a user-defined function into a pydantic model.

    Args:
        request: The request object containing the function string.

    Returns:
        Dict[str, Any]: The pydantic model in the form of a dict.
    """
    try:
        # Determine the function type
        function_type = NeuProcessKind.FILE if request.function_type.lower() == "file" else NeuProcessKind.BULK

        # Create the encoder
        # encoder = PythonEncoder()

        # # Encode the function
        # encoded_function = encoder.encode(request.function_string)

        # # Create the logic model
        # logic = NeuProcessLogic(
        #     name=request.name or "unnamed_function",
        #     description=request.description or "",
        #     kind=function_type,
        #     encoded_function=encoded_function
        # )

        # logic_dict = logic.model_dump()
        
        logic = NeuProcessLogic(
            about={
                "name": request.name or "unnamed_function",
                "description": request.description or "",
                "version": "1.0.0",
                "author": "unknown",
                "tag": ""
            },
            language="python",
            kind=function_type,
            code=request.function_string,
            import_statements=[],
            arguments=[]
        )

        result = {
            "status": "success",
            "message": "Function encoded successfully",
            "model": logic.model_dump()
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decode", response_model=Dict[str, Any])
async def decode_logic(request: LogicDecodeRequest):
    """
    Decode a pydantic model into a user-defined function.
    
    Args:
        request: The request object containing the pydantic model data.
        
    Returns:
        Dict[str, Any]: The function string and metadata.
    """
    try:
        # Create a logic model from the provided data
        logic = NeuProcessLogic(**request.model_data)
        
        # Create the encoder
        encoder = PythonEncoder()
        
        # Decode the function
        function_string = encoder.decode(logic.encoded_function)
        
        result = {
            "status": "success",
            "message": "Function decoded successfully",
            "function": {
                "name": logic.about.name,
                "description": logic.about.description,
                "function_type": logic.kind.value,
                "function_string": function_string
            }
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
