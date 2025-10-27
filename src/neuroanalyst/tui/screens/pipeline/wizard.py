"""
Pipeline wizard screen for the NeuroAnalyst TUI application.
This screen guides users through the process of creating a new pipeline.
"""
import sys, asyncio
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))
from neuroanalyst.utils.constants import PATHS
from neuroanalyst.models.pipeline.core import NeuPipeline, ExecutionMode
from neuroanalyst.models.process.process.core import NeuProcess

sys.path.append(str(Path(__file__).resolve().parents[3]))
from tui.components.list import BIDSEntityListComponent, PipelineStepsComponent, PipelineProgressComponent
from tui.utils.data import build_tree
from tui.components.modal import ErrorModal, SuccessModal, InfoModal, LoadingModal

from ..base import BaseScreen

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Header, Footer, Static, Button, Input, Select, 
    TextArea, Label, ProgressBar, ListView, ListItem, Checkbox,
    Tree, DataTable, LoadingIndicator, Digits, Log
)
from textual.reactive import reactive
from textual import on

def read_doc(filename: str) -> str:
    if not filename.endswith(".md"):
        filename += ".md"
    with open(f"text/{filename}", "r") as f:
        return f.read()

INFO_TEXTS: dict[str, str] = {
    "step_1": read_doc("create_pipeline"),
    "step_2": read_doc("review_pipeline"),
    "step_3": read_doc("execute_pipeline"),
}

