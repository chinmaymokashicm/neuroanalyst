"""
Code encoders and decoders for different programming languages.

This package provides functionality to encode NeuProcessLogic objects into
executable code in various programming languages, and decode existing code
back into NeuProcessLogic objects.

Currently supported languages:
- Python

Example usage:
    >>> from .python import encode_logic, decode_from_string
    >>> 
    >>> # Encode a NeuProcessLogic object to Python code
    >>> python_code = encode_logic(my_logic)
    >>> 
    >>> # Decode Python code back to NeuProcessLogic
    >>> logic = decode_from_string(python_code)
"""

from .python import (
    PythonEncoder,
    PythonDecoder,
    PythonEncoderConfig,
    PythonDecoderConfig,
    encode_logic,
    decode_from_string,
    decode_from_file,
    decode_from_callable
)

__all__ = [
    'PythonEncoder',
    'PythonDecoder',
    'PythonEncoderConfig',
    'PythonDecoderConfig',
    'encode_logic', 
    'decode_from_string',
    'decode_from_file',
    'decode_from_callable'
]
