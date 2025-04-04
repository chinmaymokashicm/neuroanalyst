from app.utils.constants import *
from app.frontend.textual.widgets import Welcome, Submit, Visualize

from textual import on, log
from textual.app import App, ComposeResult, RenderResult
from textual.widget import Widget
from textual.widgets import Static, Button, TextArea
from textual.containers import Horizontal, Vertical, Container
from textual.binding import Binding

class MainApp(App):
    CSS_PATH = [
        TEXTUAL_LAYOUT_MAIN_CSS_PATH,
        TEXTUAL_LAYOUT_RESOURCE_CSS_PATH,
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
            yield Container(Button("EXIT", id="close", variant="success"), classes="exit-container")
            
    
    @on(Button.Pressed, "#close")
    def close(self) -> None:
        """
        Close the app.
        """
        self.exit()
        
class TestApp(App):
    def compose(self) -> ComposeResult:
        yield TextArea("Hello World!", id="text_area")

if __name__ == "__main__":
    app = MainApp()
    # app = TestApp()
    app.run()