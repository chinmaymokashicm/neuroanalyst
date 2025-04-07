from .....utils.constants import *
from .....models.core.process.execute import ProcessExecConfig
from ...helpers import refresh_widget, DefaultDisplayWidget, APIActionEnum, APIRouteEnum
from ..components.table_viewer import TabularData
from ..components.action import ActionOnWidget

import json
from typing import Optional

from textual import on, log
from textual.app import App, ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.containers import Container, Horizontal
from textual.widgets import Select, Markdown, TabbedContent, TabPane, Tabs, Tab

class VisualizeDataset(Widget):
    """
    Widget that handles all visualize actions for datasets.
    Layout:
    - Tabs for different actions (create, execute, delete)
    - Widget dependent on the selected action
    """
    tabs: Tabs
    display_widget_class: str = "resource-display-tab-widget"
    display_widget: Widget = DefaultDisplayWidget()
    
    def compose(self) -> ComposeResult:
        yield Tabs(
            Tab("View Datasets", id="view_all_datasets"),
            Tab("View Dataset Info", id="view_dataset_info"),
        )
        yield self.display_widget
        
    @on(Tabs.TabActivated)
    def on_tab_activated(self, event: Tabs.TabActivated) -> None:
        """
        Handle the tab activated event.
        """
        if event.tab.id == "view_all_datasets":
            refresh_widget(self, "display_widget", TabularData, self.display_widget_class, api_route=APIRouteEnum.DATASET)
        elif event.tab.id == "view_dataset_info":
            refresh_widget(self, "display_widget", ActionOnWidget, self.display_widget_class, api_route=APIRouteEnum.DATASET, view_only=True)
        else:
            refresh_widget(self, "display_widget", DefaultDisplayWidget, self.display_widget_class, text="Select a resource.")