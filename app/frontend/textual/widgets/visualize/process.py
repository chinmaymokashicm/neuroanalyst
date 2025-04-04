from .....utils.constants import *
from .....models.core.process.execute import ProcessExecConfig
from ...helpers import refresh_widget, DefaultDisplayWidget, ActionEnum
from ..components.json_viewer import JSONViewerWidget
from ..components.action import ActionOnWidget
from ..components.table_viewer import TabularData

import json
from typing import Optional

from textual import on, log
from textual.app import App, ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.containers import Container, Horizontal
from textual.widgets import Select, Markdown, TabbedContent, TabPane, Tabs, Tab

class VisualizeProcess(Widget):
    """
    Widget that handles all visualize actions for processes.
    Layout:
    - Tabs for different actions (create, execute, delete)
    - Widget dependent on the selected action
    """
    tabs: Tabs
    display_widget_class: str = "resource-display-tab-widget"
    display_widget: Widget = DefaultDisplayWidget()
    
    def compose(self) -> ComposeResult:
        yield Tabs(
            Tab("View Processes", id="view_process"),
            Tab("View Process Execs", id="view_process_exec"),
        )
        yield self.display_widget
        
    @on(Tabs.TabActivated)
    def on_tab_activated(self, event: Tabs.TabActivated) -> None:
        """
        Handle the tab activated event.
        """
        if event.tab.id == "view_process":
            refresh_widget(self, "display_widget", TabularData, self.display_widget_class, collection_name=COLLECTION_PROCESS_IMAGES)
        elif event.tab.id == "view_process_exec":
            refresh_widget(self, "display_widget", TabularData, self.display_widget_class, collection_name=COLLECTION_PROCESS_EXECS)
        else:
            refresh_widget(self, "display_widget", DefaultDisplayWidget, self.display_widget_class, text="Select a resource.")