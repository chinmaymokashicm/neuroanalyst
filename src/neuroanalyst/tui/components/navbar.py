"""
Navbar component for the NeuroAnalyst TUI application.
"""
import sys
from pathlib import Path
# sys.path.append(str(Path(__file__).resolve().parents[2]))
# from tui.components.modal import InfoModal


from typing import Iterable

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Button, Select
from textual.screen import Screen
from textual.reactive import reactive
from textual import on

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
        yield Select([(username, username) for username in self.app.global_vars.get("registered_users", [])], id="user_select", prompt="User")
        
    def on_mount(self) -> None:
        """Set up the user selection on mount."""
        user_select = self.query_one("#user_select", Select)
        users = self.app.global_vars.get("registered_users", [])
        user_select.options = [(user, user) for user in users]
        current_user = self.app.global_vars.get("username", None)
        if current_user:
            user_select.value = current_user
            
    @on(Select.Changed, "#user_select")
    def on_user_select_changed(self, event: Select.Changed) -> None:
        """Handle user selection changes."""
        selected_user = event.value
        if selected_user in self.app.global_vars.get("registered_users", []):
            self.app.global_vars["username"] = selected_user
            # self.app.push_screen(InfoModal(f"Switched to user: {selected_user}"))
            self.app.notify(f"Switched to user: {selected_user}", severity="info")