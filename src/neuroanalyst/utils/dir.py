from pathlib import Path

def generate_directory_tree(path: Path, base_path: Path):
    """
    Recursively generate a directory tree structure.
    
    Args:
        path (Path): Current path to process
        base_path (Path): Base path for the dataset (for relative paths)
    
    Returns:
        Dict: Directory tree structure
    """
    result = {
        "name": path.name,
        "type": "directory" if path.is_dir() else "file",
        "abs_path": str(path.absolute()),
        "rel_path": str(path.relative_to(base_path)),
    }
    
    if path.is_dir():
        result["children"] = []
        for item in path.iterdir():
            child_info = generate_directory_tree(item, base_path)
            result["children"].append(child_info)
        
        # Sort children: directories first, then files, both alphabetically
        result["children"].sort(key=lambda x: (0 if x["type"] == "directory" else 1, x["name"]))

    return result