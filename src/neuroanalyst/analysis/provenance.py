"""
Module for provenance related code.
"""
import json
from pathlib import Path

def trace_root_sidecar(starting_sidecar_path: str | Path, root_dirpath: str = "/data") -> str:
    """
    Trace the root sidecar from a given sidecar JSON file.
    Logic:
        - Every raw and pipeline file has a sidecar JSON file.
        - Raw file sidecar does not contain "InputFile" field.
        - Pipeline file sidecar contains "InputFile" field pointing to the file it was generated from.
        - Keep tracing back until a sidecar without these fields is found.
        
    Args:
        starting_sidecar_path (Path): Path to the starting sidecar JSON file.
        root_dirpath (str): Root directory path for all files.
            If running inside a container, the root path for all derived sidecars would be /data.
            This fails if running outside a container and the root path for the raw files maps to the host system.
    Returns:
        root_sidecar_path (Path): Path to the root sidecar JSON file.
    """
    current_sidecar_path: Path = Path(starting_sidecar_path)

    while True:
        try:
            if not current_sidecar_path.exists():
                # Replace /data with root_dirpath and try again
                if str(current_sidecar_path).startswith("/data"):
                    print(f"Sidecar file does not exist: {current_sidecar_path}. Attempting to map to root dirpath.")
                    relative_path = current_sidecar_path.relative_to("/data")
                    current_sidecar_path = Path(root_dirpath) / relative_path
                    if not current_sidecar_path.exists():
                        print(f"Sidecar file does not exist: {current_sidecar_path}")
                        break
                else:
                    print(f"Sidecar file does not exist: {current_sidecar_path}")
                    break
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