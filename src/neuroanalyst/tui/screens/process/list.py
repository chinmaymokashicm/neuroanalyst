"""
Process list screen for the NeuroAnalyst TUI application.
"""
import sys
from pathlib import Path
from typing import Optional

from ..base import BaseScreen
from ..process.wizard import ProcessWizardScreen

sys.path.append(str(Path(__file__).resolve().parents[4]))
from neuroanalyst.models.process.dir.core import NeuProcessDir
from neuroanalyst.utils.constants import NeuroAnalystPaths

sys.path.append(str(Path(__file__).resolve().parents[3]))
from tui.components.modal import ConfirmModal
from tui.constants import SCREEN_NAMES

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Header,
    Footer,
    Static,
    Button,
    ListView,
    ListItem,
    DataTable
    )
from textual.screen import Screen
from textual.reactive import reactive
from textual import on

class ProcessListScreen(BaseScreen):
    """Screen that displays a list of all available processes."""
    selected_process_id: reactive[str | None] = reactive(None)
    username: Optional[str] = None

    def compose_content(self):
        yield Static("# Process Management", classes="title")
        
        yield DataTable(id="process_table")
        
        yield Horizontal(
            Button("Refresh", id="refresh_btn", variant="primary"),
            Button("Create New Process", id="new_process_btn", variant="success"),
            Button("View Details", id="view_details_btn", variant="primary"),
            Button("Delete Process", id="delete_process_btn", variant="error"),
            Button("Delete All Processes", id="delete_all_processes_btn", variant="error"),
            Button("Back", id="back_btn", variant="warning"),
            classes="button_row"
        )
    
    def on_mount(self):
        super().on_mount()
        self.update_process_table()
        
    def update_process_table(self) -> None:
        """Refresh the process data table."""
        table = self.query_one("#process_table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        
        process_dirs: list[NeuProcessDir] = NeuProcessDir.get_all_process_dirs(username=self.app.global_vars.get("username"))
        table.add_columns(
            "ID",
            "Logic",
            "Image",
            "Venv",
            "Env Vars",
            "Bind Paths",
            "Command Flags"
        )
        if not process_dirs:
            table.add_row("No processes found", "", "", "", "", "", "")
            return
        paths = NeuroAnalystPaths(username=self.username)
        for process in process_dirs:
            image_exists: bool = (paths.get_process_image_path(process.process_id)).exists()
            venv_exists: bool = (paths.get_venv_path(process.process_id)).exists()
            
            table.add_row(
                process.process_id,
                process.logic.about.name if process.logic else "N/A",
                "YES" if image_exists else "NO",
                "YES" if venv_exists else "NO",
                str(process.config.environment_variables),
                str(process.config.bind_paths),
                str(process.config.command_flags)
            )
    
    def on_data_table_row_highlighted(self, event: DataTable.RowSelected) -> None:
        """Handle data table row selection."""
        table = self.query_one("#process_table", DataTable)
        selected_row_key = event.row_key
        selected_process_id = table.get_row(selected_row_key)[0]
        self.selected_process_id = selected_process_id
        # Update the button label
        view_button = self.query_one("#view_details_btn", Button)
        view_button.label = f"View {self.selected_process_id}"
            
    @on(Button.Pressed, "#refresh_btn")
    def handle_refresh_button(self) -> None:
        """Handle refresh button press."""
        self.update_process_table()
        self.notify("Process list refreshed", severity="info")
        
    @on(Button.Pressed, "#new_process_btn")
    def handle_new_process_button(self) -> None:
        """Handle new process button press."""
        self.app.push_screen(SCREEN_NAMES["process"]["wizard"])
        
    @on(Button.Pressed, "#view_details_btn")
    def handle_view_details_button(self) -> None:
        """Handle view details button press."""
        if self.selected_process_id:
            print(f"Viewing details for process: {self.selected_process_id}")
            self.app.push_screen(ProcessWizardScreen(process_id=self.selected_process_id))
        
    def confirm_delete_process(self, result: bool) -> None:
        """Callback to confirm deletion of process."""
        if result and self.selected_process_id:
            process_dir: NeuProcessDir = NeuProcessDir.from_process_id(self.selected_process_id)
            process_dir.delete()
            
            self.notify(f"Process '{self.selected_process_id}' deleted", severity="warning")
            self.update_process_table()
    
    @on(Button.Pressed, "#delete_process_btn")
    def handle_delete_process_button(self) -> None:
        """Handle delete process button press."""
        if self.selected_process_id:
            self.app.push_screen(
                ConfirmModal(
                    message=f"Are you sure you want to delete process '{self.selected_process_id}'?"
                ),
                callback=lambda result: self.confirm_delete_process(result)
            )
    
    @on(Button.Pressed, "#delete_all_processes_btn")
    def handle_delete_all_processes_button(self) -> None:
        """Handle delete all processes button press."""
        self.app.push_screen(
            ConfirmModal(
                message="Are you sure you want to delete ALL processes and their environments (virtual env or Singularity image) if they exist? This action cannot be undone."
            ),
            callback=lambda result: self.confirm_delete_all_processes(result)
        )
        
    def confirm_delete_all_processes(self, result: bool) -> None:
        """Callback to confirm deletion of all processes."""
        if result:
            paths = NeuroAnalystPaths(username=self.username)
            all_processes: list[NeuProcessDir] = NeuProcessDir.get_all_process_dirs(username=self.app.global_vars.get("username"))
            for process in all_processes:
                process_image_path: Path = paths.get_process_image_path(process.process_id)
                process_venv_path: Path = paths.get_venv_path(process.process_id)
                if process_image_path.exists():
                    process_image_path.unlink()
                if process_venv_path.exists():
                    if process_venv_path.is_dir():
                        for item in process_venv_path.iterdir():
                            if item.is_dir():
                                for subitem in item.iterdir():
                                    if subitem.is_file():
                                        subitem.unlink()
                                item.rmdir()
                            else:
                                item.unlink()
                        process_venv_path.rmdir()
                    else:
                        process_venv_path.unlink()
                process.delete()
            self.notify("All process directories deleted", severity="warning")
            self.update_process_table()

    @on(Button.Pressed, "#back_btn")
    def handle_back_button(self) -> None:
        """Handle back button press."""
        self.app.pop_screen()