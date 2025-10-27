from typing import Optional

from textual.widgets import Tree

def build_tree(data: dict[str, any], tree: Optional[Tree[str]] = None) -> Tree[str]:
    """
    Recursively build a tree from a nested dictionary. Handle dictionaries as branches and lists as leaves.
    
    Args:
        data (dict): The nested dictionary to convert into a tree.
    """
    if tree is None:
        tree = Tree("")
    tree.root.expand()
    for key, value in data.items():
        if isinstance(value, dict):
            branch = tree.root.add(key)
            build_tree(value, branch)
        elif isinstance(value, list):
            branch = tree.root.add(key)
            for item in value:
                branch.add_leaf(str(item))
        else:
            tree.root.add(f"{key}: {value}")
    return tree