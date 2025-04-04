"""
Action on an item from the database.
"""
from .....utils.db import find_many_from_db, find_one_from_db, check_connection
from .....utils.exceptions import DBRecordMissing, MongoDBConnectionError
from ...helpers import ActionEnum

import json

from textual import on, log
from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, TextArea, Select

class ActionOnWidget(Widget):
    collection_name: str
    action: ActionEnum
    
    def __init__(self, collection_name: str, action: ActionEnum, **kwargs):
        super().__init__(**kwargs)
        self.collection_name = collection_name
        self.action = action
        
    def get_select_options(self) -> list:
        try:
            records: list[dict] = find_many_from_db(self.collection_name, filter={})
        except DBRecordMissing:
            log(f"Collection {self.collection_name} not found.")
            return
        if not records:
            log(f"Collection {self.collection_name} is empty.")
            return
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