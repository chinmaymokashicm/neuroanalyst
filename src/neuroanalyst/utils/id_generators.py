"""
Generic ID generation utilities for NeuroAnalyst.
"""

import random
from pathlib import Path
from typing import Set, Dict, Optional


# ID type configurations
ID_CONFIGS: Dict[str, Dict[str, str]] = {
    "process_id": {"prefix": "PR", "digits": 6},
    "process_exec_id": {"prefix": "PE", "digits": 6}, 
    "pipeline_id": {"prefix": "PL", "digits": 6},
    "neuprocess_id": {"prefix": "NP", "digits": 6},
    "neuprocess_exec_id": {"prefix": "NE", "digits": 6},
    "user": {"prefix": "US", "digits": 6},
}


def generate_id(id_type: str) -> str:
    """
    Generate a unique ID for the specified type.
    
    Args:
        id_type: Type of ID to generate (process_id, process_exec_id, pipeline_id, etc.)
        
    Returns:
        str: Generated ID (e.g., "PR-123456", "PE-789012")
        
    Raises:
        ValueError: If id_type is not recognized
    """
    if id_type not in ID_CONFIGS:
        raise ValueError(f"Unknown ID type: {id_type}. Available types: {list(ID_CONFIGS.keys())}")
    
    config = ID_CONFIGS[id_type]
    prefix = config["prefix"]
    digits = config["digits"]
    
    # Generate random number with specified digits
    min_val = 10 ** (digits - 1)
    max_val = (10 ** digits) - 1
    number = random.randint(min_val, max_val)
    
    return f"{prefix}-{number}"


def generate_unique_id(id_type: str, existing_ids: Set[str] = None, max_attempts: int = 1000) -> str:
    """
    Generate a unique ID that doesn't conflict with existing IDs.
    
    Args:
        id_type: Type of ID to generate
        existing_ids: Set of existing IDs to avoid conflicts
        max_attempts: Maximum number of generation attempts
        
    Returns:
        str: Unique ID
        
    Raises:
        RuntimeError: If unable to generate unique ID after max_attempts
    """
    if existing_ids is None:
        existing_ids = set()
    
    for _ in range(max_attempts):
        new_id = generate_id(id_type)
        if new_id not in existing_ids:
            return new_id
    
    raise RuntimeError(f"Unable to generate unique {id_type} after {max_attempts} attempts")


# Legacy functions for backward compatibility
def generate_process_id() -> str:
    """Generate a process ID (legacy function)."""
    return generate_id("process_id")


def generate_unique_process_id(existing_ids: Set[str] = None, max_attempts: int = 1000) -> str:
    """Generate a unique process ID (legacy function)."""
    return generate_unique_id("process_id", existing_ids, max_attempts)


# Generic availability checking functions
def check_id_availability(id_value: str, base_path: Path) -> bool:
    """
    Check if an ID is available (no existing directory with that name).
    
    Args:
        id_value: ID to check
        base_path: Base path where directories are created
        
    Returns:
        bool: True if available, False if directory already exists
    """
    directory_path = base_path / id_value
    return not directory_path.exists()


def generate_available_id(id_type: str, base_path: Path, max_attempts: int = 1000) -> str:
    """
    Generate an ID that is guaranteed to be available in the given path.
    
    Args:
        id_type: Type of ID to generate
        base_path: Base path where directories are created
        max_attempts: Maximum number of generation attempts
        
    Returns:
        str: Available ID
        
    Raises:
        RuntimeError: If unable to generate available ID after max_attempts
    """
    base_path = Path(base_path)
    
    for _ in range(max_attempts):
        new_id = generate_id(id_type)
        if check_id_availability(new_id, base_path):
            return new_id
    
    raise RuntimeError(f"Unable to generate available {id_type} after {max_attempts} attempts")


# Legacy functions for backward compatibility
def check_process_id_availability(process_id: str, base_path: Path) -> bool:
    """Check if a process ID is available (legacy function)."""
    return check_id_availability(process_id, base_path)


def generate_available_process_id(base_path: Optional[Path] = None, max_attempts: int = 1000) -> str:
    """Generate an available process ID (legacy function)."""
    if base_path is None:
        from .constants import PATHS
        base_path = PATHS.workdir
    return generate_available_id("process_id", base_path, max_attempts)


def generate_process_exec_id() -> str:
    """Generate a process execution ID."""
    return generate_id("process_exec_id")


def generate_unique_process_exec_id(existing_ids: Set[str] = None, max_attempts: int = 1000) -> str:
    """Generate a unique process execution ID."""
    return generate_unique_id("process_exec_id", existing_ids, max_attempts)


def generate_available_process_exec_id(base_path: Optional[Path] = None, max_attempts: int = 1000) -> str:
    """Generate an available process execution ID."""
    if base_path is None:
        from .constants import PATHS
        base_path = PATHS.workdir
    return generate_available_id("process_exec_id", base_path, max_attempts)
