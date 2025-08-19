"""
Python decoder for converting Python code to NeuProcessLogic objects.
"""

import ast
import inspect
import re
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

from ...core import NeuProcessLogic, NeuProcessLogicArgument, ProgrammingLanguage
from app.models.about import About
from ..base import BaseDecoder
from .config import PythonDecoderConfig


class PythonFunctionExtractor(ast.NodeVisitor):
    """AST visitor to extract function information from Python code."""
    
    def __init__(self):
        self.functions = []
        self.imports = []
        self.current_function = None
    
    def visit_Import(self, node):
        """Extract import statements."""
        for alias in node.names:
            self.imports.append(f"import {alias.name}")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Extract from-import statements."""
        module = node.module or ""
        names = [alias.name for alias in node.names]
        self.imports.append(f"from {module} import {', '.join(names)}")
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Extract function definitions and their metadata."""
        func_info = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'args': self._extract_arguments(node.args),
            'body': ast.unparse(node),
            'decorators': [ast.unparse(dec) for dec in node.decorator_list],
            'returns': ast.unparse(node.returns) if node.returns else None,
            'lineno': node.lineno
        }
        self.functions.append(func_info)
        self.generic_visit(node)
    
    def _extract_arguments(self, args_node):
        """Extract function arguments with types and defaults."""
        arguments = []
        
        # Regular arguments
        for i, arg in enumerate(args_node.args):
            arg_info = {
                'name': arg.arg,
                'type': ast.unparse(arg.annotation) if arg.annotation else 'Any',
                'is_optional': False,
                'default': None
            }
            
            # Check if there's a default value
            defaults_start = len(args_node.args) - len(args_node.defaults)
            if i >= defaults_start:
                default_idx = i - defaults_start
                arg_info['default'] = ast.unparse(args_node.defaults[default_idx])
                arg_info['is_optional'] = True
            
            arguments.append(arg_info)
        
        # Keyword-only arguments
        for i, arg in enumerate(args_node.kwonlyargs):
            arg_info = {
                'name': arg.arg,
                'type': ast.unparse(arg.annotation) if arg.annotation else 'Any',
                'is_optional': True,
                'default': ast.unparse(args_node.kw_defaults[i]) if args_node.kw_defaults[i] else None
            }
            arguments.append(arg_info)
        
        return arguments


