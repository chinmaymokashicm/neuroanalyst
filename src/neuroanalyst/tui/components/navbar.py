"""
Navbar component for the NeuroAnalyst TUI application.
"""

from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Button, Select
from textual.screen import Screen
from textual.reactive import reactive

class NavbarCategory(Select):
    """A category in the navbar."""
    def __init__(self, name: str, options: dict[str, str]):
        super().__init__(
            [(option, option) for option in options.keys()],
            id=f"nav_{name.lower()}",
            prompt=f"{name}"
        )
        self.options_dict = options
        
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle selection changes."""
        selected_option = event.value
        if selected_option in self.options_dict:
            screen_name = self.options_dict[selected_option]
            self.app.push_screen(screen_name)

class Navbar(Horizontal):
    """A navigation bar component."""
    
    def __init__(self, categories: dict[str, dict[str, str]]):
        """Initialize the navbar with options."""
        super().__init__(id="navbar")
        
        # Define the navbar structure
        self.categories = [
            NavbarCategory(name, options) for name, options in categories.items()
        ]
    
    def compose(self) -> ComposeResult:
        """Create the navbar UI."""
        
        for category in self.categories:
            yield category