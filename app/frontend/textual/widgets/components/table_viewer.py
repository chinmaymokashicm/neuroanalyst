"""
View tabular data
"""
from .....utils.db import find_many_from_db, find_one_from_db
from .....utils.constants import *
from .....utils.exceptions import DBRecordMissing
from .....utils.envs import get_neuroanalyst_root_dirs, set_neuroanalyst_root_dirs
from ...helpers import ActionEnum, APIRouteEnum

import json, re, requests
from typing import Optional
from pathlib import Path, PosixPath

from textual import on, log
from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, TextArea, Select, DataTable
import pyperclip

class TabularData(Widget):
    """
    Widget that loads list of rows from the given API endpoint and displays them in a table.
    """
    
    api_route: APIRouteEnum
    
    def __init__(self, api_route: APIRouteEnum, **kwargs):
        super().__init__(**kwargs)
        self.api_route = api_route
    
    def get_rows_from_db(self) -> list[dict]:
        endpoint: str = f"http://{HOSTNAME}:{PORT}/{self.api_route.value}/all/"
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
    
    def compose(self) -> ComposeResult:
        """
        Compose the widget.
        """
        data_table = DataTable(
            id="data_table",
            show_header=True,
            classes="tabular-data-table",
        )
        data_table.header_height = 3
        rows = self.get_rows_from_db()
        if len(rows) != 0:
            # Convert the dictionary to a list of tuples with the first row as the header and the rest as data
            header = list(rows[0].keys())
            data = [header]
            for row in rows:
                data.append(list(row.values()))
            data_table.add_columns(*data[0])
            data_table.add_rows(data[1:])
        else:
            data_table.add_columns("NO DATA")
            data_table.add_row("No data available")
        yield data_table