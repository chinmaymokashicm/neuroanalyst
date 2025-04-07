from .....utils.constants import *
from .....models.core.process.execute import ProcessExecConfig
from ...helpers import refresh_widget, DefaultDisplayWidget, APIActionEnum, APIRouteEnum
from ..components.data_viewer import DataSubmitterWidget
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
    display_widget_class: str = "resource-display-tab-widget"
    display_widget: Widget = DefaultDisplayWidget()
    
    def compose(self) -> ComposeResult:
        yield Tabs(
            Tab("View Processes", id="view_process"),
            Tab("View Process Execs", id="view_process_exec"),
            Tab("View Process Image Info", id="view_process_image_info"),
            Tab("View Process Exec Info", id="view_process_exec_info"),
        )
        yield self.display_widget
        
    @on(Tabs.TabActivated)
    def on_tab_activated(self, event: Tabs.TabActivated) -> None:
        """
        Handle the tab activated event.
        """
        if event.tab.id == "view_process":
            refresh_widget(self, "display_widget", TabularData, self.display_widget_class, api_route=APIRouteEnum.PROCESS_IMAGE)
        elif event.tab.id == "view_process_exec":
            refresh_widget(self, "display_widget", TabularData, self.display_widget_class, api_route=APIRouteEnum.PROCESS_EXEC)
        elif event.tab.id == "view_process_image_info":
            refresh_widget(self, "display_widget", ActionOnWidget, self.display_widget_class, api_route=APIRouteEnum.PROCESS_IMAGE, view_only=True)
        elif event.tab.id == "view_process_exec_info":
            refresh_widget(self, "display_widget", ActionOnWidget, self.display_widget_class, api_route=APIRouteEnum.PROCESS_EXEC, view_only=True)
        else:
            refresh_widget(self, "display_widget", DefaultDisplayWidget, self.display_widget_class, text="Select a resource.")