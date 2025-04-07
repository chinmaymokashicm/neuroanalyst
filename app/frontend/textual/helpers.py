from typing import Optional, Any, get_type_hints
import random
import inspect
from enum import Enum

from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult, RenderResult

class DefaultDisplayWidget(Widget):
    """
    Default display widget to display a message.
    """
    text: str = "Select a resource."
    
    def __init__(self, text: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.text = text if text is not None else self.text
        self.text
    
    def render(self) -> RenderResult:
        """
        Render the default message.
        """
        return self.text
    
    def compose(self) -> ComposeResult:
        """
        Compose the default display widget.
        """
        yield Static(self.render(), id="default-message")

class APIActionEnum(Enum):
    """
    Enum for actions.
    """
    DELETE = "delete"
    UPDATE = "update"
    CREATE = "create"
    EXECUTE = "execute"
    
class APIRouteEnum(Enum):
    """
    Enum for API routes.
    """
    PROCESS_IMAGE = "/process/image"
    PROCESS_EXEC = "/process/exec"
    WORKDIR = "/process/workdir"
    PIPELINE = "/pipeline"
    DATASET = "/dataset"

def refresh_widget(root_widget: Widget, widget_to_refresh_name: str, updated_widget: Widget, new_widget_class: Optional[str] = None, **properties) -> None:
    """
    Refresh a widget in the root widget.
    """
    old_widget = getattr(root_widget, widget_to_refresh_name)
    new_widget = updated_widget(classes=new_widget_class, **properties)
    old_widget.remove()
    setattr(root_widget, widget_to_refresh_name, new_widget)
    root_widget.mount(new_widget)
    new_widget.refresh()



# ! NOT using it currently

def generate_random_args(func):
    """
    Generates random arguments for a function based on its type hints.
    """
    type_hints = get_type_hints(func)
    args = {}
    for param_name, param_type in type_hints.items():
        if param_name == 'return':
            continue
        args[param_name] = generate_value_for_type(param_type)
    return args

def generate_value_for_type(param_type):
    """
    Generates a random value for a given type.
    """
    if param_type == int:
        return random.randint(-100, 100)
    elif param_type == float:
        return random.uniform(-100.0, 100.0)
    elif param_type == str:
        return ''.join(random.choices('abcdefg', k=5))
    elif param_type == bool:
        return random.choice([True, False])
    elif hasattr(param_type, '__origin__') and param_type.__origin__ == list:
      return [generate_value_for_type(param_type.__args__[0]) for _ in range(random.randint(0, 5))]
    # Add more type handling as needed (e.g., for lists, dicts, custom classes)
    else:
        return None # Default case if type is not handled

# Example Usage
# def my_function(a: int, b: str, c: bool, d: list[int]) -> float:
#     """
#     Example function with type hints.
#     """
#     return float(a) + len(b) + (1.0 if c else 0.0) + sum(d)

# random_args = generate_random_args(my_function)
# print(f"Generated arguments: {random_args}")

# result = my_function(**random_args)
# print(f"Result of function call: {result}")
