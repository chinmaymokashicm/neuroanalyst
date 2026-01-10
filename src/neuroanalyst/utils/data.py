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

def find_and_transform_instances(data: Any, cls: type, path: str = "",visited: Set[int] = None) -> Generator[Tuple[str, type], None, None]:
    if visited is None:
        visited = set()

    # Prevent infinite loops
    if id(data) in visited:
        return
    
    # We only care about dicts and lists for traversal
    if isinstance(data, (dict, list)):
        visited.add(id(data))
    else:
        return

    # Check if this specific dictionary is an instance of the target class
    if isinstance(data, dict):
        try:
            instance = cls(**data)
            yield (path, instance)
        except Exception:
            pass
        # Note: We usually don't recurse inside an instance once found

    # Otherwise, keep searching deeper
    iterator = data.items() if isinstance(data, dict) else enumerate(data)
    for key, value in iterator:
        new_path = f"{path}[{key}]" if isinstance(data, list) else (f"{path}.{key}" if path else str(key))
        
        if isinstance(value, (dict, list)):
            yield from find_and_transform_instances(value, cls, new_path, visited)