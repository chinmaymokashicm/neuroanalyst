"""
Home screen for the NeuroAnalyst TUI application.
"""
from .base import BaseScreen

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import MarkdownViewer, Markdown, Button
from textual import on

class HomeScreen(BaseScreen):
    """The home screen for the NeuroAnalyst TUI application."""

    def compose_content(self) -> ComposeResult:
        """Create the UI layout for the home screen."""
        
        with open("text/welcome.md", "r") as f:
            welcome_text = f.read()

        yield Markdown(welcome_text)
        yield Horizontal(
            Vertical(
                Button("View Logics", id="logic_btn", variant="primary"),
                Button("Create New Logic", id="new_logic_btn", variant="success"),
                classes="menu"
            ),
            Vertical(
                Button("View Processes", id="process_btn", variant="primary"),
                Button("Create New Process", id="new_process_btn", variant="success"),
                classes="menu"
            ),
            Vertical(
                Button("View Pipelines", id="pipeline_btn", variant="primary"),
                Button("Create New Pipeline", id="new_pipeline_btn", variant="success"),
                classes="menu"
            ),
            classes="home_button_row"
        )
    
    @on(Button.Pressed, "#logic_btn")
    def go_to_logic_list(self) -> None:
        """Navigate to the logic list screen."""
        self.app.push_screen("logic_list")

    @on(Button.Pressed, "#new_logic_btn")
    def go_to_register_logic(self) -> None:
        """Navigate to the register logic screen."""
        self.app.push_screen("logic_register")

    @on(Button.Pressed, "#process_btn")
    def go_to_process_list(self) -> None:
        """Navigate to the process list screen."""
        self.app.push_screen("process_list")

    @on(Button.Pressed, "#new_process_btn")
    def go_to_register_process(self) -> None:
        """Navigate to the register process screen."""
        self.app.push_screen("process_wizard")

    @on(Button.Pressed, "#pipeline_btn")
    def go_to_pipeline_list(self) -> None:
        """Navigate to the pipeline list screen."""
        self.app.push_screen("pipeline_list")

    @on(Button.Pressed, "#new_pipeline_btn")
    def go_to_register_pipeline(self) -> None:
        """Navigate to the register pipeline screen."""
        self.app.push_screen("pipeline_wizard")