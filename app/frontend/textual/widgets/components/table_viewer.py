"""
View tabular data
"""
from .....utils.db import find_many_from_db, find_one_from_db
from .....utils.constants import *
from .....utils.exceptions import DBRecordMissing
from .....utils.envs import get_neuroanalyst_root_dirs, set_neuroanalyst_root_dirs
from ...helpers import APIActionEnum, APIRouteEnum

import json, re, requests
from typing import Optional
from pathlib import Path, PosixPath

from textual import on, log
from textual.app import ComposeResult, RenderResult
from textual.containers import Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import Button, TextArea, Select, DataTable
import pyperclip

COLUMN_WIDTH: int = 30
ROW_HEIGHT: int = 3

class TabularData(Widget):
    """
    Widget that loads list of rows from the given API endpoint and displays them in a table.
    """
    
    api_route: APIRouteEnum
    
    def __init__(self, api_route: APIRouteEnum, **kwargs):
        super().__init__(**kwargs)
        self.api_route = api_route
    
    def get_rows_from_db(self) -> list[dict]:
        endpoint: str = f"http://{FASTAPI_HOSTNAME}:{FASTAPI_PORT}/{self.api_route.value}/all/"
        rows: list[dict] = []
        try:
            response: requests.Response = requests.get(endpoint, timeout=5)
            if response.status_code != 200:
                self.notify(f"Failed to fetch data: {response.text}", severity="error", title="Error")
                return []
            rows: list[dict] = response.json()
        except requests.RequestException as e:
            self.notify(f"Request failed: {str(e)}", severity="error", title="Error")
            return []
        
        if(len(rows) == 0):
            self.notify(f"Collection {self.api_route.name} is empty.", severity="warning", title="Warning")
            return []
        return rows
    
    def convert_rows_to_data(self, rows: list[dict]) -> tuple[list[str], list[list[str]], bool]:
        """
        Convert rows from the database to a list of lists for the DataTable.
        """
        data = []
        if len(rows) != 0:
            # Convert the dictionary to a list of tuples with the first row as the header and the rest as data
            headers = list(rows[0].keys())
            data = [headers]
            for row in rows:
                data.append(list(row.values()))
            return headers, data, True
        else:
            return ["NO DATA"], [["No data available"]], False
    
    @on(Button.Pressed, "#table_refresh_button")
    def refresh_button(self, event: Button.Pressed):
        """
        Handle the refresh button click event.
        """
        # Refresh the table data
        rows = self.get_rows_from_db()
        headers, data, has_data = self.convert_rows_to_data(rows)
        data_table: DataTable = self.query_one("#data_table")
        data_table.clear(columns=True)
        # data_table.add_columns(*headers)
        for header in headers:
            data_table.add_column(header, width=COLUMN_WIDTH)
        # data_table.add_rows(data[1:])
        for row in data[1:]:
            data_table.add_row(*row, height=ROW_HEIGHT)
        if has_data:
            self.notify("Table data refreshed successfully.", severity="information", title="Success")
        else:
            self.notify("No data available to display.", severity="warning", title="Warning")
    
    def compose(self) -> ComposeResult:
        """
        Compose the widget.
        """
        # Add a refresh button to the top of the table
        vertical_container: Vertical = Vertical(id="table_viewer_container", classes="table-view-container")
        # yield vertical_container
        with vertical_container:
            yield Button("Refresh", id="table_refresh_button", classes="table-refresh-button")
            data_table = DataTable(
                id="data_table",
                show_header=True,
                classes="tabular-data-table",
            )
            data_table.header_height = 3
            rows = self.get_rows_from_db()
            headers, data, has_data = self.convert_rows_to_data(rows)
            data_table.clear(columns=True)
            # data_table.add_columns(*headers)
            for header in headers:
                data_table.add_column(header, width=COLUMN_WIDTH)
            # data_table.add_rows(data[1:])
            for row in data[1:]:
                data_table.add_row(*row, height=ROW_HEIGHT)
            data_table
            if has_data:
                self.notify("Table data loaded successfully.", severity="information", title="Success")
            else:
                self.notify("No data available to display.", severity="warning", title="Warning")
            yield data_table