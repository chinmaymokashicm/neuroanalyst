"""
Module for provenance related code.
"""
import json
from pathlib import Path

def trace_root_sidecar(starting_sidecar_path: str | Path) -> str:
    """
    Trace the root sidecar from a given sidecar JSON file.
    Logic:
        - Every raw and pipeline file has a sidecar JSON file.
        - Raw file sidecar does not contain "InputFile" or "OutputFile" field.
        - Pipeline file sidecar contains "InputFile" or "OutputFile" field pointing to the file it was generated from.
        - Keep tracing back until a sidecar without these fields is found.
        
    Args:
        starting_sidecar_path (Path): Path to the starting sidecar JSON file.
    Returns:
        root_sidecar_path (Path): Path to the root sidecar JSON file.
    """
    current_sidecar_path: Path = Path(starting_sidecar_path)

    while True:
        try:
            with open(current_sidecar_path, 'r') as f:
                sidecar_data = json.load(f)
        except Exception as e:
            print(f"Error reading sidecar JSON file at {current_sidecar_path}: {e}")
            break

        input_file: str = sidecar_data.get("InputFile", None)

        if input_file:
            current_sidecar_path: Path = Path(current_sidecar_path).parent / (input_file.split(".")[0] + ".json")
        else:
            # No more InputFile field, we've reached the root
            break

    return current_sidecar_path