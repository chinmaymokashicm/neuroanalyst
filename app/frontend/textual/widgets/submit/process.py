from .....utils.constants import *
from .....models.core.process.execute import ProcessExecConfig
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

class SubmitProcess(Widget):
    """
    Widget that handles all submit actions for processes.
    Layout:
    - Tabs for different actions (create, execute, delete)
    - Widget dependent on the selected action
    """
    tabs: Tabs
    display_widget_class: str = "submit-display-tab-widget"
    display_widget: Widget = DefaultDisplayWidget()
    
    def compose(self) -> ComposeResult:
        yield Tabs(
            Tab("Create Process Image", id="create_process"),
            Tab("Execute Process Image", id="execute_process"),
            Tab("Delete Process Image", id="delete_process"),
            Tab("Delete Process Exec", id="delete_process_exec"),
        )
        yield self.display_widget
        
    @on(Tabs.TabActivated)
    def on_tab_activated(self, event: Tabs.TabActivated) -> None:
        """
        Handle the tab activated event.
        """
        if event.tab.id == "create_process":
            # Create a random input for ProcessImageApptainer.from_user() classmethod
            working_directory: dict = {
                "process_workdir_name": "random_process", 
                "main_file": "main.py", 
                "requirements_file": "install_requirements.sh", 
                "main_exec_prefix": "python", 
                "requirements_exec_prefix": "bash"
            }
            process_image_dict: dict = {
                "name": "random_process",
                "tag": "randomprocess",
                "author": "Chinmay Mokashi",
                "description": "Random process image",
                "base_docker_image": "python:3.12",
                "working_directory": working_directory,
                "container_volumes": {
                    "data_dir": "/bids_dir/"
                    },
                "environment_variables": DEFAULT_CONTAINER_ENVS
            }
            default_json: str = json.dumps(process_image_dict, indent=4)
            refresh_widget(self, "display_widget", JSONViewerWidget, self.display_widget_class, submit_url="https://example.com/api/submit", default_json_data=default_json)
        elif event.tab.id == "execute_process":
            default_dict: dict = {
                "process_exec_config": ProcessExecConfig().model_dump(),
                "process_image_id": "PR-00000"
            }
            default_json: str = json.dumps(default_dict, indent=4)
            refresh_widget(self, "display_widget", JSONViewerWidget, self.display_widget_class, submit_url="https://example.com/api/submit", default_json_data=default_json)
        elif event.tab.id == "delete_process":
            refresh_widget(self, "display_widget", ActionOnWidget, self.display_widget_class, collection_name=COLLECTION_PROCESS_IMAGES, action=ActionEnum.DELETE)
        elif event.tab.id == "delete_process_exec":
            refresh_widget(self, "display_widget", ActionOnWidget, self.display_widget_class, collection_name=COLLECTION_PROCESS_EXECS, action=ActionEnum.DELETE)