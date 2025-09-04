"""
Convenience functions for Python encoding and decoding operations.
"""

from typing import Optional, Union
from pathlib import Path

from ...core import NeuProcessLogic
from ..base import CodeGenerationResult, CodeDecodingResult
from .config import PythonEncoderConfig, PythonDecoderConfig
from .encoder import PythonEncoder
from .decoder import PythonDecoder


def encode_logic(logic: NeuProcessLogic, config: Optional[PythonEncoderConfig] = None) -> CodeGenerationResult:
    """
    Convenience function to encode a NeuProcessLogic object to Python code.
    
    Args:
        logic: The NeuProcessLogic object to encode
        config: Optional encoder configuration
        
    Returns:
        CodeGenerationResult with generated code and metadata
    """
    encoder_config = config or PythonEncoderConfig()
    encoder = PythonEncoder(config=encoder_config)
    return encoder.encode(logic)


def decode_from_string(code: str, function_name: Optional[str] = None, 
                      config: Optional[PythonDecoderConfig] = None) -> NeuProcessLogic:
    """
    Convenience function to decode Python code string to NeuProcessLogic.
    
    Args:
        code: Python code string
        function_name: Optional function name to extract
        config: Optional decoder configuration
        
    Returns:
        NeuProcessLogic object (legacy compatibility)
    """
    decoder_config = config or PythonDecoderConfig()
    decoder = PythonDecoder(config=decoder_config)
    return decoder.decode_from_string(code, function_name)


def decode_from_file(file_path: Union[str, Path], 
                    function_name: Optional[str] = None,
                    config: Optional[PythonDecoderConfig] = None) -> CodeDecodingResult:
    """
    Convenience function to decode Python file to NeuProcessLogic.
    
    Args:
        file_path: Path to Python file
        function_name: Optional function name to extract
        config: Optional decoder configuration
        
    Returns:
        CodeDecodingResult with decoded logic and metadata
    """
    decoder_config = config or PythonDecoderConfig()
    decoder = PythonDecoder(config=decoder_config)
    return decoder.decode_from_file(file_path, function_name)


def decode_from_callable(func: callable, config: Optional[PythonDecoderConfig] = None) -> CodeDecodingResult:
    """
    Convenience function to decode Python callable to NeuProcessLogic.
    
    Args:
        func: Python callable
        config: Optional decoder configuration
        
    Returns:
        CodeDecodingResult with decoded logic and metadata
    """
    decoder_config = config or PythonDecoderConfig()
    decoder = PythonDecoder(config=decoder_config)
    return decoder.decode_from_callable(func)
