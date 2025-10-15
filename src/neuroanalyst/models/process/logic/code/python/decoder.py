"""
Python decoder for converting Python code to NeuProcessLogic objects.
"""

import ast
import inspect
import re
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

from ...core import NeuProcessLogic, NeuProcessLogicArgument, ProgrammingLanguage
# from ..models.about import About
from .....about import About
from ..base import BaseDecoder
from .config import PythonDecoderConfig


class PythonFunctionExtractor(ast.NodeVisitor):
    """AST visitor to extract function information from Python code."""
    
    def __init__(self):
        self.functions = []
        self.imports = []
        self.current_function = None
        self.has_metrics = False
        self.output_entities = {}
    
    def visit_Import(self, node):
        """Extract import statements."""
        for alias in node.names:
            if alias.asname:
                self.imports.append(f"import {alias.name} as {alias.asname}")
            else:
                self.imports.append(f"import {alias.name}")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Extract from-import statements."""
        module = node.module or ""
        names = []
        for alias in node.names:
            if alias.asname:
                names.append(f"{alias.name} as {alias.asname}")
            else:
                names.append(alias.name)
        self.imports.append(f"from {module} import {', '.join(names)}")
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Extract function definitions and their metadata."""
        # Get source code from the source being parsed
        # This approach uses the node's line number information to preserve the original formatting
        source_lines = None
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            # Get the source code from the root
            try:
                source_lines = ast.unparse(node)  # Default fallback
            except Exception:
                pass  # Will use ast.unparse(node) as fallback
        
        # Analyze function body for metrics and output_entities
        self._analyze_function_body(node)
                
        func_info = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'args': self._extract_arguments(node.args),
            'body': source_lines if source_lines else ast.unparse(node),
            'decorators': [ast.unparse(dec) for dec in node.decorator_list],
            'returns': ast.unparse(node.returns) if node.returns else None,
            'lineno': node.lineno,
            'has_metrics': self.has_metrics,
            'output_entities': self.output_entities
        }
        self.functions.append(func_info)
        self.generic_visit(node)
    
    def _analyze_function_body(self, node):
        """Analyze function body to check for metrics dict and output_entities dict."""
        self.has_metrics = False
        self.output_entities = {}
        
        # Look for variable assignments in the function body
        for stmt in ast.walk(node):
            # Check for assignments
            if isinstance(stmt, ast.Assign):
                # Look for metrics dictionary
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == 'metrics':
                        # Check if it's assigned a dictionary
                        if isinstance(stmt.value, ast.Dict):
                            self.has_metrics = True
                        elif isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'dict':
                            self.has_metrics = True
                    
                    # Look for output_entities dictionary
                    if isinstance(target, ast.Name) and target.id == 'output_entities':
                        if isinstance(stmt.value, ast.Dict):
                            # Extract key-value pairs if it's a literal dictionary
                            self._extract_dict_items(stmt.value)
    
    def _extract_dict_items(self, dict_node):
        """Extract items from a dictionary node."""
        if not isinstance(dict_node, ast.Dict):
            return
        
        # Process each key-value pair
        for key, value in zip(dict_node.keys, dict_node.values):
            # Only extract string keys and string values
            if isinstance(key, ast.Constant) and isinstance(key.value, str) and isinstance(value, ast.Constant) and isinstance(value.value, str):
                self.output_entities[key.value] = value.value
    
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
            tree = ast.parse(code, type_comments=True)
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
            
            # Extract the original function code from the source
            # Find the function in the original code to preserve formatting
            func_name = target_function['name']
            lines = code.split('\n')
            
            func_start = -1
            func_end = len(lines)
            bracket_level = 0
            in_func = False
            
            for i, line in enumerate(lines):
                if not in_func:
                    # Look for function definition
                    if re.match(r'^\s*def\s+' + re.escape(func_name) + r'\s*\(', line):
                        func_start = i
                        in_func = True
                        bracket_level += line.count('(') - line.count(')')
                else:
                    # Count brackets to find end of function definition
                    bracket_level += line.count('(') - line.count(')')
                    
                    # Check for end of function
                    if i + 1 < len(lines) and not lines[i + 1].strip():
                        # Next line is blank
                        next_nonblank = i + 2
                        while next_nonblank < len(lines) and not lines[next_nonblank].strip():
                            next_nonblank += 1
                        
                        if next_nonblank < len(lines) and not lines[next_nonblank].startswith(' '):
                            # Next non-blank line is not indented - end of function
                            func_end = next_nonblank - 1
                            break
            
            if func_start >= 0:
                # Extract the function code with original formatting
                original_func_code = '\n'.join(lines[func_start:func_end+1])
                
                # Update the target function with the original code
                target_function['original_code'] = original_func_code
            
            return self._convert_to_logic(target_function, extractor.imports, original_code=code)
            
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
        
        # Try to parse the source code to extract metrics and output_entities
        is_metrics_available = False
        output_entities = {}
        
        try:
            tree = ast.parse(source)
            extractor = PythonFunctionExtractor()
            extractor.visit(tree)
            
            if extractor.has_metrics:
                is_metrics_available = True
            
            if extractor.output_entities:
                output_entities = extractor.output_entities
        except:
            # If parsing fails, use regex-based detection for metrics
            is_metrics_available = bool(re.search(r'\bmetrics\s*=\s*{', source) or re.search(r'\bmetrics\s*=\s*dict\(', source))
        
        return NeuProcessLogic(
            about=about,
            language=ProgrammingLanguage.PYTHON,
            code=clean_source,
            import_statements=imports,
            arguments=arguments,
            is_metrics_available=is_metrics_available,
            output_entities=output_entities
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
    
    def _convert_to_logic(self, func_info: Dict[str, Any], imports: List[str], original_code: str = None) -> NeuProcessLogic:
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

        # Infer logic kind
        if len(arguments) == 1 and arguments[0].name == "input_filepath":
            logic_kind = "file"
        else:
            logic_kind = "bulk"
        
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
        
        # Use original function code if available to preserve formatting
        if 'original_code' in func_info:
            clean_code = func_info['original_code']
        elif self.config.preserve_original_formatting:
            clean_code = func_info['body']
        else:
            # Find the function in the original code to preserve its formatting
            if original_code and name in original_code:
                lines = original_code.split('\n')
                func_pattern = re.compile(r'^\s*def\s+' + re.escape(name) + r'\s*\(')
                
                # Find function start
                start_idx = -1
                for i, line in enumerate(lines):
                    if func_pattern.match(line):
                        start_idx = i
                        break
                
                if start_idx >= 0:
                    # Extract function definition and body with proper indentation
                    func_lines = []
                    func_lines.append(lines[start_idx])  # Function signature
                    
                    # Add function body with proper indentation
                    i = start_idx + 1
                    while i < len(lines):
                        if not lines[i].strip() and i + 1 < len(lines):
                            # Check if next non-blank line is not indented
                            next_idx = i + 1
                            while next_idx < len(lines) and not lines[next_idx].strip():
                                next_idx += 1
                            if next_idx < len(lines) and not lines[next_idx].startswith(' '):
                                break  # End of function
                        
                        if i >= len(lines) or (i > start_idx + 1 and lines[i].strip() and not lines[i].startswith(' ')):
                            # Unindented line after function start means end of function
                            break
                        
                        func_lines.append(lines[i])
                        i += 1
                    
                    clean_code = '\n'.join(func_lines)
                else:
                    # Fallback to standard import removal
                    clean_code = self._remove_imports_from_function_body(func_info['body'])
            else:
                # Fallback to standard import removal
                clean_code = self._remove_imports_from_function_body(func_info['body'])
        
        # Get metrics and output_entities info
        is_metrics_available = func_info.get('has_metrics', False)
        output_entities = func_info.get('output_entities', {})
        
        return NeuProcessLogic(
            about=about,
            language=ProgrammingLanguage.PYTHON,
            code=clean_code,
            import_statements=imports,
            arguments=arguments,
            logic_kind=logic_kind,
            is_metrics_available=is_metrics_available,
            output_entities=output_entities
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
        
        # For fallback mode, try to detect metrics and output_entities with regex
        is_metrics_available = bool(re.search(r'\bmetrics\s*=\s*{', code) or re.search(r'\bmetrics\s*=\s*dict\(', code))
        
        # For output_entities, we can't reliably extract key-value pairs with regex in fallback mode
        
        return NeuProcessLogic(
            about=about,
            language=ProgrammingLanguage.PYTHON,
            code=code,  # Keep original code as-is
            import_statements=[],  # Cannot reliably extract imports with regex
            arguments=[],  # Cannot reliably extract arguments with regex
            is_metrics_available=is_metrics_available,
            output_entities={}  # Empty dict for fallback mode
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
            import_pattern = r'^(import\s+.+|from\s+.+\s+import\s+.+)$'
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
        # If the function already starts with 'def', just return it as is
        if function_code.strip().startswith('def '):
            return function_code
            
        try:
            # Parse the function to extract its structure
            tree = ast.parse(function_code)
            
            # Find the function definition node
            function_node = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_node = node
                    break
            
            if not function_node:
                return function_code  # No function found, return original code
                
            # Get the function's name and line numbers
            func_name = function_node.name
            start_line = function_node.lineno
            end_line = function_node.end_lineno if hasattr(function_node, 'end_lineno') else None
            
            # Split the code into lines
            lines = function_code.split('\n')
            
            # Find the function definition line
            def_line_idx = -1
            for i, line in enumerate(lines):
                if f"def {func_name}" in line and ":" in line:
                    def_line_idx = i
                    break
                    
            if def_line_idx == -1:
                return function_code  # Function definition not found
                
            # Extract the function body, preserving all formatting
            function_lines = lines[def_line_idx:]
            
            # Filter out import statements from the function body while preserving structure
            filtered_lines = [function_lines[0]]  # Keep function signature
            
            # Process the body, keeping all lines except imports
            in_body = False
            for i in range(1, len(function_lines)):
                line = function_lines[i]
                stripped = line.strip()
                
                # Once we see indented code, we're in the body
                if not in_body and stripped:
                    in_body = True
                
                # Skip import statements in the body but keep everything else including blank lines
                if not in_body or not (stripped.startswith('import ') or 
                                      (stripped.startswith('from ') and ' import ' in stripped)):
                    filtered_lines.append(line)
            
            return '\n'.join(filtered_lines)
        except SyntaxError:
            # If parsing fails, return the original code
            return function_code
