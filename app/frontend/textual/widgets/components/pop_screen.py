from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Static, Header, Button, Label, Footer, Markdown, MarkdownViewer
from textual.containers import Grid

# class PopupScreen(Screen):
class PopupScreen(ModalScreen):
    title: str = "Popup Screen"
    content: str = "This is a popup screen."
    footer: str = "Press any key to continue."
    show_table_of_contents: bool = True
    
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self, title: str = None, content: str = None, footer: str = None, show_table_of_contents: bool = True, **kwargs):
        super().__init__(**kwargs)
        if title:
            self.title = title
        if content:
            self.content = content
        if footer:
            self.footer = footer
        self.show_table_of_contents = show_table_of_contents

    def compose(self) -> ComposeResult:
        yield Grid(
            Header(self.title, classes="popup-header"),
            # Markdown(self.content, classes="popup-content"),
            MarkdownViewer(self.content, classes="popup-content", show_table_of_contents=self.show_table_of_contents),
            # Button("Quit", variant="error", id="quit"),
            # Button("Cancel", variant="primary", id="cancel"),
            Footer(classes="popup-footer"),
            id="dialog",
        )