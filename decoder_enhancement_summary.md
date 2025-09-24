# Python Decoder Enhancement Summary

## Issues Fixed

1. **Import Alias Preservation**
   - The Python decoder now correctly preserves import aliases when converting Python functions to NeuProcessLogic objects
   - Both regular imports (`import numpy as np`) and from-imports (`from scipy import stats as st`) are properly handled

2. **Code Formatting Preservation**
   - The original function code formatting is now preserved, including indentation, comments, and multi-line structures
   - This ensures generated code maintains the exact structure of the original functions

## Implementation Details

### Import Alias Handling

We enhanced the `PythonFunctionExtractor` class to properly handle import aliases:

```python
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
```

### Code Formatting Preservation

We improved the `decode_from_string` method to extract and preserve the original function code:

1. Enhanced function extraction from source code
2. Preserved original formatting by extracting the function directly from the source string
3. Added sophisticated code boundary detection to properly handle nested structures

```python
# Extract the original function code from the source
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
```

### Logic Conversion

We updated the `_convert_to_logic` method to use the original function code when available:

```python
# Use original function code if available to preserve formatting
if 'original_code' in func_info:
    clean_code = func_info['original_code']
elif self.config.preserve_original_formatting:
    clean_code = func_info['body']
else:
    # Find the function in the original code to preserve its formatting
    # ...
```

## Testing

A comprehensive test suite was developed to verify that:

1. All types of import aliases are properly preserved
2. The original code formatting is maintained
3. The enhanced decoder works with a wide range of Python code patterns

## Conclusion

These improvements ensure that when Python functions are converted to NeuProcessLogic objects and back to Python code, all import aliases and code formatting are preserved exactly as in the original source code. This is crucial for maintaining the functionality and readability of the generated code.