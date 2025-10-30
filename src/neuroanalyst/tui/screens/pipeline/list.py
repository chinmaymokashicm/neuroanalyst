"""
Pipeline list screen for the NeuroAnalyst TUI application.
"""
import sys
from pathlib import Path

from ..base import BaseScreen
# from ..process.wizard import ProcessWizardScreen
from ..pipeline.wizard import PipelineWizardScreen

sys.path.append(str(Path(__file__).resolve().parents[4]))
from neuroanalyst.models.pipeline.core import NeuPipeline

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

class PipelineListScreen(BaseScreen):
    """Screen that displays a list of all available pipelines."""
    selected_pipeline_id: reactive[str | None] = reactive(None)

    def compose_content(self):
        yield Static("# Pipeline Management", classes="title")
        
        yield DataTable(id="pipeline_table")
        
        yield Horizontal(
            Button("Refresh", id="refresh_btn", variant="primary"),
            Button("Create New Pipeline", id="new_pipeline_btn", variant="success"),
            Button("View Details", id="view_details_btn", variant="primary"),
            Button("Delete Pipeline", id="delete_pipeline_btn", variant="error"),
            Button("Delete All Pipelines", id="delete_all_pipelines_btn", variant="error"),
            Button("Back", id="back_btn", variant="warning"),
            classes="button_row"
        )
    
    def on_mount(self):
        super().on_mount()
        self.update_pipeline_table()
        
    def update_pipeline_table(self) -> None:
        """Refresh the pipeline data table."""
        table = self.query_one("#pipeline_table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        
        pipelines: list[NeuPipeline] = NeuPipeline.get_all_pipelines(username=self.app.global_vars.get("username"))
        table.add_columns(
            "ID",
            "Directory Name",
            "Name",
            "Author",
            "Number of Steps",
            "Scheduler",
            # "Start from Raw Data",
            "Ready for Execution"
        )
        if not pipelines:
            # table.add_row("No pipelines found ", "", "", "", "", "", "", "")
            table.add_row("No pipelines found ", "", "", "", "", "", "")
            return
        for pipeline in pipelines:
            table.add_row(
                pipeline.pipeline_id,
                pipeline.bids_root.name,
                pipeline.about.name if pipeline.about else "N/A",
                pipeline.about.author if pipeline.about else "N/A",
                str(len(pipeline.steps)) if pipeline.steps else "0",
                pipeline.scheduler,
                # "YES" if pipeline.start_from_raw_bids else "NO",
                "YES" if not pipeline.get_missing_configs() else "NO"
            )
    
    def on_data_table_row_highlighted(self, event: DataTable.RowSelected) -> None:
        """Handle data table row selection."""
        table = self.query_one("#pipeline_table", DataTable)
        selected_row_key = event.row_key
        selected_pipeline_id = table.get_row(selected_row_key)[0]
        self.selected_pipeline_id = selected_pipeline_id
        # Update the button label
        view_button = self.query_one("#view_details_btn", Button)
        view_button.label = f"View {self.selected_pipeline_id}"
            
    @on(Button.Pressed, "#refresh_btn")
    def handle_refresh_button(self) -> None:
        """Handle refresh button press."""
        self.update_pipeline_table()
        self.notify("Pipeline list refreshed", severity="info")
        
    @on(Button.Pressed, "#new_pipeline_btn")
    def handle_new_pipeline_button(self) -> None:
        """Handle new pipeline button press."""
        self.app.push_screen(SCREEN_NAMES["pipeline"]["wizard"])
        
    @on(Button.Pressed, "#view_details_btn")
    def handle_view_details_button(self) -> None:
        """Handle view details button press."""
        if self.selected_pipeline_id:
            print(f"Viewing details for pipeline: {self.selected_pipeline_id}")
            self.app.push_screen(PipelineWizardScreen(pipeline_id=self.selected_pipeline_id))
        
    def confirm_delete_pipeline(self, result: bool) -> None:
        """Callback to confirm deletion of pipeline."""
        if result and self.selected_pipeline_id:
            pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(self.selected_pipeline_id)
            pipeline.delete()
            
            self.notify(f"Pipeline '{self.selected_pipeline_id}' deleted", severity="warning")
            self.update_pipeline_table()
    
    @on(Button.Pressed, "#delete_pipeline_btn")
    def handle_delete_pipeline_button(self) -> None:
        """Handle delete pipeline button press."""
        if self.selected_pipeline_id:
            self.app.push_screen(
                ConfirmModal(
                    message=f"Are you sure you want to delete pipeline '{self.selected_pipeline_id}'?"
                ),
                callback=lambda result: self.confirm_delete_pipeline(result)
            )

    @on(Button.Pressed, "#delete_all_pipelines_btn")
    def handle_delete_all_pipelines_button(self) -> None:
        """Handle delete all pipelines button press."""
        self.app.push_screen(
            ConfirmModal(
                message="Are you sure you want to delete ALL pipelines? This action cannot be undone."
            ),
            callback=lambda result: self.confirm_delete_all_pipelines(result)
        )
        
    def confirm_delete_all_pipelines(self, result: bool) -> None:
        """Callback to confirm deletion of all pipelines."""
        if result:
            all_pipelines: list[NeuPipeline] = NeuPipeline.get_all_pipelines(username=self.app.global_vars.get("username"))
            for pipeline in all_pipelines:
                pipeline.delete(delete_execs=True)
            self.notify("All pipelines deleted", severity="warning")
            self.update_pipeline_table()

    @on(Button.Pressed, "#back_btn")
    def handle_back_button(self) -> None:
        """Handle back button press."""
        self.app.pop_screen()