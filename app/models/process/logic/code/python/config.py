"""
Configuration classes for Python encoder and decoder with enhanced Pydantic validation.
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Self
from ..base import BaseEncoderConfig, BaseDecoderConfig


class PythonEncoderConfig(BaseEncoderConfig):
    """Configuration for Python encoder with enhanced validation."""
    
    model_config = ConfigDict(
        extra='forbid',
        validate_assignment=True,
        str_strip_whitespace=True  # Automatically strip whitespace from strings
    )
    
    include_type_hints: bool = Field(
        default=True, 
        description="Whether to include type hints in function signature"
    )
    docstring_style: str = Field(
        default="google",
        description="Docstring style to use (google, numpy, sphinx)"
    )
    indent_size: int = Field(
        default=4, 
        ge=1,
        le=8,
        description="Number of spaces for indentation (1-8)"
    )
    max_line_length: int = Field(
        default=88, 
        ge=50,
        le=200,
        description="Maximum line length for code formatting (50-200)"
    )
    use_black_style: bool = Field(
        default=True, 
        description="Whether to use Black code formatting style"
    )
    include_imports_in_docstring: bool = Field(
        default=True, 
        description="Whether to document required imports in docstring"
    )
    include_metadata_in_docstring: bool = Field(
        default=True,
        description="Whether to include metadata (version, language) in docstring"
    )
    
    @field_validator("docstring_style")
    @classmethod
    def validate_docstring_style(cls, v):
        allowed_styles = {"google", "numpy", "sphinx", "epytext"}
    # Removed explicit validators for indent_size and max_line_length; constraints are now handled by Field.
    def validate_max_line_length(cls, v):
        if v < 50 or v > 200:
            raise ValueError("Max line length must be between 50 and 200")
        return v
    
    @model_validator(mode='after')
    def validate_black_style_consistency(self) -> Self:
        """Ensure Black style settings are consistent."""
        if self.use_black_style and self.max_line_length != 88:
            # Black uses 88 characters by default
            self.max_line_length = 88
        return self


class PythonDecoderConfig(BaseDecoderConfig):
    """Configuration for Python decoder with enhanced validation."""
    
    model_config = ConfigDict(
        extra='forbid',
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    preserve_original_formatting: bool = Field(
        default=False, 
        description="Whether to preserve original code formatting"
    )
    default_argument_description: str = Field(
        default="Parameter {name}", 
        description="Default description template for arguments"
    )
    extract_type_hints: bool = Field(
        default=True, 
        description="Whether to extract type hints from function signatures"
    )
    extract_imports: bool = Field(
        default=True, 
        description="Whether to extract import statements"
    )
    fallback_on_syntax_error: bool = Field(
        default=True, 
        description="Whether to use regex fallback on syntax errors"
    )
    min_function_lines: int = Field(
        default=1,
        ge=0,
        description="Minimum number of lines for a valid function"
    )
    max_function_lines: int = Field(
        default=1000,
        ge=1,
        description="Maximum number of lines for a function to process"
    )
    
    @field_validator("default_argument_description")
    @classmethod
    def validate_default_description(cls, v):
        if "{name}" not in v:
            raise ValueError("Default argument description must contain '{name}' placeholder")
        return v
    
    @model_validator(mode='after')
    def validate_function_line_limits(self) -> Self:
        """Ensure max function lines is greater than min function lines."""
        if self.max_function_lines <= self.min_function_lines:
            raise ValueError("max_function_lines must be greater than min_function_lines")
        return self
