"""
Action on an item from the database.
"""
from .....utils.db import find_many_from_db, find_one_from_db, check_connection
from .....utils.constants import *
from .....utils.exceptions import DBRecordMissing, MongoDBConnectionError
from ...helpers import ActionEnum, APIRouteEnum

import json, requests

from textual import on, log
from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, TextArea, Select

class ActionOnWidget(Widget):
    """
    Widget that submits an action on a selected item.
    """
    api_route: APIRouteEnum
    action: ActionEnum
    
    def __init__(self, api_route: APIRouteEnum, action: ActionEnum, **kwargs):
        super().__init__(**kwargs)
        self.api_route = api_route
        self.action = action
        
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
            yield Button(self.action.value.title(), id="action_button", classes="action-button-action")
            yield Button("Copy ID", id="copy_id_button", classes="action-button-copy-id")
            yield Button("Copy JSON", id="copy_json_button", classes="action-button-copy-json")
        yield TextArea(classes="action-textarea", id="action_textarea", read_only=True, language="json")
        
    @on(Select.Changed, "#action_select")
    def update_textarea(self, event: Select.Changed) -> None:
        """
        Update the textarea with the selected item.
        """
        selected_id = event.value
        record: dict = find_one_from_db(self.collection_name, filter={"id": selected_id})
        record_json: str = json.dumps(record, indent=4)
        self.query_one("#action_textarea", TextArea).text = record_json