class PipelineWizardScreen(BaseScreen):
    """Wizard screen for creating or editing a pipeline."""
    
    def __init__(self, pipeline_id: Optional[str] = None):
        """
        If a pipeline_id is provided, the wizard will load the existing pipeline for review in review mode. The wizard will jump straight to Step 2.
        Otherwise, it will create a new pipeline.
        
        If a pipeline_id is not provided, the wizard starts in creation mode.
        Step 1:
            - About the Pipeline: Name, Description, Version, Author
            - Dataset Name: BIDS Dataset to use
            - Starting BIDS Filters: Provide filters to select specific subjects/runs/sessions from the BIDS dataset for the first step.
                NeuroAnalyst will propagate these filters to subsequent steps.
            - Steps - Select number of steps. And for each step, provide:
                - Step Name
                - Step Description
                - Processes to include in the step (multi-select from available processes) with optional extra parameters for each process.
            - Execution Mode: Container or Virtual Environment
            - Scheduler: Select HPC Scheduler if applicable.
            - Starting Scope: Define the initial BIDS scope for the first step.
            - Save the pipeline to disk.
            
        Step 2:
            - Review and confirm the pipeline configuration.
        
        Step 3:
            - The user sees a button to launch the pipeline.
            - The logs from the execution will be streamed in a log area.
            - The status of the pipeline execution will also be live displayed from status.json in the pipeline directory.
        
        """
        super().__init__()
        self.current_step = 1
        self.total_steps = 3
        
        datasets_path = PATHS.datasets
        self.datasets_options = [(str(p.name), str(p)) for p in datasets_path.iterdir() if p.is_dir()]
        
        self.n_pipeline_steps: int = reactive(1)  # Default number of steps
        
        self.pipeline_id: Optional[str] = pipeline_id
        self.pipeline: Optional[NeuPipeline] = NeuPipeline.from_pipeline_id(pipeline_id) if pipeline_id else None
        self.review_mode: bool = True if self.pipeline else False
        
        self.notify(
            "Pipeline Wizard initialized in review mode." if self.review_mode else "Pipeline Wizard initialized in creation mode.",
            severity="info"
        )
        
        # Add attributes for log streaming tasks
        self._pipeline_exec_log_task: Optional[asyncio.Task] = None
        
        # Set variables for BIDS file loading in BIDSEntityListComponent
        self.bids_root: Optional[str] = None
        self.starting_scope: Optional[str] = None

    def compose_content(self) -> ComposeResult:
        """Create the UI layout for the pipeline wizard screen."""
        title = "# Review Pipeline" if self.review_mode else "# Create New Pipeline"
        
        yield Static(title, classes="title")
        yield Static(f"Step {self.current_step} of {self.total_steps}", id="step_indicator", classes="subtitle")
        yield ProgressBar(total=self.total_steps, id="progress")
        
        # Step 1: Basic Information and Save to Disk (initially visible)
        yield Container(
            Horizontal(
                Label("Pipeline Name:"),
                Input(placeholder="Enter pipeline name", id="pipeline_name_input", classes="medium_input"),
                Label("Version:"),
                Input(placeholder="Enter pipeline version", id="pipeline_version_input", classes="small_input"),
                Label("Author:"),
                Input(placeholder="Enter author name", id="pipeline_author_input", classes="medium_input"),
                Label("BIDS Dataset Name:"),
                Select(
                    options=self.datasets_options,
                    prompt="Select BIDS Dataset",
                    type_to_search=True,
                    id="bids_dataset_select",
                    classes="medium_input",
                    ),
                Label("Starting Scope:"),
                Select(
                    [(option, option) for option in ["raw", "derivatives"]],
                    prompt="Select Starting Scope",
                    id="starting_scope_select",
                    classes="medium_input",
                ),
            ),
            Horizontal(
              Label("Number of Steps:"),
              Input(
                  placeholder="Enter number of steps",
                  id="n_steps_input",
                  classes="small_input",
                  type="number",
                  restrict=r"[1-9]*",
                  max_length=1,
                  ),
              Button("Set Steps", id="set_pipeline_steps_btn", variant="primary"),
              PipelineStepsComponent(
                  n_steps=2,
              ),
              Label("Execution Mode:"),
                Select(
                    [(mode.name, mode.value) for mode in ExecutionMode],
                    id="execution_mode_select",
                    prompt="Select Execution Mode",
                    value=ExecutionMode.CONTAINER.value,
                    classes="medium_input",
                ),
                Label("HPC Scheduler:"),
                Select(
                    [(option, option.lower()) for option in ["LOCAL", "SLURM", "PBS", "LSF"]],
                    id="hpc_scheduler_select",
                    prompt="Select HPC Scheduler",
                    value="lsf",
                    classes="medium_input",
                ),
            ),
            Horizontal(
                Label("Description:"),
                TextArea(placeholder="Enter pipeline description", id="pipeline_description_input"),
                Label("Starting BIDS Filters:"),
                BIDSEntityListComponent(
                    bids_root=self.bids_root,
                    scope=self.starting_scope,
                ),
            ),
            id="step_1_container",
            classes="hidden",
        )
        
        yield LoadingIndicator(id="loading_indicator", classes="hidden")
        
        # Step 2: Pipeline Review (initially hidden)
        yield Container(
                Static("Review Pipeline Configuration", classes="subtitle"),
                Horizontal(
                    Label("Name:"),
                    Input(value="", id="pipeline_name_input_review", classes="medium_input", disabled=True),
                    Label("Author:"),
                    Input(value="", id="pipeline_author_input_review", classes="medium_input", disabled=True),
                    Label("Dataset:"),
                    Input(value="", id="bids_dataset_name_input_review", classes="medium_input", disabled=True),
                    Label("Number of Steps:"),
                    Digits(value="", id="n_steps_digits_review", classes="small_input", disabled=True),
                    Label("Parallel Execs per Step:"),
                    Digits(value="", id="n_parallel_execs_digits_review", classes="small_input", disabled=True),
                    Label("HPC Scheduler:"),
                    Input(value="", id="hpc_scheduler_input_review", classes="medium_input", disabled=True),
                ),
                Horizontal(
                    Label("Steps:"),
                    DataTable(id="step_descriptions_table_review", disabled=True, zebra_stripes=True),
                    Label("Description:"),
                    TextArea(text="", id="pipeline_description_input_review", disabled=True),
                ),
                id="step_2_container",
                classes="hidden"
                )
                
        # Step 3: Pipeline Execution (initially hidden)
        yield Container(
            Vertical(
                Static("Execute Pipeline", classes="subtitle"),
                Button("Launch Pipeline", id="launch_pipeline_btn", variant="success"),
                PipelineProgressComponent(pipeline_id=self.pipeline_id) if self.pipeline_id else Static("No pipeline loaded.", classes="subtitle"),
            ),
            Log(id="pipeline_execution_log", classes="log_area hidden"),
            # Log(id="pipeline_execution_log", classes="log_area"),
            id="step_3_container",
            classes="hidden",
        )
            
        # Navigation buttons
        yield Horizontal(
            Button("Previous", id="prev_btn", variant="primary", disabled=True),
            Button("Next", id="next_btn", variant="primary"),
            Button("Cancel", id="cancel_btn", variant="warning"),
            Button("Help", variant="default", id="help_btn"),
        id="wizard_buttons",
        classes="button_row"
        )

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        super().on_mount()
        if not self.pipeline_id:
            # Start in creation mode at Step 1
            self.navigate_to_step(1)
        if self.review_mode and self.pipeline_id:
            # Load the pipeline data based on the selected ID and populate the form fields
            # self.notify("Loading pipeline for review...", severity="info")
            self.navigate_to_step(2)
    
    def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        self._stop_log_streaming()
            
    @on(Select.Changed, "#bids_dataset_select")
    async def on_bids_dataset_changed(self, event: Select.Changed) -> None:
        """Handle changes to the BIDS dataset selection."""
        if event.value == Select.BLANK:
            self.bids_root = None
            self.set_bids_entity_list_component()
            return
        selected_dataset_path: str = event.value
        self.bids_root: str = selected_dataset_path
        try:
            available_scopes = await self.app.push_screen(LoadingModal(
                message="Verifying BIDS dataset and loading available BIDS scopes...",
                function=NeuPipeline.get_available_scopes,
                kwargs={"bids_root": selected_dataset_path}
            ))
            if not available_scopes:
                available_scopes = ["raw", "derivatives"]
        except Exception as e:
            error_str: str = str(e).replace("[", "").replace("]", "").replace("'", "")
            self.app.push_screen(ErrorModal(f"Error loading BIDS dataset:\n{error_str}"))
        starting_scope_select: Select = self.query_one("#starting_scope_select", Select)
        starting_scope_select.options = [(option, option) for option in available_scopes]
        if available_scopes:
            if "raw" in available_scopes:
                starting_scope_select.value = "raw"
                self.starting_scope = "raw"
            else:
                starting_scope_select.value = available_scopes[0]
                self.starting_scope = available_scopes[0]
        else:
            starting_scope_select.value = None
            self.starting_scope = None
        
        self.set_bids_entity_list_component()

    @on(Select.Changed, "#starting_scope_select")
    def on_starting_scope_changed(self, event: Select.Changed) -> None:
        """Handle changes to the starting scope selection."""
        selected_scope: str = event.value
        self.starting_scope = selected_scope
        
        self.set_bids_entity_list_component()
        
    def set_bids_entity_list_component(self) -> None:
        """Set bids_root and scope in BIDSEntityListComponent."""
        bids_entity_component: BIDSEntityListComponent = self.query_one(BIDSEntityListComponent)
        bids_entity_component.bids_root = self.bids_root
        bids_entity_component.scope = self.starting_scope

    @on(Input.Submitted, "#n_steps_input")
    def on_n_steps_submitted(self, event: Input.Submitted) -> None:
        """Handle submission of number of steps input."""
        self.on_set_steps_pressed(Button.Pressed(self.query_one("#set_pipeline_steps_btn", Button)))

    @on(Button.Pressed, "#set_pipeline_steps_btn")
    def on_set_steps_pressed(self, event: Button.Pressed) -> None:
        """Set the number of pipeline steps based on user input."""
        n_steps_input = self.query_one("#n_steps_input", Input)
        try:
            n_steps = int(n_steps_input.value)
            if n_steps < 1:
                raise ValueError("Number of steps must be at least 1.")
            self.n_pipeline_steps = n_steps
            # Re-render the PipelineStepsComponent with the new number of steps
            steps_component = self.query_one(PipelineStepsComponent)
            steps_component.n_steps = n_steps
            steps_component._reset_table()
        except ValueError:
            self.notify("Please enter a valid number of steps (at least 1).", severity="error")

    @on(Button.Pressed, "#next_btn")
    def on_next_btn_pressed(self, event: Button.Pressed) -> None:
        """Handle Next button press."""
        if self.current_step == 1:
            try:
                self.pipeline = self.load_pipeline_from_step_1()
                self.pipeline.create_pipeline_dir()
                self.app.push_screen(SuccessModal("Pipeline created successfully in Step 1. Proceeding to review."))
            except Exception as e:
                # Clean up error string to avoid MarkupError in notify
                error_str: str = str(e).replace("[", "").replace("]", "").replace("'", "")
                self.notify(f"Error in Step 1: {error_str}", severity="error")
                self.app.push_screen(ErrorModal(f"Error in Step 1:\n{error_str}"))
                return
            
            # Populate review fields in Step 2
            self.set_ui_fields_step_2()
            
        # elif self.current_step == 2:
        #     self.notify("Review completed. Proceeding to final step.", severity="info")
            
        
        if self.current_step < self.total_steps:
            self.navigate_to_step(self.current_step + 1)
        else:
            # Final step - save the pipeline
            # self.save_pipeline()
            # self.notify("Pipeline created successfully", severity="success")
            # self.app.push_screen(SuccessModal("Pipeline created successfully."))
            # self.app.pop_screen()
            
            self.notify("Reached the final step of the wizard.", severity="info")
            
            
    @on(Button.Pressed, "#prev_btn")
    def on_prev_btn_pressed(self, event: Button.Pressed) -> None:
        """Handle Previous button press."""
        if self.current_step <= 1:
            return
        
        # Delete the pipeline directory if going back from Step 2 to Step 1 if not in review mode
        if self.current_step == 2 and self.pipeline and not self.review_mode:
            self.pipeline.delete()
            self.pipeline = None
            self.pipeline_id = None
            self.notify("Pipeline data cleared. Returning to Step 1.", severity="info")
        
        self.navigate_to_step(self.current_step - 1)

    @on(Button.Pressed, "#cancel_btn")
    def on_cancel_btn_pressed(self, event: Button.Pressed) -> None:
        """Handle Cancel button press."""
        if not self.review_mode and self.current_step == 2 and self.pipeline:
            # Delete the pipeline directory if cancelling in creation mode at Step 2
            self.pipeline.delete()
            self.notify("Pipeline creation cancelled. Temporary data cleared.", severity="warning")
        self.app.pop_screen()
        
    @on(Button.Pressed, "#help_btn")
    def handle_help_button(self, event: Button.Pressed) -> None:
        """Handle help button press to show info modal."""
        info_text = INFO_TEXTS.get(f"step_{self.current_step}", "No information available for this step.")
        self.app.push_screen(
            InfoModal(
                message=info_text,
            )
        )
    
    @on(Button.Pressed, "#launch_pipeline_btn")
    def on_launch_pipeline_btn_pressed(self, event: Button.Pressed) -> None:
        """Handle Launch Pipeline button press."""
        if not self.pipeline:
            self.notify("No pipeline loaded to execute.", severity="error")
            return
        
        try:
            self.notify("Pipeline execution started.", severity="info")
            # Start streaming the pipeline execution log
            self._start_pipeline_exec_log_streaming()
            # Show the log area
            log_widget = self.query_one("#pipeline_execution_log", Log)
            log_widget.remove_class("hidden")
            
            async def launch_pipeline():
                try:
                    result_msg = await self.pipeline.async_execute_via_python()
                    self.app.push_screen(SuccessModal(result_msg))
                    self.notify("Pipeline execution completed successfully.", severity="success")
                except Exception as e:
                    error_str: str = str(e).replace("[", "").replace("]", "").replace("'", "")
                    self.notify(error_str, severity="error")
                    self.app.push_screen(ErrorModal(f"Error during pipeline execution:\n{error_str}"))

            asyncio.create_task(launch_pipeline())

        except Exception as e:
            error_str: str = str(e).replace("[", "").replace("]", "").replace("'", "")
            self.notify(f"Error launching pipeline: {error_str}", severity="error")
            self.app.push_screen(ErrorModal(f"Error launching pipeline:\n{error_str}"))
    
    def load_pipeline_from_step_1(self) -> NeuPipeline:
        """Retrieve all UI field values from Step 1."""
        # Hide the elements from Step 1
        # step_1_container = self.query_one("#step_1_container", Container)
        # step_1_container.add_class("hidden")
        
        # # Display loading indicator
        # loading_indicator = self.query_one("#loading_indicator", LoadingIndicator)
        # loading_indicator.remove_class("hidden")

        steps: list[tuple[str, str, list[str], dict]] = self.query_one(PipelineStepsComponent).steps
        # Preparing variables for NeuPipeline constructor v2
        steps_info: list[list[str]] = [[step[0], step[1]] for step in steps]
        process_configs: list[list[str | dict]] = [[step[2], step[3]] for step in steps]
        fields = {
            "pipeline_name": self.query_one("#pipeline_name_input", Input).value,
            "pipeline_description": self.query_one("#pipeline_description_input", TextArea).text,
            "pipeline_version": self.query_one("#pipeline_version_input", Input).value,
            "pipeline_author": self.query_one("#pipeline_author_input", Input).value,
            "bids_dataset": self.query_one("#bids_dataset_select", Select).value,
            "starting_bids_filters": self.query_one(BIDSEntityListComponent).bids_entities,
            "starting_scope": self.query_one("#starting_scope_select", Select).value,
            "execution_mode": self.query_one("#execution_mode_select", Select).value,
            "hpc_scheduler": self.query_one("#hpc_scheduler_select", Select).value,
        }
        
        pipeline: NeuPipeline = NeuPipeline.constructor_v2(
            about_pipeline={
                "name": fields["pipeline_name"],
                "description": fields["pipeline_description"],
                "version": fields["pipeline_version"],
                "author": fields["pipeline_author"],
            },
            bids_root=fields["bids_dataset"],
            steps_info=steps_info,
            process_configs=process_configs,
            starting_bids_filters=fields["starting_bids_filters"],
            execution_mode=fields["execution_mode"],
            scheduler=fields["hpc_scheduler"],
            starting_scope=fields["starting_scope"],
        )
        # pipeline: NeuPipeline = NeuPipeline(**args)
        
        # # Hide loading indicator
        # loading_indicator.add_class("hidden")
        
        # # Show the elements for Step 1 again
        # step_1_container.remove_class("hidden")
        
        return pipeline if pipeline else None
    
    def set_ui_fields_step_2(self) -> None:
        """Populate the UI fields in Step 2 for review."""
        if not self.pipeline:
            return
        # Populate basic fields
        n_execs_per_step: int = sum([n_execs for n_execs in self.pipeline.get_pipeline_status().get_stats(by="all")[0].values()])
        
        self.query_one("#n_steps_digits_review", Digits).update(str(len(self.pipeline.steps)))
        self.query_one("#n_parallel_execs_digits_review", Digits).update(str(n_execs_per_step))
        self.query_one("#bids_dataset_name_input_review", Input).value = str(self.pipeline.bids_root.name)
        self.query_one("#pipeline_name_input_review", Input).value = self.pipeline.about.name
        self.query_one("#pipeline_author_input_review", Input).value = self.pipeline.about.author
        self.query_one("#hpc_scheduler_input_review", Input).value = self.pipeline.scheduler
        self.query_one("#pipeline_description_input_review", TextArea).text = self.pipeline.about.description
        
        # Populate steps table
        step_table: DataTable = self.query_one("#step_descriptions_table_review", DataTable)
        step_table.clear(columns=True)
        step_table.add_columns("Step Number", "Step Name", "Process ID", "Process Logic")
        for step_idx, step in enumerate(self.pipeline.steps, start=1):
            unique_process_ids: set[str] = set(process_exec.process.process_id for process_exec in step.process_execs)
            for process_id in unique_process_ids:
                process: NeuProcess = NeuProcess.from_process_id(process_id)
                process_logic_name: str = (
                    process.process_dir.logic.about.name
                    if process.process_dir.logic
                    else "N/A"
                )
                step_table.add_row(
                    str(step_idx),
                    step.name,
                    process_id,
                    process_logic_name
                )
    
    def navigate_to_step(self, step: int) -> None:
        """Navigate to a specific step in the wizard."""
        # Hide all step containers
        for i in range(1, self.total_steps + 1):
            container = self.query_one(f"#step_{i}_container", Container)
            container.add_class("hidden") if i != step else container.remove_class("hidden")
        
        # Update step indicator and progress bar
        self.current_step = step
        self.query_one("#step_indicator", Static).update(f"Step {step} of {self.total_steps}")
        self.query_one("#progress", ProgressBar).update(progress=step)
        
        # Update button states
        prev_btn = self.query_one("#prev_btn", Button)
        next_btn = self.query_one("#next_btn", Button)
        
        prev_btn.disabled = (step == 1)
        next_btn.label = "Finish" if step == self.total_steps else "Next"
        
        if step == 2:
            # Populate review fields in Step 2
            self.set_ui_fields_step_2()
            # Disable previous button in review mode
            if self.review_mode:
                prev_btn.disabled = True
            next_btn.disabled = False

        # Special handling for step transitions
        if step == 3:
            # Update the process order list based on selected processes in step 2
            # self.update_process_order_list()
            next_btn.disabled = True  # Disable Next button on final step
    
    def _start_pipeline_exec_log_streaming(self) -> None:
        """Start streaming logs from the pipeline execution log file."""
        if self._pipeline_exec_log_task:
            self._pipeline_exec_log_task.cancel()
        
        self._pipeline_exec_log_task = asyncio.create_task(
            self._stream_log_file(self.pipeline.log_file_path, "#pipeline_execution_log")
        )
    
    async def _stream_log_file(self, log_path: Path, log_widget_id: str) -> None:
        """Stream contents of a log file to a Log widget."""
        log_widget = self.query_one(log_widget_id, Log)
        
        # Clear existing logs
        log_widget.clear()
        
        # Keep track of file position
        last_position = 0
        
        while True:
            try:
                if log_path.exists():
                    with open(log_path, 'r') as f:
                        # Seek to last position
                        f.seek(last_position)
                        
                        # Read new content
                        new_content = f.read()
                        
                        if new_content:
                            # Split into lines and add each line
                            lines = new_content.split('\n')
                            for line in lines:
                                if line.strip():  # Only add non-empty lines
                                    log_widget.write_line(line)
                        
                        # Update position
                        last_position = f.tell()
                
                # Wait before checking again
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                log_widget.write_line(f"Error reading log: {str(e)}")
                await asyncio.sleep(5)  # Wait longer on error
    
    def _stop_log_streaming(self) -> None:
        """Stop all log streaming tasks."""
        if self._pipeline_exec_log_task:
            self._pipeline_exec_log_task.cancel()
            self._pipeline_exec_log_task = None