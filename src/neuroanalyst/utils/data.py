from typing import Generator, Any, Tuple, Set

# Flatten nested metrics
def flatten_dict(d: dict[str, any], parent_key: str = '', sep: str = '.') -> dict[str, any]:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

def convert_string_to_number(s: str) -> any:
    try:
        if '.' in s:
            return float(s)
        else:
            return int(s)
    except ValueError:
        return None

def identify_instance_from_dict(
    data: Any, 
    cls: type, 
    path: str = "",
    visited: Set[int] = None
) -> Generator[Tuple[str, Any], None, None]:
    """
    Yields (path, instance) tuples for every instance of 'cls' found.
    Uses a 'visited' set of object IDs to safely handle circular references.
    """
    if visited is None:
        visited = set()

    # Get unique ID of current container to check for circularity
    data_id = id(data)
    if data_id in visited:
        return
    visited.add(data_id)

    # Determine iteration strategy
    if isinstance(data, dict):
        iterator = data.items()
    elif isinstance(data, list):
        iterator = enumerate(data)
    else:
        return

    for key, value in iterator:
        # Format path
        current_path = f"{path}[{key}]" if isinstance(data, list) else (f"{path}.{key}" if path else str(key))
        
        # Yield the instance if it matches the class
        if isinstance(value, cls):
            yield (current_path, value)
        
        # Recurse if the value is a container
        if isinstance(value, (dict, list)):
            yield from identify_instance_from_dict(value, cls, current_path, visited)