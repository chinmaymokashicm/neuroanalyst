"""
Generic ID generation utilities for NeuroAnalyst.
"""
from .constants import NeuroAnalystPaths

import random, os
from pathlib import Path
from typing import Set, Dict, Optional, Literal


def generate_id(prefix: Optional[str] = None) -> str:
    """
    Generate a unique ID for the specified type.
    
    Args:
        prefix: Prefix for the ID to generate (e.g., "PR", "PE", "PL")
        
    Returns:
        str: Generated ID (e.g., "PR-123456", "PE-789012")
        
    Raises:
        ValueError: If id_type is not recognized
    """
    digits: int = 6
    
    # Generate random number with specified digits
    min_val = 10 ** (digits - 1)
    max_val = (10 ** digits) - 1
    number = random.randint(min_val, max_val)
    
    return f"{prefix}-{number}" if prefix else str(number)

def generate_unique_id(kind: Literal["process", "process_exec", "pipeline", "user"], max_attempts: int = 1000) -> str:
    """
    Generate a unique ID that doesn't conflict with existing IDs.
    
    Args:
        kind: Type of ID to generate ("process", "process_exec", "pipeline", or "user")
        max_attempts: Maximum number of generation attempts
        
    Returns:
        str: Unique ID
        
    Raises:
        RuntimeError: If unable to generate unique ID after max_attempts
    """
    # Get working directory for existing IDs
    if kind == "process":
        working_dir: Path = NeuroAnalystPaths().workdir
        prefix: Optional[str] = "PR"
    elif kind == "process_exec":
        working_dir: Path = NeuroAnalystPaths().process_execs
        prefix: Optional[str] = "PE"
    elif kind == "pipeline":
        working_dir: Path = NeuroAnalystPaths().pipelines
        prefix: Optional[str] = "PL"
    elif kind == "user":
        working_dir: Path = Path(os.getenv("NEUROANALYST_HOME")) / "users"
        prefix: Optional[str] = None
    else:
        raise ValueError(f"Unknown kind '{kind}' for unique ID generation.")
    
    existing_ids: Set[str] = {
        dir.name for dir in working_dir.iterdir() if dir.is_dir()
    }
    
    for _ in range(max_attempts):
        new_id = generate_id(prefix=prefix)
        if new_id not in existing_ids:
            return new_id
    
    raise RuntimeError(f"Unable to generate unique {kind} after {max_attempts} attempts")