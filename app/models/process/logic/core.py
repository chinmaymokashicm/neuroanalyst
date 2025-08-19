"""
Module working with NeuProcessLogic.

Purpose-
- To create a structure around a piece of code that can then be wrapped around by a NeuProcess structure.
- The NeuProcess can then be wrapped around by NeuProcessExec which would be used in NeuPipeline.
"""
from ...about import About

from enum import Enum

from pydantic import BaseModel, Field, field_validator

# =======================Default Logic=======================

DEFAULT_ARGS_DICT: list[dict] = [
    {
        "name": "input_filepath",
        "type": "str | PosixPath",
        "description": "Path to the input file"
    },
    {
        "name": "layout",
        "type": "BIDSLayout",
        "description": "BIDSLayout object of the dataset"
    },
    {
        "name": "pipeline_name",
        "type": "str",
        "description": "Name of the pipeline"
    },
    {
        "name": "overwrite",
        "type": "bool",
        "description": "Whether to overwrite existing files"
    },
    {
        "name": "process_id",
        "type": "str",
        "is_optional": True,
        "description": "ID of the NeuProcess"
    },
    {
        "name": "process_exec_id",
        "type": "str",
        "is_optional": True,
        "description": "ID of the NeuProcessExec"
    },
    {
        "name": "pipeline_id",
        "type": "str",
        "is_optional": True,
        "description": "ID of the NeuPipeline"
    }
]

# ==================================================

class ProgrammingLanguage(str, Enum):
    PYTHON = "python"
    MATLAB = "matlab"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    C_SHARP = "csharp"
    RUBY = "ruby"

class NeuProcessLogicArgument(BaseModel):
    name: str = Field(..., description="Name of the argument")
    type: str = Field(..., description="Type of the argument")
    is_optional: bool = Field(False, description="Whether the argument is optional")
    description: str = Field(..., description="Description of the argument")

class NeuProcessLogic(BaseModel):
    about: About = Field(..., description="About the process logic")
    language: ProgrammingLanguage = Field(default=ProgrammingLanguage.PYTHON, description="Programming language used in the process logic")
    code: str = Field(..., description="Code for the process logic")
    import_statements: list[str] = Field(
        default_factory=list, description="List of import statements required for the process logic"
    )
    arguments: list[NeuProcessLogicArgument] = Field(
        default_factory=list, description="List of arguments for the process logic"
    )

    @field_validator("arguments")
    def validate_arguments(cls, v):
        # Set default arguments if empty list
        if not v:
            v = [NeuProcessLogicArgument(**arg) for arg in DEFAULT_ARGS_DICT]
        return v