class PythonDecoder(BaseDecoder):
    """Decodes Python functions back into NeuProcessLogic objects."""
    
    def __init__(self, config: PythonDecoderConfig = None):
        decoder_config = config or PythonDecoderConfig()
        super().__init__(language=ProgrammingLanguage.PYTHON, config=decoder_config)
    
    def decode_from_string(self, code: str, function_name: Optional[str] = None) -> NeuProcessLogic:
        """
        Decode Python code string into a NeuProcessLogic object.
        
        Args:
            code: Python code containing the function
            function_name: Specific function name to extract (if multiple functions exist)
            
        Returns:
            NeuProcessLogic object
            
        Raises:
            ValueError: If code is invalid or no functions found
        """
        if not self.validate_code(code):
            if self.config.fallback_on_syntax_error:
                return self._fallback_decode(code, function_name)
            else:
                raise ValueError("Invalid Python code")
        
        try:
            tree = ast.parse(code)
            extractor = PythonFunctionExtractor()
            extractor.visit(tree)
            
            if not extractor.functions:
                raise ValueError("No functions found in the provided code")
            
            # Select function to decode
            target_function = None
            if function_name:
                target_function = next(
                    (f for f in extractor.functions if f['name'] == function_name), 
                    None
                )
                if not target_function:
                    raise ValueError(f"Function '{function_name}' not found")
            else:
                target_function = extractor.functions[0]  # Use first function
            
            return self._convert_to_logic(target_function, extractor.imports)
            
        except SyntaxError as e:
            if self.config.strict_parsing:
                raise ValueError(f"Invalid Python syntax: {e}")
            else:
                # Try to extract what we can with regex fallback
                return self._fallback_decode(code, function_name)
    
    def decode_from_file(self, file_path: Union[str, Path], 
                        function_name: Optional[str] = None) -> NeuProcessLogic:
        """
        Decode Python function from file into a NeuProcessLogic object.
        
        Args:
            file_path: Path to the Python file
            function_name: Specific function name to extract
            
        Returns:
            NeuProcessLogic object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        return self.decode_from_string(code, function_name)
    
    def decode_from_callable(self, func: callable) -> NeuProcessLogic:
        """
        Decode a Python callable into a NeuProcessLogic object.
        
        Args:
            func: Python function object
            
        Returns:
            NeuProcessLogic object
            
        Raises:
            ValueError: If source code cannot be retrieved
        """
        # Get source code
        try:
            source = inspect.getsource(func)
        except OSError:
            raise ValueError("Cannot retrieve source code for the function")
        
        # Extract imports from the source if enabled
        imports = []
        if self.config.extract_imports:
            imports = self._extract_imports_from_code(source)
        
        # Get function metadata
        sig = inspect.signature(func)
        
        # Convert to NeuProcessLogic
        arguments = []
        for param_name, param in sig.parameters.items():
            arg_type = "Any"
            if self.config.extract_type_hints and param.annotation != inspect.Parameter.empty:
                arg_type = str(param.annotation)
                # Clean up type annotation strings
                arg_type = arg_type.replace("<class '", "").replace("'>", "")
            
            is_optional = param.default != inspect.Parameter.empty
            description = self.config.default_argument_description.format(name=param_name)
            
            arguments.append(NeuProcessLogicArgument(
                name=param_name,
                type=arg_type,
                is_optional=is_optional,
                description=description
            ))
        
        # Create About object
        about = About(
            name=func.__name__,
            description=func.__doc__ or f"Function {func.__name__}",
            version="1.0.0"
        )
        
        # Remove imports from the function body since we store them separately
        if self.config.preserve_original_formatting:
            clean_source = source
        else:
            clean_source = self._remove_imports_from_code(source)
        
        return NeuProcessLogic(
            about=about,
            language=ProgrammingLanguage.PYTHON,
            code=clean_source,
            import_statements=imports,
            arguments=arguments
        )
    
    def validate_code(self, code: str) -> bool:
        """
        Validate that the code can be decoded.
        
        Args:
            code: Source code to validate
            
        Returns:
            True if the code can be decoded, False otherwise
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    def _convert_to_logic(self, func_info: Dict[str, Any], imports: List[str]) -> NeuProcessLogic:
        """Convert extracted function info to NeuProcessLogic object."""
        # Create arguments
        arguments = []
        for arg_info in func_info['args']:
            description = self.config.default_argument_description.format(name=arg_info['name'])
            arguments.append(NeuProcessLogicArgument(
                name=arg_info['name'],
                type=arg_info['type'],
                is_optional=arg_info['is_optional'],
                description=description
            ))
        
        # Parse metadata from docstring if available and enabled
        name = func_info['name']
        description = func_info['docstring'] or f"Function {name}"
        version = "1.0.0"  # Default version
        
        # Try to extract metadata from docstring if enabled
        if self.config.extract_metadata and func_info['docstring']:
            version_match = re.search(r'Version:\s*([^\n]+)', func_info['docstring'])
            if version_match:
                version = version_match.group(1).strip()
        
        # Create About object
        about = About(
            name=name,
            description=description,
            version=version
        )
        
        # Remove imports from function body since we store them separately
        if self.config.preserve_original_formatting:
            clean_code = func_info['body']
        else:
            clean_code = self._remove_imports_from_function_body(func_info['body'])
        
        return NeuProcessLogic(
            about=about,
            language=ProgrammingLanguage.PYTHON,
            code=clean_code,
            import_statements=imports,
            arguments=arguments
        )
    
    def _fallback_decode(self, code: str, function_name: Optional[str] = None) -> NeuProcessLogic:
        """
        Fallback decoder using regex when AST parsing fails.
        
        Args:
            code: Python code string
            function_name: Optional function name to extract
            
        Returns:
            NeuProcessLogic object with basic information
        """
        # Extract function definition with regex
        func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
        matches = re.findall(func_pattern, code)
        
        if not matches:
            raise ValueError("No function definitions found in code")
        
        target_name = function_name if function_name else matches[0]
        if target_name not in matches:
            raise ValueError(f"Function '{function_name}' not found")
        
        # Create minimal NeuProcessLogic object
        about = About(
            name=target_name,
            description=f"Function {target_name} (parsed with fallback method)",
            version="1.0.0"
        )
        
        return NeuProcessLogic(
            about=about,
            language=ProgrammingLanguage.PYTHON,
            code=code,  # Keep original code as-is
            import_statements=[],  # Cannot reliably extract imports with regex
            arguments=[]  # Cannot reliably extract arguments with regex
        )
    
    def _extract_imports_from_code(self, code: str) -> List[str]:
        """Extract import statements from the code."""
        try:
            tree = ast.parse(code)
            extractor = PythonFunctionExtractor()
            extractor.visit(tree)
            return extractor.imports
        except SyntaxError:
            # If code can't be parsed, try to extract imports with regex
            import_pattern = r'^(import\s+\S+|from\s+\S+\s+import\s+.+)$'
            imports = []
            for line in code.split('\n'):
                line = line.strip()
                if re.match(import_pattern, line):
                    imports.append(line)
            return imports
    
    def _remove_imports_from_code(self, code: str) -> str:
        """Remove import statements from code, keeping only the function definition."""
        try:
            tree = ast.parse(code)
            # Find function definitions and extract only those
            functions = []
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    functions.append(ast.unparse(node))
            
            if functions:
                return functions[0]  # Return the first function
            else:
                # If no function found, return original code without imports
                lines = code.split('\n')
                non_import_lines = []
                for line in lines:
                    stripped = line.strip()
                    if not (stripped.startswith('import ') or stripped.startswith('from ')):
                        non_import_lines.append(line)
                return '\n'.join(non_import_lines)
        except SyntaxError:
            # Fallback to regex-based removal
            lines = code.split('\n')
            non_import_lines = []
            for line in lines:
                stripped = line.strip()
                if not (stripped.startswith('import ') or stripped.startswith('from ')):
                    non_import_lines.append(line)
            return '\n'.join(non_import_lines)
    
    def _remove_imports_from_function_body(self, function_code: str) -> str:
        """Remove import statements from a function body, keeping only the function logic."""
        try:
            # Parse the function
            tree = ast.parse(function_code)
            if tree.body and isinstance(tree.body[0], ast.FunctionDef):
                func_node = tree.body[0]
                
                # Extract only the function body (without imports at module level)
                func_body_lines = []
                for stmt in func_node.body:
                    if not (isinstance(stmt, ast.Import) or isinstance(stmt, ast.ImportFrom)):
                        func_body_lines.append(ast.unparse(stmt))
                
                # Reconstruct the function without imports
                signature_line = f"def {func_node.name}({', '.join([ast.unparse(arg) for arg in func_node.args.args])}):"
                if func_node.returns:
                    signature_line = signature_line.replace("):", f") -> {ast.unparse(func_node.returns)}:")
                
                # Add docstring if present
                body_parts = []
                if func_node.body and isinstance(func_node.body[0], ast.Expr) and isinstance(func_node.body[0].value, ast.Constant):
                    # Has docstring
                    docstring = func_node.body[0].value.value
                    body_parts.append(f'    """{docstring}"""')
                    # Get statements after docstring
                    for stmt in func_node.body[1:]:
                        if not (isinstance(stmt, ast.Import) or isinstance(stmt, ast.ImportFrom)):
                            body_parts.append(f"    {ast.unparse(stmt)}")
                else:
                    # No docstring, process all statements
                    for stmt in func_node.body:
                        if not (isinstance(stmt, ast.Import) or isinstance(stmt, ast.ImportFrom)):
                            body_parts.append(f"    {ast.unparse(stmt)}")
                
                if not body_parts:
                    body_parts.append("    pass")
                
                return signature_line + "\n" + "\n".join(body_parts)
            else:
                return function_code
        except SyntaxError:
            return function_code
