import os
import string
import datetime
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

def assemble_script(components: List[Dict[str, Union[str, Dict[str, str]]]]) -> str:
    """
    Assemble a shell script from components.
    
    Args:
        components: List of component dictionaries, each with 'template' (path to template file) 
                   and 'context' (variables to substitute)
                   
    Returns:
        The assembled script as a string
    """
    script_parts = []
    
    for component in components:
        template_path = component['template']
        context = component.get('context', {})
        
        # Read the template
        with open(template_path, 'r') as f:
            template_content = f.read()
            
        # Substitute variables
        template = string.Template(template_content)
        content = template.safe_substitute(context)
        
        script_parts.append(content)
    
    return "\n\n".join(script_parts)
