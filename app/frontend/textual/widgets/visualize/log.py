from .....utils.constants import *
from .....models.core.process.execute import ProcessExecConfig
from ...helpers import refresh_widget, DefaultDisplayWidget, ActionEnum, APIRouteEnum
from ..components.table_viewer import TabularData
from ..components.log_viewer import StreamingLogWidget

import json
from typing import Optional

from textual import on, log
from textual.app import App, ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.containers import Container, Horizontal
from textual.widgets import Select, Markdown, TabbedContent, TabPane, Tabs, Tab

class VisualizeLog(Widget):
    """
    Widget that handles all visualize actions for logs.
    Layout:
    - Tabs for different actions (create, execute, delete)
    - Widget dependent on the selected action
    """
    display_widget_class: str = "resource-display-tab-widget"
    display_widget: Widget = DefaultDisplayWidget()
    
    def compose(self) -> ComposeResult:
        yield Tabs(
            Tab("Fast API", id="view_fastapi_logs"),
            Tab("Celery", id="view_celery_logs"),
        )
        yield self.display_widget
        
    @on(Tabs.TabActivated)
    def on_tab_activated(self, event: Tabs.TabActivated) -> None:
        """
        Handle the tab activated event.
        """
        if event.tab.id == "view_fastapi_logs":
            refresh_widget(self, "display_widget", StreamingLogWidget, self.display_widget_class, app_type="fastapi")
        elif event.tab.id == "view_celery_logs":
            refresh_widget(self, "display_widget", StreamingLogWidget, self.display_widget_class, app_type="celery")
        else:
            refresh_widget(self, "display_widget", DefaultDisplayWidget, self.display_widget_class, text="Select a resource.")