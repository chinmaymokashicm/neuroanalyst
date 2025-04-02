from typing import Any, Optional

import re

def search_nested_key(data: Any, key: str, nesting_sep: str = ".") -> Optional[Any]:
    if isinstance(data, dict):
        if nesting_sep in key:
            first_key: str = key.split(nesting_sep)[0]
            if first_key in data:
                return search_nested_key(data[first_key], f"{nesting_sep}".join(key.split(nesting_sep)[1:]), nesting_sep=nesting_sep)
        else:
            if key in data:
                return data[key]
            
def match_dict_with_filters(data: dict[str, any], filters: dict[str, str]) -> bool:
    for key, pattern in filters.items():
        value: Optional[Any] = search_nested_key(data, key)
        if not value:
            return False
        value = str(value)
        if not re.search(pattern, value):
            return False
    return True