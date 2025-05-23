"""
Action on an item from the database.
"""
from .....utils.db import find_many_from_db, find_one_from_db, check_connection
from .....utils.constants import *
from .....utils.exceptions import DBRecordMissing, MongoDBConnectionError
from ...helpers import APIActionEnum, APIRouteEnum

import json, requests
from typing import Optional

from textual import on, log
from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, TextArea, Select
import pyperclip

class ActionOnWidget(Widget):
    """
    Widget that submits an action on a selected item.
    """
    api_route: APIRouteEnum
    action: Optional[APIActionEnum] = None
    view_only: bool = False
    
    def __init__(self, api_route: APIRouteEnum, action: Optional[APIActionEnum] = None, view_only: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.api_route = api_route
        self.action = action
        self.view_only = view_only
        
    def get_select_options(self) -> list:
        endpoint: str = f"http://{FASTAPI_HOSTNAME}:{FASTAPI_PORT}/{self.api_route.value}/all/"
        records: list[dict] = []
        try:
            response: requests.Response = requests.get(endpoint, timeout=5)
            if response.status_code not in [200, 201]:
                log(f"Failed to fetch data: {response.text}")
                self.notify(f"Failed to fetch data: {response.text}", severity="error", title="Error")
                return []
            records: list[dict] = response.json()
        except requests.RequestException as e:
            log(f"Request failed: {str(e)}")
            self.notify(f"Request failed: {str(e)}", severity="error", title="Error")
            return []
        if not records:
            log(f"Collection {self.api_route.name} is empty.")
            self.notify(f"Collection {self.api_route.name} is empty.", severity="warning", title="Warning")
            return []
        options = []
        if len(records) > 0:
            try:
                pyperclip.copy(records[0])
            except Exception as e:
                self.notify(f"Failed to copy: {e}")
            if "name" not in records[0]:
                options: list[tuple[str, str]] = [(f"{record['id']}", record['id']) for record in records]
            else:
                options: list[tuple[str, str]] = [(f"{record['id']} : {record['name']}", record['id']) for record in records]
        return options
    
    def compose(self) -> ComposeResult:
        """
        Compose the widget.
        """
        with Horizontal(classes="action-item-choose"):
            yield Select(id="action_select", options=self.get_select_options(), classes="action-select", type_to_search=True)
            if not self.view_only:
                yield Button(self.action.value.title(), id="action_button", classes="action-button-action")
            yield Button("Copy ID", id="copy_id_button", classes="action-button-copy-id")
            yield Button("Copy JSON", id="copy_json_button", classes="action-button-copy-json")
        yield TextArea(classes="action-textarea", id="action_textarea", read_only=True, language="json")
        
    @on(Button.Pressed, "#copy_id_button")
    def copy_id(self, event: Button.Pressed) -> None:
        """
        Copy the selected ID to the clipboard.
        """
        try:
            selected_id = self.query_one("#action_select", Select).value
            pyperclip.copy(selected_id)
            self.notify(f"ID {selected_id} copied to clipboard.", severity="information", title="Copy ID")
        except Exception as e:
            log(f"Error copying ID: {str(e)}")
            self.notify(f"Error copying ID: {str(e)}", severity="error", title="Error")
            return
        
    @on(Button.Pressed, "#copy_json_button")
    def copy_json(self, event: Button.Pressed) -> None:
        """
        Copy the selected JSON to the clipboard.
        """
        try:
            # Get text from the textarea
            json_text = self.query_one("#action_textarea", TextArea).text
            pyperclip.copy(json_text)
            self.notify("JSON copied to clipboard.", severity="information", title="Copy JSON")
        except Exception as e:
            log(f"Error copying JSON: {str(e)}")
            self.notify(f"Error copying JSON: {str(e)}", severity="error", title="Error")
            return
    
    @on(Select.Changed, "#action_select")
    def update_textarea(self, event: Select.Changed) -> None:
        """
        Update the textarea with the selected item.
        """
        selected_id = event.value
        # Get one record from the database by ID
        endpoint: str = f"http://{FASTAPI_HOSTNAME}:{FASTAPI_PORT}/{self.api_route.value}/id/{selected_id}/"
        try:
            response: requests.Response = requests.get(endpoint)
            record: dict = response.json()
            self.query_one("#action_textarea", TextArea).text = json.dumps(record, indent=4)
        except requests.RequestException as e:
            log(f"Request failed: {str(e)}")
            self.notify(f"Request failed: {str(e)}", severity="error", title="Error")
            return
        except json.JSONDecodeError as e:
            log(f"Error decoding JSON: {str(e)}")
            self.notify(f"Error decoding JSON: {str(e)}", severity="error", title="Error")
            return
        except Exception as e:
            log(f"Error: {str(e)}")
            self.notify(f"Error: {str(e)}", severity="error", title="Error")
            return
        
    @on(Button.Pressed, "#action_button")
    def action_button(self, event: Button.Pressed) -> None:
        """
        Handle the action button click event.
        """
        selected_id = self.query_one("#action_select", Select).value
        if not selected_id:
            self.notify("No item selected.", severity="error", title="Error")
            return
        
        # Perform the action on the selected item
        endpoint: str = f"http://{FASTAPI_HOSTNAME}:{FASTAPI_PORT}/{self.api_route.value}/{self.action.value}/{selected_id}/"
        try:
            response: requests.Response = requests.post(endpoint)
            if response.status_code not in [200, 201]:
                log(f"Failed to {self.action.value}: {response.text}")
                self.notify(f"Failed to {self.action.value}: {response.text}", severity="error", title="Error")
                try:
                    pyperclip.copy(response.json())
                except Exception as e:
                    self.notify(f"Failed to copy: {e}")
                return
            self.notify(f"{self.action.value} performed successfully.", severity="information", title="Success")
        except requests.RequestException as e:
            log(f"Request failed: {str(e)}")
            pyperclip.copy(str(e))
            self.notify(f"Request failed: {str(e)}", severity="error", title="Error")
            return