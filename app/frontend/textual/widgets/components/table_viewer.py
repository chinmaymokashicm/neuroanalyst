"""
View tabular data
"""
from .....utils.db import find_many_from_db, find_one_from_db
from .....utils.exceptions import DBRecordMissing
from .....utils.envs import get_neuroanalyst_root_dirs, set_neuroanalyst_root_dirs
from ...helpers import ActionEnum

import json, re
from typing import Optional
from pathlib import Path, PosixPath

from textual import on, log
from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, TextArea, Select, DataTable
import pyperclip

class TabularData(Widget):
    collection_name: Optional[str] = None
    root_dir: Optional[str] = None
    
    def __init__(self, collection_name: Optional[str] = None, root_dir: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.collection_name = collection_name
        self.root_dir = root_dir
    
    def get_rows_from_db(self) -> list[dict]:
        if self.collection_name is None:
            return []
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
        return rows
    
    def get_subdirs_from_root(self, skip_subdirs: Optional[list[str]] = None) -> list[dict]:
        if skip_subdirs is None:
            skip_subdirs = ["venv*"]
        if self.root_dir is None:
            set_neuroanalyst_root_dirs()
            self.root_dir = get_neuroanalyst_root_dirs("workdir")
        root_dir: PosixPath = Path(self.root_dir)
        if not root_dir.exists():
            return []
        subdirs = []
        for subdir in root_dir.iterdir():
            if subdir.is_dir() and not any(re.match(pattern, subdir.name) for pattern in skip_subdirs):
                subdirs.append({"name": subdir.name, "path": str(subdir)})
        return subdirs
    
    def compose(self) -> ComposeResult:
        """
        Compose the widget.
        """
        data_table = DataTable(
            id="data_table",
            show_header=True,
            classes="tabular-data-table",
        )
        if self.collection_name is not None:
            rows = self.get_rows_from_db()
        else:
            rows = self.get_subdirs_from_root()
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