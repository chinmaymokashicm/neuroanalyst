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