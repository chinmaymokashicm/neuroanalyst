"""
This is a TUI application for NeuroAnalyst.

Functionalities:
- Logic
    - Register and edit logic
    - List all logics
- Processes
    - Build process (wizard)
        - Initialize process directory
        - Prepare process directory
        - Build Singularity image / virtual environment
    - List all processes
    - View process details
- Pipelines
    - Construct pipeline (wizard)
        - Initialize pipeline
        - Set remaining parameters
    - List all pipelines
    - View pipeline details and execute
- Execution Monitoring
    - Monitor running pipelines
    - View logs
"""

import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, Static, Button, Label, ListView, ListItem, Select
from textual.screen import Screen, ModalScreen
from textual.css.query import NoMatches
from textual.binding import Binding

from constants import SCREEN_NAMES
# Import screens
from screens.home import HomeScreen
from screens.logic.list import LogicListScreen
from screens.logic.register import RegisterLogicScreen
from screens.process.list import ProcessListScreen
from screens.process.wizard import ProcessWizardScreen
from screens.pipeline.list import PipelineListScreen
from screens.pipeline.wizard import PipelineWizardScreen

from components.modal import InfoModal

class NeuroAnalystTUI(App):
    """The main NeuroAnalyst TUI application."""
    
    CSS_PATH = "styles.tcss"
    TITLE = "NeuroAnalyst TUI"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("h", "push_screen('home')", "Home"),
        Binding("escape", "app.pop_screen", "Back", show=False),
    ]
    
    # Enable rich text markup by default
    ENABLE_MARKUP = True
    
    def __init__(self):
        super().__init__()
        self.title = "NeuroAnalyst TUI"
    
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Install all the screens
        self.install_screen(HomeScreen, name=SCREEN_NAMES["home"])
        self.install_screen(LogicListScreen, name=SCREEN_NAMES["logic"]["list"])
        self.install_screen(RegisterLogicScreen, name=SCREEN_NAMES["logic"]["register"])
        self.install_screen(ProcessListScreen, name=SCREEN_NAMES["process"]["list"])
        self.install_screen(ProcessWizardScreen, name=SCREEN_NAMES["process"]["wizard"])
        self.install_screen(PipelineListScreen, name=SCREEN_NAMES["pipeline"]["list"])
        self.install_screen(PipelineWizardScreen, name=SCREEN_NAMES["pipeline"]["wizard"])
        
        # Start with the home screen
        self.push_screen(SCREEN_NAMES["home"])
    
    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        yield Footer()


if __name__ == "__main__":
    app = NeuroAnalystTUI()
    app.run()