from ...helpers import refresh_widget, DefaultDisplayWidget, AnotherDisplayWidget, OneOtherDisplayWidget
from .process import SubmitProcess
from .pipeline import SubmitPipeline

from textual import on, log
from textual.app import App, ComposeResult, RenderResult
from textual.widget import Widget
from textual.containers import Container, Horizontal
from textual.widgets import Select, Markdown

class Submit(Widget):
    """
    Widget that handles all submit actions.
    Layout:
    - 2 horizontal select widgets (select API, select resource (dependent on API selection))
    - Widget dependent on previous selection
    """
    
    select_api: Select
    select_resource: Select
    display_widget_class: str
    display_widget: Widget = DefaultDisplayWidget()
    
    options: dict[str, list[str]] = {
        "core": ["process", "pipeline"],
        "insight": ["submit_user_query", "generate_report"]
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.select_api = Select(id="api_select", options=[(key.replace("_", " ").title(), key) for key in self.options.keys()])
        self.select_resource = Select(id="resource_select", options=[])
        self.display_widget_class = "submit-display-widget-container"
        self.display_widget = DefaultDisplayWidget(classes=self.display_widget_class)
        
    def compose(self) -> ComposeResult:
        with Horizontal(classes="submit-select-container"):
            yield self.select_api
            yield self.select_resource
        yield self.display_widget
        
    @on(Select.Changed, "#api_select")
    def update_resource_options(self, event: Select.Changed) -> None:
        """
        Update the resource select options based on the selected API.
        """
        selected_api: str | Select.BLANK = event.value
        options: list[str] = []
        if not selected_api == Select.BLANK:
            options = [(option.replace("_", " ").title(), option) for option in self.options[selected_api]]
        self.select_resource.set_options(options=options)
        self.select_resource.value = Select.BLANK
            
    @on(Select.Changed, "#resource_select")
    def update_display_widget(self, event: Select.Changed) -> None:
        """
        Update the display widget based on the selected resource.
        """
        selected_resource: str | Select.BLANK = event.value
        if not selected_resource == Select.BLANK:
            if selected_resource == "process":
                refresh_widget(self, "display_widget", SubmitProcess, self.display_widget_class)
            elif selected_resource == "pipeline":
                refresh_widget(self, "display_widget", SubmitPipeline, self.display_widget_class)
        else:
            refresh_widget(self, "display_widget", DefaultDisplayWidget, self.display_widget_class)