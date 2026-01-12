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

def find_and_transform_instances(data: Any, cls: type, path: str = "", visited: Set[int] = None) -> Generator[Tuple[str, type], None, None]:
    """
    Recursively search through nested dictionaries and lists to find instances of a specified class.
    When an instance is found, it is transformed into the specified class.
    
    Args:
        data (Any): The input data structure (dicts/lists) to search.
        cls (type): The class type to search for and transform into.
        path (str): The current path in the data structure (for tracking).
        visited (Set[int]): Set of visited object ids to prevent infinite loops.
        
    Yields:
        Tuple[str, type]: A tuple containing the path to the instance and the transformed instance.
    """
    if visited is None:
        visited = set()

    if id(data) in visited:
        return

    if not isinstance(data, (dict, list)):
        return

    visited.add(id(data))

    if isinstance(data, dict):
        # Strict schema gate
        required = set(cls.model_fields.keys())
        if required.intersection(data.keys()):
            try:
                instance = cls(**data)
                yield path, instance
                return  # do NOT recurse into a valid instance
            except Exception:
                pass

        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            yield from find_and_transform_instances(value, cls, new_path, visited)

    else:  # list
        for i, item in enumerate(data):
            yield from find_and_transform_instances(item, cls, f"{path}[{i}]", visited)