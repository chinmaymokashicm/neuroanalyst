from textual.app import App, ComposeResult, RenderResult
from textual.widget import Widget
from textual.widgets import Static

class Welcome(Widget):
    """
    Welcome widget to display a welcome message.
    """
    def render(self) -> RenderResult:
        """
        Render the welcome message.
        """
        text: str = """Welcome to the NeuroAnalyst App!"""
        return text
    
    def compose(self) -> ComposeResult:
        """
        Compose the welcome widget.
        """
        yield Static(self.render(), id="welcome-message")