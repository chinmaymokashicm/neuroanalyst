from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Static, Header, Button, Label
from textual.containers import Grid

# class PopupScreen(Screen):
class PopupScreen(ModalScreen):
    title: str = "Popup Screen"
    content: str = "This is a popup screen."
    footer: str = "Press any key to continue."
    
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self, title: str = None, content: str = None, footer: str = None, **kwargs):
        super().__init__(**kwargs)
        if title:
            self.title = title
        if content:
            self.content = content
        if footer:
            self.footer = footer

    def compose(self) -> ComposeResult:
        yield Grid(
            Header(self.title, classes="popup-header"),
            Label(self.content, classes="popup-content"),
            # Button("Quit", variant="error", id="quit"),
            # Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )