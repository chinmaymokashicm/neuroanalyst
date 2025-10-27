"""
Process wizard screen for the NeuroAnalyst TUI application.
This screen guides users through the process of creating a new process.
"""
import sys
from pathlib import Path
import asyncio
import os

sys.path.append(str(Path(__file__).resolve().parents[4]))
from neuroanalyst.models.process.dir.core import NeuProcessDir
from neuroanalyst.models.process.logic.core import NeuProcessLogic
from neuroanalyst.utils.constants import PATHS

sys.path.append(str(Path(__file__).resolve().parents[3]))
from tui.components.list import MultiParameterListComponent
from tui.components.modal import InfoModal, ConfirmModal
from tui.constants import SCREEN_NAMES

from ..base import BaseScreen

from typing import Optional, Literal

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Header,
    Footer,
    Static,
    Button,
    Input,
    Select,
    TextArea,
    Label,
    ProgressBar,
    Switch,
    Tree,
    ListView,
    ListItem,
    Log,
    )
from textual.screen import Screen
from textual import on
from textual.reactive import reactive

def read_doc(filename: str) -> str:
    if not filename.endswith(".md"):
        filename += ".md"
    with open(f"text/{filename}", "r") as f:
        return f.read()

INFO_TEXTS: dict[str, str] = {
    "step_1": read_doc("create_process"),
    "step_2": read_doc("review_process"),
    "step_3": read_doc("build_process"),
}

def get_all_logic_options() -> list[tuple[str, str]]:
    """Retrieve all registered NeuProcessLogic instances as options."""
    all_logics: list[NeuProcessLogic] = NeuProcessLogic.get_all_registered_logics()
    return [(logic.about.name, logic.about.name) for logic in all_logics]

