from textual.app import App, ComposeResult, RenderResult
from textual.widget import Widget
from textual.widgets import Static, Markdown

class Welcome(Widget):
    """
    Welcome widget to display a welcome message.
    """
    text: str = "Welcome to the NeuroAnalyst App!"
    
    def __init__(self, text: str = None, **kwargs):
        super().__init__(**kwargs)
        self.text = text if text is not None else self.text
    
    def render(self) -> RenderResult:
        """
        Render the welcome message.
        """
        return self.text
    
    def compose(self) -> ComposeResult:
        """
        Compose the welcome widget.
        """
        yield Markdown(self.render(), id="welcome-message")
        # yield Static(self.text, id="welcome-message")