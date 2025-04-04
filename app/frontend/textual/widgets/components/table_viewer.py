"""
View tabular data
"""
from .....utils.db import find_many_from_db, find_one_from_db
from .....utils.exceptions import DBRecordMissing
from ...helpers import ActionEnum

import json

from textual import on, log
from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, TextArea, Select, DataTable
import pyperclip

class TabularData(Widget):
    collection_name: str
    
    def __init__(self, collection_name: str, **kwargs):
        super().__init__(**kwargs)
        self.collection_name = collection_name
        # self.data: list[dict] = []
        # self.selected_id: str = ""
    
    def compose(self) -> ComposeResult:
        """
        Compose the widget.
        """
        rows: list[dict] = find_many_from_db(self.collection_name, filter={})
        # Identify columns that have iterable values in any row
        iterable_columns = set()
        for row in rows:
            for key, value in row.items():
                if isinstance(value, (list, dict)):
                    iterable_columns.add(key)
        # Keep only non-iterable columns
        non_iterable_columns = set(rows[0].keys()) - iterable_columns
        rows = [{k: v for k, v in row.items() if k in non_iterable_columns} for row in rows]
        data_table = DataTable(
            id="data_table",
            show_header=True,
            classes="tabular-data-table",
        )
        if len(rows) != 0:
            # Convert the dictionary to a list of tuples with the first row as the header and the rest as data
            header = list(rows[0].keys())
            data = [header]
            for row in rows:
                data.append(list(row.values()))
            data_table.add_columns(*data[0])
            data_table.add_rows(data[1:])
        else:
            log(f"Collection {self.collection_name} is empty.")
        yield data_table