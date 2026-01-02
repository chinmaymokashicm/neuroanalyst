"""
Logic Routes

This module contains the API endpoints for NeuProcessLogic operations.
"""
from ..models import (
    NeuProcessLogic,
    PythonEncoder,
    PythonDecoder,
    CodeGenerationResult,
    About
)
from ..utils.constants import NeuroAnalystPaths

from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# Router definition
router = APIRouter(
    prefix="/logic",
    tags=["logic"],
)

# Pydantic models for request/response validation
class ProcessLogicRequest(BaseModel):
    """
    Request model for creating a NeuProcessLogic
    """
    logic: NeuProcessLogic | dict = Field(..., description="NeuProcessLogic object or dict to create")
    register_logic: bool = Field(True, description="Whether to register the logic in the system", alias="register")
    overwrite: bool = Field(False, description="Whether to overwrite existing logic with the same name if registering")
    
class ProcessLogicEncodeRequest(BaseModel):
    """
    Request model for encoding a NeuProcessLogic function
    """
    logic: NeuProcessLogic | dict = Field(..., description="NeuProcessLogic object or dict to encode")
    
class ProcessLogicDecodeRequest(BaseModel):
    """
    Request model for decoding a string of code
    """
    function_string: str = Field(..., description="Encoded function string to decode")
    language: str = Field("python", description="Programming language of the function")
    
class ProcessLogicRegisterRequest(BaseModel):
    """
    Request model for registering a NeuProcessLogic from existing code
    """
    logic: NeuProcessLogic | dict = Field(..., description="NeuProcessLogic object or dict to register")
    overwrite: bool = Field(False, description="Whether to overwrite existing logic with the same name")

class LogicResponse(BaseModel):
    """
    Response model for Logic operations
    """
    id: str = Field(..., description="ID of the created resource")
    name: str = Field(..., description="Name of the resource")
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Descriptive message about the operation")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data if applicable")

@router.post("/", response_model=LogicResponse, status_code=status.HTTP_201_CREATED)
async def create_process_logic(request: ProcessLogicRequest):
    """
    Create a new NeuProcessLogic and register it in the system if specified.
    """
    try:
        logic: NeuProcessLogic = NeuProcessLogic.model_validate(request.logic) if isinstance(request.logic, dict) else request.logic
        
        if request.register_logic:
            logic.register(overwrite=request.overwrite)
            
        return {
            "id": logic.about.name,
            "name": logic.about.name,
            "status": "created",
            "message": f"NeuProcessLogic '{logic.about.name}' created successfully",
            "data": {
                "level": logic.kind, "function_name": logic.about.name, "description": logic.about.description
                }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create NeuProcessLogic: {str(e)}"
        )

@router.post("/encode", response_model=CodeGenerationResult)
async def encode_process_logic(request: ProcessLogicEncodeRequest):
    """
    Encode a NeuProcessLogic object to a string format.
    
    This endpoint takes a Python function code, validates it, and encodes it in the specified format.
    Encoding preserves the function's logic for later use in a NeuProcessDir.
    """
    try:
        encoder: PythonEncoder = PythonEncoder()
        if isinstance(request.logic, dict):
            logic = NeuProcessLogic.model_validate(request.logic)
        else:
            logic = request.logic
        result: CodeGenerationResult = encoder.encode(logic)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to encode function: {str(e)}"
        )

@router.post("/decode", response_model=NeuProcessLogic)
async def decode_process_logic(request: ProcessLogicDecodeRequest):
    """
    Decode a string of code into a NeuProcessLogic object.
    
    This endpoint takes an encoded function string and decodes it back into Python function code.
    """
    try:
        decoder: PythonDecoder = PythonDecoder()
        logic: NeuProcessLogic = decoder.decode_from_string(request.function_string)
        return logic
    except Exception as e:
        print(f"Error decoding function: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decode function: {str(e)}"
        )

@router.get("/{logic_name}", response_model=NeuProcessLogic)
async def get_process_logic(logic_name: str):
    """
    Get information about a specific NeuProcessLogic.
    """
    try:
        logic: NeuProcessLogic = NeuProcessLogic.from_func_name(logic_name)
        return logic
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process logic {logic_name} not found: {str(e)}"
        )

@router.get("/", response_model=List[NeuProcessLogic])
async def list_process_logic(username: Optional[str] = None):
    """
    List all available NeuProcessLogic functions.
    """
    try:
       neuroanalyst_paths = NeuroAnalystPaths()
       logic_dir: Path = Path(neuroanalyst_paths.functions)
       logic_name: list[str] = [subdir.name for subdir in logic_dir.iterdir() if subdir.is_dir()]
       return [NeuProcessLogic.from_func_name(name) for name in logic_name]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list process logic: {str(e)}"
        )
        
@router.delete("/{logic_name}", response_model=LogicResponse)
async def delete_process_logic(logic_name: str):
    """
    Delete a specific NeuProcessLogic from the system.
    """
    try:
        logic: NeuProcessLogic = NeuProcessLogic.from_func_name(logic_name)
        logic.delete()
        return {
            "id": logic_name,
            "name": logic_name,
            "status": "deleted",
            "message": f"NeuProcessLogic '{logic_name}' deleted successfully",
            "data": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete NeuProcessLogic {logic_name}: {str(e)}"
        )