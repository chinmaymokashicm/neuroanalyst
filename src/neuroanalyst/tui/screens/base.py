"""
Base screen class with navbar for the NeuroAnalyst TUI application.
"""
from constants import SCREEN_NAMES
from components.navbar import Navbar

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static
from textual import log

class BaseScreen(Screen):
    """A base screen class that includes the navbar."""
    
    def compose(self) -> ComposeResult:
        """Create the UI layout with navbar."""
        
        # Use a vertical layout to ensure proper ordering
        categories: dict[str, dict[str, str]] = {
            "Logic": {
                "View All": SCREEN_NAMES["logic"]["list"],
                "Register New": SCREEN_NAMES["logic"]["register"]
            },
            "Process": {
                "View All": SCREEN_NAMES["process"]["list"],
                "Register New": SCREEN_NAMES["process"]["wizard"]
            },
            "Pipeline": {
                "View All": SCREEN_NAMES["pipeline"]["list"],
                "Register New": SCREEN_NAMES["pipeline"]["wizard"]
            },
        }
        yield Vertical(
            # Navbar at the top
            Navbar(categories),
            # Suboptions container (will be populated by Navbar)
            Container(id="suboptions_container", classes="suboptions hidden"),
            # Content container below navbar
            Container(
                *self.compose_content(),
                Static("Press 'q' to quit, 'h' for home, or 'escape' to go back", id="footer_spacer"),
                id="content_container"
                ),
            id="main_layout"
        )
    
    def compose_content(self) -> ComposeResult:
        """Placeholder for screen-specific content."""
        pass
        
    def on_mount(self) -> None:
        """Mount the screen content when the screen is mounted."""
        pass