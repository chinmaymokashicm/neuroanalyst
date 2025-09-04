#!/usr/bin/env python
"""
Fix f-strings in bulk template by escaping braces.
"""

import re

def fix_f_strings_in_template():
    """Fix all f-strings in the bulk template."""
    
    template_path = '/Users/cmokashi/Documents/GitHub/neuroanalyst/app/models/process/templates/main_bulk.py.template'
    
    # Read the template
    with open(template_path, 'r') as f:
        content = f.read()
    
    print("🔍 Original content length:", len(content))
    
    # Find all f-string patterns (f"..." or f'...')
    # We need to escape all {} inside f-strings that aren't template variables
    
    # Pattern to find f-strings
    f_string_pattern = r'f"([^"]*)"'
    
    def escape_braces_in_match(match):
        f_string_content = match.group(1)
        # Escape all braces that aren't already escaped
        # But preserve template variables like {process_id}, {function_name}, etc.
        template_vars = [
            'process_name', 'pipeline_name', 'author', 'description', 
            'version', 'process_id', 'created_timestamp', 'encoded_function_code', 
            'function_name'
        ]
        
        # For now, escape all braces - the template vars will be handled separately
        escaped = f_string_content.replace('{', '{{').replace('}', '}}')
        return f'f"{escaped}"'
    
    # Replace all f-strings
    new_content = re.sub(f_string_pattern, escape_braces_in_match, content)
    
    print("🔍 New content length:", len(new_content))
    print("🔍 Changes made:", len(content) != len(new_content))
    
    # Write back
    with open(template_path, 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed f-strings in template")

if __name__ == "__main__":
    fix_f_strings_in_template()