class ProcessWizardScreen(BaseScreen):
    """Wizard screen for creating or editing a process."""
    bootstrap_method: reactive[Literal["docker", "localimage"]] = reactive("localimage")
    
    CSS = """
    #base_image_container {
        # Remove padding and margin to fit better
        padding: 0;
    }
    """

    def __init__(self, process_id: Optional[str] = None):
        """
        If a process_id is provided, the wizard will load the existing process for editing.
        Otherwise, it will create a new process.
        
        If process_id is not provided, the wizard starts in creation mode.
        Step 1:
            - The first logic from the registered logics will be selected by default.
            - The code area will be populated with the corresponding logic code.
            - A process directory will be initialized under the selected logic. The process directory parameters will be populated in their fields.
            - Every time the user chooses a different logic, a new process directory will be initialized (but not created on disk yet).
            - The user clicks continue to go to the next step. The process directory is now created on disk.
        
        If process_id is provided, the wizard starts from Step 2 in review mode.
        
        Step 2:
            - The user reviews the process directory parameters. If not satisfied, goes back to Step 1 to change logic or parameters (only if in edit mode), and recreate the process directory on disk.
            - The user clicks continue to go to the next step.
        
        Step 3:
            - The user sees two options - to build a Singularity image, or to create a virtual environment.
            - If either of them already created, the option to build is disabled.
            - The logs from the build will be displayed in a log area. The latest logs will be shown at the bottom with auto-scrolling.
        """
        
        super().__init__()
        
        # Add attributes for log streaming
        self._image_log_task = None
        self._venv_log_task = None
        
        self.current_step = 1
        self.review_mode: bool = False
        self.total_steps = 3
        
        self.process_dir: Optional[NeuProcessDir] = None
        logic_select_options = get_all_logic_options()
        self.logic_select = Select(
            logic_select_options,
            id="logic_select",
            prompt="Select Logic to Build Process",
            type_to_search=True
        )
        
        try:
            print(f"Loading existing process with ID: {process_id}")
            self.process_dir= NeuProcessDir.from_process_id(process_id)
            self.logic_name = self.process_dir.logic.about.name
            self.review_mode = True
            self.current_step = 2
            # self.navigate_to_step(2)
        except Exception as e:
            print(f"Initializing new process wizard: {str(e)}")
            self.logic_name = ""
            # self.navigate_to_step(1)
            
        print(self.review_mode, self.current_step)
            
    def on_mount(self):
        super().on_mount()
        
        if self.review_mode and self.process_dir:
            self.set_ui_fields_for_step_2()
            self.set_ui_fields_for_step_3()
            self.navigate_to_step(2)
            
        else:
            self.navigate_to_step(1)

    @on(Select.Changed, "#logic_select")
    def handle_logic_selection(self, event: Select.Changed) -> None:
        """Handle logic selection changes."""
        selected_logic_name = event.value
        try:
            logic: NeuProcessLogic = NeuProcessLogic.from_func_name(selected_logic_name)
            self.logic_name = logic.about.name
        except Exception:
            self.logic_name = ""
        if self.logic_name:
            self.query_one("#logic_code_input", TextArea).text = logic.code
            self.query_one("#next_btn", Button).disabled = False
            self.initialize_process_dir(logic)
        else:
            self.query_one("#logic_code_input", TextArea).text = "Logic not found."
            self.query_one("#next_btn", Button).disabled = True
            
    @on(Select.Changed, "#bootstrap_method_select")
    def handle_bootstrap_method_change(self, event: Select.Changed) -> None:
        """Handle bootstrap method selection changes."""
        self.bootstrap_method = event.value
        self.update_base_image_component()
        
    @on(Button.Pressed, "#help_btn")
    def handle_help_button(self, event: Button.Pressed) -> None:
        """Handle help button press to show info modal."""
        info_text = INFO_TEXTS.get(f"step_{self.current_step}", "No information available for this step.")
        self.app.push_screen(
            InfoModal(
                message=info_text,
            )
        )
    
    @on(Button.Pressed, "#next_btn")
    def handle_next_button(self, event: Button.Pressed) -> None:
        """Handle next button press events."""
        if self.current_step == 1:
            # Create the process directory on disk
            self.create_process_dir_on_disk()
        elif self.current_step == 2:
            pass
        
        self.navigate_to_step(self.current_step + 1)
        
    @on(Button.Pressed, "#prev_btn")
    def handle_prev_button(self, event: Button.Pressed) -> None:
        """Handle previous button press events."""
        if self.current_step == 2:
            # Going back to step 1, delete the process directory from disk
            if self.process_dir:
                self.process_dir.delete()
        self.navigate_to_step(self.current_step - 1)
        
    @on(Button.Pressed, "#cancel_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        """Handle cancel button press events."""
        if self.current_step in {2, 3} and not self.review_mode:
            # If cancelling from step 2 or 3, delete the process directory from disk if it was created in step 1
            self.process_dir.delete()
            self.app.notify("Process creation cancelled. Temporary process directory deleted.", severity="warning")
        self.reset_wizard()
        self.app.push_screen(SCREEN_NAMES["process"]["list"]) # Pop back to the main screen
        
    @on(Button.Pressed, "#save_exit_btn")
    def handle_save_exit_button(self, event: Button.Pressed) -> None:
        """Handle save and exit button press events."""
        if self.current_step == 1:
            # Create the process directory on disk
            self.create_process_dir_on_disk()
        elif self.current_step == 2:
            pass
        
        self.notify("Process saved successfully", severity="success")
        self.reset_wizard()
        self.app.push_screen(SCREEN_NAMES["process"]["list"]) # Pop back to the main screen
        
    def reset_wizard(self) -> None:
        """Reset the wizard to its initial state."""
        self.current_step = 1
        self.navigate_to_step(1)
        self.process_dir = None
        self.logic_name = ""
        self.query_one("#logic_select", Select).clear()
        self.query_one("#logic_code_input", TextArea).text = ""
        self.query_one("#next_btn", Button).disabled = True

    def initialize_process_dir(self, logic: NeuProcessLogic) -> None:
        """Initialize the process directory based on the selected logic."""
        self.process_dir = NeuProcessDir.from_logic(logic)
        process_id: str = self.process_dir.process_id
        bootstrap_method: Literal["docker", "localimage"] = self.process_dir.config.bootstrap_method
        base_image: str = self.process_dir.config.base_image
        parallel_exec: bool = self.process_dir.config.parallel_execution
        max_workers: Optional[int] = self.process_dir.config.max_workers
        bids_validate: bool = self.process_dir.config.bids_validate
        python_packages: list[str] = self.process_dir.config.language_packages.get("python", [])
        system_packages: list[str] = self.process_dir.config.system_packages
        env_vars: list[str] = self.process_dir.config.environment_variables
        binds: list[str] = self.process_dir.config.bind_paths
        command_flags: list[str] = self.process_dir.config.command_flags
        
        # Set the fields in the UI
        self.query_one("#process_id_input", Input).value = process_id
        self.query_one("#bootstrap_method_select", Select).value = bootstrap_method
        self.query_one("#parallel_switch", Switch).value = parallel_exec
        if max_workers is not None:
            self.query_one("#max_workers_input", Input).value = str(max_workers)
        self.query_one("#bids_validate_switch", Switch).value = bids_validate
        multi_param_component: MultiParameterListComponent = self.query_one(MultiParameterListComponent)
        multi_param_component.categories = {
            "Python Packages": python_packages,
            "System Packages": system_packages,
            "Environment Variables": env_vars,
            "Binds": binds,
            "Command Flags": command_flags
        }
        multi_param_component._update_tree_view()
    
    def get_base_image_component(self, bootstrap_method: Literal["docker", "localimage"]) -> Input | Select:
        """Return the appropriate base image component based on the bootstrap method."""
        if bootstrap_method == "localimage":
            options: list[tuple[str, str]] = [
                (img.name, str(img)) for img in PATHS.base_images.iterdir() if img.is_file() and img.suffix in {".sif", ".img"}
            ]
            if not options:
                self.app.notify(f"No local base images found at {PATHS.base_images} . Please add images to proceed.", severity="error")
            return Select(
                options,
                id="base_image_select",
                prompt="Select Base Image",
                type_to_search=True
            )
        else:
            return Input(placeholder="Enter base docker image", id="base_image_input")
    
    def update_base_image_component(self) -> None:
        """Update the base image component based on the bootstrap method."""
        container = self.query_one("#base_image_container", Container)
        
        # Remove existing component
        container.remove_children()
        
        # Add new component based on bootstrap method
        new_component = self.get_base_image_component(self.bootstrap_method)
        container.mount(new_component)
        
    def get_base_image_value(self) -> str:
        """Retrieve the value of the base image input/select."""
        if self.bootstrap_method == "localimage":
            select_widget = self.query_one("#base_image_select", Select)
            return select_widget.value or ""
        else:
            input_widget = self.query_one("#base_image_input", Input)
            return input_widget.value or ""
        
    def update_process_dir_from_ui(self) -> None:
        # Update process_dir config based on current UI values
        self.process_dir.config.bootstrap_method = self.bootstrap_method
        self.process_dir.config.base_image = self.get_base_image_value()
        self.process_dir.config.parallel_execution = self.query_one("#parallel_switch", Switch).value
        max_workers_input = self.query_one("#max_workers_input", Input).value
        self.process_dir.config.max_workers = int(max_workers_input) if max_workers_input.isdigit() else None
        self.process_dir.config.bids_validate = self.query_one("#bids_validate_switch", Switch).value
        multi_param_component: MultiParameterListComponent = self.query_one(MultiParameterListComponent)
        self.process_dir.config.language_packages["python"] = multi_param_component.categories.get("Python Packages", [])
        self.process_dir.config.system_packages = multi_param_component.categories.get("System Packages", [])
        self.process_dir.config.environment_variables = multi_param_component.categories.get("Environment Variables", [])
        self.process_dir.config.bind_paths = multi_param_component.categories.get("Binds", [])
        self.process_dir.config.command_flags = multi_param_component.categories.get("Command Flags", [])
        
    def set_ui_fields_for_step_2(self) -> None:
        if self.process_dir:
                self.query_one("#review_process_id_input", Input).value = self.process_dir.process_id
                self.query_one("#review_logic_name_input", Input).value = self.process_dir.logic.about.name
                self.query_one("#review_bootstrap_method_input", Input).value = self.process_dir.config.bootstrap_method
                self.query_one("#review_base_image_input", Input).value = self.process_dir.config.base_image
                self.query_one("#review_author_input", Input).value = self.process_dir.logic.about.author
                self.query_one("#review_build_script_input", Input).value = str(Path(self.process_dir.script_paths["build"]["image"]).relative_to(PATHS.workdir)) or ""
                self.query_one("#review_venv_build_script_input", Input).value = str(Path(self.process_dir.script_paths["build"]["venv"]).relative_to(PATHS.workdir)) or ""
                self.query_one("#review_env_vars_input", TextArea).text = "\n".join(self.process_dir.config.environment_variables)
                self.query_one("#review_binds_input", TextArea).text = "\n".join(self.process_dir.config.bind_paths)
                self.query_one("#review_command_flags_input", TextArea).text = "\n".join(self.process_dir.config.command_flags)
                self.query_one("#review_system_packages_input", TextArea).text = "\n".join(self.process_dir.config.system_packages)
                self.query_one("#review_python_packages_input", TextArea).text = "\n".join(self.process_dir.config.language_packages.get("python", []))
                self.query_one("#review_working_dir_input", Input).value = str(self.process_dir.working_dir.relative_to(PATHS.home))
                
    def set_ui_fields_for_step_3(self) -> None:
        if self.process_dir:
            build_image_btn = self.query_one("#build_image_btn", Button)
            build_venv_btn = self.query_one("#build_venv_btn", Button)
            
            # Check if builds exist
            image_exists: bool = Path(PATHS.images / f"{self.process_dir.process_id}.sif").exists()
            venv_exists: bool = Path(PATHS.venvs / self.process_dir.process_id).exists()
            
            if image_exists:
                build_image_btn.disabled = True
                build_image_btn.label = "Singularity Image Built"
            else:
                build_image_btn.disabled = False
                build_image_btn.label = "Build Singularity Image"
                
            if venv_exists:
                build_venv_btn.disabled = True
                build_venv_btn.label = "Virtual Environment Created"
            else:
                build_venv_btn.disabled = False
                build_venv_btn.label = "Build Virtual Environment"
            
            # Initialize log viewers
            image_log = self.query_one("#image_log_viewer", Log)
            venv_log = self.query_one("#venv_log_viewer", Log)
            
            image_log.clear()
            venv_log.clear()
            
            # Show existing logs if they exist
            if self.process_dir.build_image_log_path.exists():
                try:
                    with open(self.process_dir.build_image_log_path, 'r') as f:
                        for line in f:
                            if line.strip():
                                image_log.write_line(line.rstrip())
                except Exception as e:
                    image_log.write_line(f"Error reading existing log: {str(e)}")
            
            if self.process_dir.build_venv_log_path.exists():
                try:
                    with open(self.process_dir.build_venv_log_path, 'r') as f:
                        for line in f:
                            if line.strip():
                                venv_log.write_line(line.rstrip())
                except Exception as e:
                    venv_log.write_line(f"Error reading existing log: {str(e)}")
    
    def create_process_dir_on_disk(self) -> None:
        if not self.process_dir:
            self.app.notify("Process directory is not initialized.", severity="error")
            return
        self.update_process_dir_from_ui()
        self.process_dir.generate()

    def compose_content(self) -> ComposeResult:
        """Create the UI layout for the process wizard screen."""
        title = "Review Process" if self.review_mode else "Create New Process"
        
        yield Static(title, classes="title")
        yield Static(f"Step {self.current_step} of {self.total_steps}", id="step_indicator", classes="subtitle")
        yield ProgressBar(total=self.total_steps, id="progress")
        
        # Step 1: Initialize and Create Process Directory
        yield Container(
            Horizontal(
                Vertical(
                    Label("Logic Name:"),
                    self.logic_select,
                    Label("Python Code:"),
                    TextArea(
                        placeholder="Enter Python code for the logic",
                        id="logic_code_input",
                        language="python"
                    ),
                    id="logic_code_container"
                ),
                Vertical(
                    Horizontal(
                        Label("Process ID:"),
                        Input(placeholder="N/A", id="process_id_input", disabled=True),
                        Label("Bootstrap Method:"),
                        Select(
                            [("docker", "docker"), ("localimage", "localimage")],
                            id="bootstrap_method_select",
                            value="localimage"
                        ),
                        Label("Base Image:"),
                        Container(id="base_image_container"),
                        id="process_basic_info_container",
                    ),
                    Horizontal(
                        Label("Parallel Execution:"),
                        Switch(id="parallel_switch"),
                        Input(placeholder="N_WORKERS", id="max_workers_input", type="integer", max_length=1),
                        Label("BIDS Validation:"),
                        Switch(id="bids_validate_switch"),
                        id="process_options_container",
                    ),
                    MultiParameterListComponent(
                        title="Add Parameters to Process",
                        categories={
                            "Python Packages": [],
                            "System Packages": [],
                            "Environment Variables": [],
                            "Binds": [],
                            "Command Flags": []
                        },
                    ),
                    id="process_details_container",
                ),
                id="logic_form_container",
            ),
            id="step_1_container",
            classes="hidden"
        )
            
        # # Step 2: Process Directory Review (initially hidden)
        yield Container(
            Label("Review the process directory parameters and modify them if needed."),
            Horizontal(
                Label("ID"),
                Input(disabled=True, id="review_process_id_input"),
                Label("Author"),
                Input(disabled=True, id="review_author_input", classes="medium_input"),
                Label("Logic Name"),
                Input(disabled=True, id="review_logic_name_input"),
                id="review_basic_info_container",
            ),
            Horizontal(
                Label("Bootstrap Method"),
                Input(disabled=True, id="review_bootstrap_method_input"),
                Label("Base Image"),
                Input(disabled=True, id="review_base_image_input"),
                Label("Image Build Script"),
                Input(disabled=True, id="review_build_script_input", classes="long_input"),
                Label("Venv Build Script"),
                Input(disabled=True, id="review_venv_build_script_input", classes="long_input"),
                Label("Working Directory"),
                Input(disabled=True, id="review_working_dir_input", classes="long_input"),
                id="review_image_info_container",
            ),
            Horizontal(
                Label("Environment Variables"),
                TextArea(disabled=True, id="review_env_vars_input"),
                Label("Binds"),
                TextArea(disabled=True, id="review_binds_input"),
                Label("Command Flags"),
                TextArea(disabled=True, id="review_command_flags_input"),
                Label("System Packages"),
                TextArea(disabled=True, id="review_system_packages_input"),
                Label("Python Packages"),
                TextArea(disabled=True, id="review_python_packages_input"),
                id="review_additional_info_container",
            ),
            id="step_2_container",
            classes="hidden"
        )
        
        # Step 3: Build Configuration (initially hidden)
        yield Container(
            Horizontal(
                Vertical(
                    Label("Build Singularity Image:"),
                    Button("Build Singularity Image", id="build_image_btn", variant="primary", disabled=True),
                    Label("Build Logs:"),
                    Log(id="image_log_viewer", classes="log_viewer"),
                    classes="build_section"
                ),
                Vertical(
                    Label("Build Virtual Environment:"),
                    Button("Build Virtual Environment", id="build_venv_btn", variant="primary", disabled=True),
                    Label("Build Logs:"),
                    Log(id="venv_log_viewer", classes="log_viewer"),
                    classes="build_section"
                ),
                id="build_options_container"
            ),
            id="step_3_container",
            classes="hidden"
        )
        
        # Navigation buttons
        yield Horizontal(
            Button("Previous", id="prev_btn", variant="primary", disabled=True),
            Button("Next", id="next_btn", variant="primary", disabled=True),
            Button("Cancel", id="cancel_btn", variant="warning"),
            Button("Help", variant="default", id="help_btn"),
            Button("Save and Exit", variant="success", id="save_exit_btn"),
            id="wizard_buttons",
            classes="button_row",
        )
    
    def navigate_to_step(self, step: int) -> None:
        """Navigate to a specific step in the wizard."""
        if step < 1 or step > self.total_steps:
            return
        
        # Hide all step containers
        for i in range(1, self.total_steps + 1):
            print(f"Setting visibility for step {i}, target step is {step}")
            container = self.query_one(f"#step_{i}_container", Container)
            container.add_class("hidden") if i != step else container.remove_class("hidden")
            
        if step == 2:
            print("Setting UI fields for step 2")
            self.set_ui_fields_for_step_2()
        elif step == 3:
            self.set_ui_fields_for_step_3()
        
        # Stop log streaming when leaving step 3
        if self.current_step == 3 and step != 3:
            self._stop_log_streaming()
        
        # Update step indicator and progress bar
        self.current_step = step
        self.query_one("#step_indicator", Static).update(f"Step {step} of {self.total_steps}")
        self.query_one("#progress", ProgressBar).update(progress=step)
        
        # Update button states
        prev_btn = self.query_one("#prev_btn", Button)
        next_btn = self.query_one("#next_btn", Button)
        
        if self.review_mode:
            prev_btn.disabled = (step > 1)
        else:
            prev_btn.disabled = (step == 1)
        
        next_btn.label = "Next" if step < self.total_steps else "Finish"
        if (step == 1 and not self.logic_name) or (step == 3):
            next_btn.disabled = True
        else:
            next_btn.disabled = False
            
        save_exit_btn = self.query_one("#save_exit_btn", Button)
        save_exit_btn.visible = (step not in {3})

    def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        self._stop_log_streaming()
    
    def _start_image_log_streaming(self) -> None:
        """Start streaming logs from the image build log file."""
        if self._image_log_task:
            self._image_log_task.cancel()
        
        self._image_log_task = asyncio.create_task(
            self._stream_log_file(self.process_dir.build_image_log_path, "#image_log_viewer")
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
        if self._image_log_task:
            self._image_log_task.cancel()
            self._image_log_task = None
            
        if self._venv_log_task:
            self._venv_log_task.cancel()
            self._venv_log_task = None
    
    @on(Button.Pressed, "#build_image_btn")
    def handle_build_image_button(self, event: Button.Pressed) -> None:
        """Handle build Singularity image button press."""
        if not self.process_dir:
            self.app.notify("No process directory available.", severity="error")
            return
            
        try:
            # Start the build process
            image_path, job_id = self.process_dir.build_singularity_image(scheduler=None)
            
            # Update button state
            build_btn = self.query_one("#build_image_btn", Button)
            build_btn.label = f"Building... (PID: {job_id})"
            build_btn.disabled = True
            
            # Start log streaming
            self._start_image_log_streaming()
            
            self.app.notify(f"Singularity image build started with PID: {job_id}", severity="info")
            
        except Exception as e:
            self.app.notify(f"Failed to start image build: {str(e)}", severity="error")