from .....utils.constants import *
from ...helpers import refresh_widget, DefaultDisplayWidget, ActionEnum
from ..components.json_viewer import JSONViewerWidget
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
    display_widget_class: str = "submit-display-tab-widget"
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
                "description": "Random pipeline",
                "process_exec_ids": ["PE-123456", "PE-654321"],
                "checkpoint_steps": [0, 1]
            }
            default_json: str = json.dumps(default_dict, indent=4)
            
            refresh_widget(
                self, 
                "display_widget", 
                JSONViewerWidget, 
                self.display_widget_class, 
                submit_url="https://example.com/api/submit", 
                default_json_data=default_json
                )
        elif event.tab.id == "execute_pipeline":
            # Execute pipeline 
            refresh_widget(self, "display_widget", ActionOnWidget, self.display_widget_class, collection_name=COLLECTION_PIPELINES, action=ActionEnum.EXECUTE)
        elif event.tab.id == "delete_pipeline":
            # Delete pipeline
            refresh_widget(self, "display_widget", ActionOnWidget, self.display_widget_class, collection_name=COLLECTION_PIPELINES, action=ActionEnum.DELETE)