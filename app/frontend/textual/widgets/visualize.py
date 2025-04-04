from textual.app import App, ComposeResult, RenderResult
from textual.widget import Widget

class Visualize(Widget):
    """
    Welcome widget to display a welcome message.
    """
    def render(self) -> RenderResult:
        """
        Render the welcome message.
        """
        text: str = """Welcome to the Neuroanalyst App!"""
        return text