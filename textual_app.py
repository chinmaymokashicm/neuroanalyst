from app.utils.constants import *
from app.frontend.textual.widgets import Welcome, Submit, Visualize

from textual.app import App, ComposeResult, RenderResult
from textual.widget import Widget
from textual.widgets import Static, Button, TextArea
from textual.containers import Horizontal, Vertical, Container
from textual.binding import Binding

class DefaultDisplayWidget(Widget):
    """
    Default display widget to display a message.
    """
    text: str = "Select a resource."
    
    def render(self) -> RenderResult:
        """
        Render the default message.
        """
        return self.text

class AnotherDisplayWidget(Widget):
    """
    Another display widget to display a message.
    """
    text: str = "Another display widget."
    
    def render(self) -> RenderResult:
        """
        Render the default message.
        """
        return self.text

class OneOtherDisplayWidget(Widget):
    """
    Another display widget to display a message.
    """
    text: str = "One other display widget."
    
    def render(self) -> RenderResult:
        """
        Render the default message.
        """
        return self.text




class MainApp(App):
    CSS_PATH = [
        TEXTUAL_LAYOUT_MAIN_CSS_PATH,
        TEXTUAL_LAYOUT_SUBMIT_CSS_PATH,
        ]
    
    # BINDINGS = [
    #     Binding("d", "toggle_dark_mode", "Toggle Dark Mode"),
    #     Binding("r", "refresh", "Refresh"),
    #     Binding("q", "quit", "Quit"),
    # ]
    
    def compose(self) -> ComposeResult:
        """
        Compose the layout of the app.
        
        Layout-
        - Welcome Static Widget at the top (full width)
        - Left container for submit widgets
        - Right container for output widgets
        """
        with Vertical(classes="screen-container"):
            yield Welcome(classes="welcome-container")
            with Horizontal(classes="main-container"):
                yield Submit(classes="left-container")
                yield Visualize(classes="right-container")
            yield Container(Button("OK", id="close", variant="success"), classes="exit-container")
        
        
class TestApp(App):
    def compose(self) -> ComposeResult:
        yield TextArea("Hello World!", id="text_area")

if __name__ == "__main__":
    app = MainApp()
    # app = TestApp()
    app.run()