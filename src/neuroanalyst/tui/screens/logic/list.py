"""
Logic list screen for the NeuroAnalyst TUI application.
"""
# from src.neuroanalyst.models.process.logic import NeuProcessLogic
# Use absolute import by constructing the path properly
from ..base import BaseScreen
from .register import RegisterLogicScreen

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))
from neuroanalyst.models.process.logic.core import NeuProcessLogic

sys.path.append(str(Path(__file__).resolve().parents[3]))
from tui.components.modal import ConfirmModal

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button, ListView, ListItem, DataTable
from textual.screen import Screen
from textual.reactive import reactive
from textual import on


class LogicListScreen(BaseScreen):
    """Screen that displays a list of all available logics."""
    selected_logic_name: reactive[str | None] = reactive(None)
    
    def compose_content(self) -> ComposeResult:
        """Create the UI layout for the logic list screen."""
        yield Static("All Registered Logics", classes="title")
        
        yield DataTable(id="logic_table")
        
        yield Horizontal(
            Button("Refresh", id="refresh_btn", variant="primary"),
            Button("Register New Logic", id="new_logic_btn", variant="success"),
            Button("View Details", id="view_details_btn", variant="primary"),
            Button("Delete Logic", id="delete_logic_btn", variant="error"),
            Button("Delete All Logics", id="delete_all_logics_btn", variant="error"),
            Button("Back", id="back_btn", variant="warning"),
            classes="button_row"
        )
    
    def on_mount(self):
        super().on_mount()
        self.update_logic_table()
        
    def update_logic_table(self) -> None:
        """Refresh the logic data table."""
        table = self.query_one("#logic_table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        
        logics: list[NeuProcessLogic] = NeuProcessLogic.get_all_registered_logics(username=self.app.global_vars.get("username"))
        table.add_columns("Name", "Description", "Author", "Language")
        for logic in logics:
            table.add_row(
                logic.about.name,
                logic.about.description,
                logic.about.author,
                logic.language
            )

    def on_data_table_row_highlighted(self, event: DataTable.RowSelected) -> None:
        """Handle data table row selection."""
        table = self.query_one("#logic_table", DataTable)
        selected_row_key = event.row_key
        selected_logic_name = table.get_row(selected_row_key)[0]
        self.selected_logic_name = selected_logic_name
        # Update the button label
        view_button = self.query_one("#view_details_btn", Button)
        view_button.label = f"View {self.selected_logic_name}"
            
    @on(Button.Pressed, "#refresh_btn")
    def handle_refresh_button(self) -> None:
        """Handle refresh button press."""
        self.update_logic_table()
        self.notify("Logic list refreshed", severity="info")
        
    @on(Button.Pressed, "#new_logic_btn")
    def handle_new_logic_button(self) -> None:
        """Handle new logic button press."""
        self.app.push_screen("register_logic")
        
    @on(Button.Pressed, "#view_details_btn")
    def handle_view_details_button(self) -> None:
        """Handle view details button press."""
        if self.selected_logic_name:
            print(f"Viewing details for logic: {self.selected_logic_name}")
            self.app.push_screen(RegisterLogicScreen(logic_name=self.selected_logic_name))
        
    def confirm_delete_logic(self, result: bool) -> None:
        """Callback to confirm deletion of logic."""
        if result and self.selected_logic_name:
            logic: NeuProcessLogic = NeuProcessLogic.from_func_name(self.selected_logic_name, username=self.app.global_vars.get("username"))
            logic.delete()
            self.notify(f"Logic '{self.selected_logic_name}' deleted", severity="warning")
            self.update_logic_table()
    
    @on(Button.Pressed, "#delete_logic_btn")
    def handle_delete_logic_button(self) -> None:
        """Handle delete logic button press."""
        if self.selected_logic_name:
            self.app.push_screen(
                ConfirmModal(
                    message=f"Are you sure you want to delete logic '{self.selected_logic_name}'?"
                ),
                callback=lambda result: self.confirm_delete_logic(result)
            )
    
    @on(Button.Pressed, "#delete_all_logics_btn")
    def handle_delete_all_logics_button(self) -> None:
        """Handle delete all logics button press."""
        self.app.push_screen(
            ConfirmModal(
                message="Are you sure you want to delete ALL registered logics? This action cannot be undone."
            ),
            callback=lambda result: self.confirm_delete_all_logics(result)
        )
        
    def confirm_delete_all_logics(self, result: bool) -> None:
        """Callback to confirm deletion of all logics."""
        if result:
            all_logics: list[NeuProcessLogic] = NeuProcessLogic.get_all_registered_logics(username=self.app.global_vars.get("username"))
            for logic in all_logics:
                logic.delete()
            self.notify("All registered logics deleted", severity="warning")
            self.update_logic_table()

    @on(Button.Pressed, "#back_btn")
    def handle_back_button(self) -> None:
        """Handle back button press."""
        self.app.pop_screen()