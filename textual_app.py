from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll, VerticalGroup, HorizontalGroup
from textual.screen import Screen
from textual.widgets import Button, Digits, Footer, Header, Input
from textual.demo.page import PageScreen
from textual.binding import Binding
from textual import containers, events, lazy, on

class TimeDisplay(Digits):
    """A widget to display elapsed time."""


class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch())

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
        
class FormOptions(HorizontalGroup):
    
    def compose(self) -> ComposeResult:
        yield Button("Submit", id="submit")
        yield Button("Cancel", id="cancel")
        yield Button("Reset", id="reset")

class Form(VerticalGroup):
    
    def compose(self) -> ComposeResult:
        yield TimeDisplay("00:00:00.00")
        yield Input(placeholder="Enter your name", id="name")
        yield FormOptions()
        
class HomeScreen(PageScreen):
    CSS = """
    WidgetsScreen {
        align-horizontal: center;
        Markdown {
            background: transparent;
        } & > VerticalScroll {
            scrollbar-gutter: stable;
            & > * {
                &:even { background: $boost; }
                padding-bottom: 1;
            }
        }
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Toggle dark mode"),
    ]
    
    def compose(self) -> ComposeResult:
        with lazy.Reveal(VerticalScroll(can_focus=False)):
            yield Stopwatch()
            yield Form()
        yield Footer()

class MainApp(App):
    def get_default_screen(self) -> Screen:
        return HomeScreen()


if __name__ == "__main__":
    # app = StopwatchApp()
    # app.run()
    app = MainApp()
    app.run()