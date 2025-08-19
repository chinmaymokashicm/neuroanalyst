"""
Python encoder for converting NeuProcessLogic objects to Python code with enhanced Pydantic integration.
"""

import ast
import time
from typing import List

from ...core import NeuProcessLogic, NeuProcessLogicArgument, ProgrammingLanguage
from ..base import BaseEncoder, CodeGenerationResult
from .config import PythonEncoderConfig


class PythonEncoder(BaseEncoder):
    """Encodes NeuProcessLogic objects into Python functions with enhanced validation."""
    
    def __init__(self, config: PythonEncoderConfig = None):
        encoder_config = config or PythonEncoderConfig()
        super().__init__(language=ProgrammingLanguage.PYTHON, config=encoder_config)
    
    def encode(self, logic: NeuProcessLogic) -> CodeGenerationResult:
        """
        Encode a NeuProcessLogic object into Python code.
        
        Args:
            logic: The NeuProcessLogic object to encode
            
        Returns:
            CodeGenerationResult with generated code and metadata
        """
        start_time = time.time()
        
        # Validate input
        is_valid, errors = self.validate_logic(logic)
        if not is_valid:
            result = CodeGenerationResult(
                code="# Invalid logic - could not encode",
                language=ProgrammingLanguage.PYTHON,
                validation_errors=errors
            )
            result.generation_time = time.time() - start_time
            return result
        
        try:
            # Generate function signature
            signature = self._generate_signature(logic.arguments)
            
            # Generate function body
            body = self._format_code_body(logic.code)
            
            # Use provided import statements
            imports = logic.import_statements or []
            
            # Generate docstring if enabled
            docstring = ""
            if self.config.include_docstring:
                docstring = self._generate_docstring(logic)
            
            # Combine all parts
            function_parts = []
            
            # Add imports first
            if imports:
                function_parts.extend(imports)
                function_parts.append("")  # Empty line after imports
            
            # Add function definition
            function_parts.append(f"def {logic.about.name}{signature}:")
            
            # Add docstring if present
            if docstring:
                function_parts.append(docstring)
            
            # Add function body
            function_parts.append(body)
            
            generated_code = "\n".join(function_parts)
            
            # Validate generated code if enabled
            validation_errors = []
            if self.config.validate_output:
                try:
                    ast.parse(generated_code)
                except SyntaxError as e:
                    validation_errors.append(f"Generated code has syntax error: {str(e)}")
            
            result = CodeGenerationResult(
                code=generated_code,
                language=ProgrammingLanguage.PYTHON,
                imports=imports,
                metadata={
                    'function_name': logic.about.name,
                    'argument_count': len(logic.arguments),
                    'has_docstring': bool(docstring),
                    'encoding_config': self.config.model_dump()
                },
                validation_errors=validation_errors
            )
            result.generation_time = time.time() - start_time
            return result
            
        except Exception as e:
            result = CodeGenerationResult(
                code=f"# Error during encoding: {str(e)}",
                language=ProgrammingLanguage.PYTHON,
                validation_errors=[f"Encoding failed: {str(e)}"]
            )
            result.generation_time = time.time() - start_time
            return result
    
    def _generate_signature(self, arguments: List[NeuProcessLogicArgument]) -> str:
        """Generate function signature from arguments."""
        if not self.config.include_type_hints:
            # Generate signature without type hints
            sig_parts = []
            required_args = [arg for arg in arguments if not arg.is_optional]
            optional_args = [arg for arg in arguments if arg.is_optional]
            
            # Add required arguments first
            for arg in required_args:
                sig_parts.append(arg.name)
            
            # Add optional arguments with defaults
            for arg in optional_args:
                sig_parts.append(f"{arg.name}=None")
            
            return f"({', '.join(sig_parts)})"
        else:
            # Generate signature with type hints
            sig_parts = []
            required_args = [arg for arg in arguments if not arg.is_optional]
            optional_args = [arg for arg in arguments if arg.is_optional]
            
            # Add required arguments with type hints
            for arg in required_args:
                sig_parts.append(f"{arg.name}: {arg.type}")
            
            # Add optional arguments with type hints and defaults
            for arg in optional_args:
                sig_parts.append(f"{arg.name}: {arg.type} = None")
            
            return f"({', '.join(sig_parts)})"
    
    def _format_code_body(self, code: str) -> str:
        """Format the function body with proper indentation."""
        if not code.strip():
            return "    pass"
        
        # Split into lines and ensure proper indentation
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():  # Non-empty line
                # Ensure proper indentation (4 spaces by default)
                if not line.startswith(' ' * self.config.indent_size):
                    # Add indentation if not present
                    formatted_lines.append(' ' * self.config.indent_size + line.lstrip())
                else:
                    formatted_lines.append(line)
            else:
                # Keep empty lines
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _generate_docstring(self, logic: NeuProcessLogic) -> str:
        """Generate docstring for the function."""
        if not self.config.include_docstring:
            return ""
        
        docstring_parts = []
        
        # Add the main description
        description = logic.about.description or f"Function {logic.about.name}"
        docstring_parts.append(f'    """\n    {description}')
        
        # Add arguments section if there are arguments
        if logic.arguments:
            docstring_parts.append("\n    Args:")
            for arg in logic.arguments:
                arg_desc = arg.description or f"Parameter {arg.name}"
                type_info = f" ({arg.type})" if self.config.include_type_hints else ""
                docstring_parts.append(f"        {arg.name}{type_info}: {arg_desc}")
        
        # Add imports section if enabled and imports exist
        if self.config.include_imports_in_docstring and logic.import_statements:
            docstring_parts.append("\n    Required imports:")
            for import_stmt in logic.import_statements:
                docstring_parts.append(f"        {import_stmt}")
        
        # Add metadata section if enabled
        if self.config.include_metadata_in_docstring:
            docstring_parts.append("\n    Metadata:")
            docstring_parts.append(f"        Version: {logic.about.version or '1.0.0'}")
            docstring_parts.append(f"        Language: {logic.language.value}")
        
        docstring_parts.append('    """')
        return '\n'.join(docstring_parts)
