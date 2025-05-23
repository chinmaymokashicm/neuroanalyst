from .....utils.constants import *
from ...helpers import refresh_widget, DefaultDisplayWidget, APIActionEnum, APIRouteEnum
from ..components.data_viewer import DataSubmitterWidget
from ..components.action import ActionOnWidget

import json
from typing import Optional

from textual import on, log
from textual.app import App, ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.containers import Container, Horizontal
from textual.widgets import Select, Markdown, TabbedContent, TabPane, Tabs, Tab

class SubmitPipeline(Widget):
    """
    Widget that handles all submit actions for pipelines.
    Layout:
    - Tabs for different actions (create, execute, delete)
    - Widget dependent on the selected action
    """
    tabs: Tabs
    display_widget_class: str = "resource-display-tab-widget"
    display_widget: Widget = DefaultDisplayWidget()
    
    def compose(self) -> ComposeResult:
        yield Tabs(
            Tab("Build Pipeline", id="build_pipeline"),
            Tab("Execute Pipeline", id="execute_pipeline"),
            Tab("Delete Pipeline", id="delete_pipeline"),
        )
        yield self.display_widget
        
    @on(Tabs.TabActivated)
    def on_tab_activated(self, event: Tabs.TabActivated) -> None:
        """
        Handle the tab activated event.
        """
        if event.tab.id == "build_pipeline":
            # Build pipeline
            default_dict: dict = {
                "name": "random_pipeline",
                "author": "Chinmay Mokashi",
                "description": "Random pipeline",
                "process_exec_ids": ["PE-123456", "PE-654321"],
                "checkpoint_steps": [0, 1]
            }
            default_json: str = json.dumps(default_dict, indent=4)
            submit_url: str = f"http://{FASTAPI_HOSTNAME}:{FASTAPI_PORT}/pipeline/create/"
            
            refresh_widget(
                self, 
                "display_widget", 
                DataSubmitterWidget, 
                self.display_widget_class, 
                submit_url=submit_url, 
                default_data=default_json,
                language="json",
                )
        elif event.tab.id == "execute_pipeline":
            # Execute pipeline 
            refresh_widget(self, "display_widget", ActionOnWidget, self.display_widget_class, api_route=APIRouteEnum.PIPELINE, action=APIActionEnum.EXECUTE)
        elif event.tab.id == "delete_pipeline":
            # Delete pipeline
            refresh_widget(self, "display_widget", ActionOnWidget, self.display_widget_class, api_route=APIRouteEnum.PIPELINE, action=APIActionEnum.DELETE)