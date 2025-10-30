import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))
from neuroanalyst.models.process.process.core import NeuProcess

from typing import Optional

from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Label,
    Input,
    Select,
    Markdown,
    SelectionList,
    ListView,
    ListItem,
    TextArea,
    Log
    )
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.binding import Binding
from textual import on

class ConfirmModal(ModalScreen[bool]):
    BINDINGS = [
        Binding("escape", "dismiss(False)", "Cancel"),
    ]
    
    def __init__(self, message="Are you sure you want to proceed?"):
        super().__init__()
        self.message = message

    def compose(self):
        with Container(id="dialog"):
            yield Label(self.message, id="question")
            with Horizontal():
                yield Button("Yes", variant="primary", id="yes-button")
                yield Button("No", variant="default", id="no-button")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes-button":
            self.dismiss(True)
        else:
            self.dismiss(False)
            
class ErrorModal(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss()", "Close"),
    ]
    
    def __init__(self, error_message="An error has occurred."):
        super().__init__()
        self.error_message = error_message

    def compose(self):
        with Container(id="error_dialog"):
            yield Markdown(f"**Error:** {self.error_message}", id="error_message")
            yield Button("Close", variant="primary", id="close-button")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "close-button":
            self.dismiss()
            
class SuccessModal(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss()", "Close"),
    ]
    
    def __init__(self, message="Operation completed successfully."):
        super().__init__()
        self.message = message

    def compose(self):
        with Container(id="success_dialog"):
            yield Markdown(f"**Success:** {self.message}", id="success_message")
            yield Button("Close", variant="primary", id="close-button")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "close-button":
            self.dismiss()
            
class InputModal(ModalScreen[str | None]):
    BINDINGS = [
        Binding("escape", "dismiss(None)", "Cancel"),
    ]
    
    def __init__(self, prompt="Please enter a value:"):
        super().__init__()
        self.prompt = prompt

    def compose(self):
        with Container(id="input_dialog"):
            yield Label(self.prompt, id="input_prompt")
            yield Input(placeholder="Type here...", id="input_field", classes="medium_input")
            with Horizontal():
                yield Button("Submit", variant="primary", id="submit-button")
                yield Button("Cancel", variant="default", id="cancel-button")

    def on_input_submitted(self, event: Input.Submitted):
        if event.value.strip():
            self.dismiss(event.value)
        else:
            self.dismiss(None)

    def action_submit_input(self):
        input_field = self.query_one("#input_field", Input)
        if input_field.value.strip():
            self.dismiss(input_field.value)
        else:
            self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "submit-button":
            input_field = self.query_one("#input_field", Input)
            if input_field.value.strip():
                self.dismiss(input_field.value)
            else:
                self.dismiss(None)
        else:
            self.dismiss(None)
            
class SelectModal(ModalScreen[int | None]):
    BINDINGS = [
        Binding("escape", "dismiss(None)", "Cancel"),
    ]
    
    def __init__(self, prompt="Please make a selection:", options: list[str] = []):
        super().__init__()
        self.prompt = prompt
        self.options = options

    def compose(self):
        with Container(id="select_dialog"):
            yield Label(self.prompt, id="select_prompt")
            yield Select(
                options=[(option, option) for option in self.options],
                id="select_field",
                prompt="Select an option"
            )
            with Horizontal():
                yield Button("Submit", variant="primary", id="submit-button")
                yield Button("Cancel", variant="default", id="cancel-button")
    
    def action_submit_selection(self):
        select_field = self.query_one("#select_field", Select)
        if select_field.value is not None:
            self.dismiss(select_field.value)
        else:
            self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "submit-button":
            select_field = self.query_one("#select_field", Select)
            if select_field.value is not None:
                self.dismiss(select_field.value)
            else:
                self.dismiss(None)
        else:
            self.dismiss(None)
            
            
class InfoModal(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss()", "Close"),
    ]
    
    def __init__(self, message="This is an informational message."):
        super().__init__()
        self.message = message

    def compose(self):
        with VerticalScroll(id="info_dialog"):
            yield Markdown(self.message, id="info_message")
        yield Button("Close", variant="primary", id="close-button")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "close-button":
            self.dismiss()
            
class LoadingModal(ModalScreen[None]):
    """A modal screen that displays a loading message while performing a blocking operation. Returns the result of the operation when done."""
    BINDINGS = [
        Binding("escape", "dismiss()", "Close"),
    ]
    
    def __init__(self, message="Loading, please wait...", function: Optional[callable] = None, kwargs: Optional[dict] = None):
        super().__init__()
        self.message = message
        self.function = function
        self.kwargs = kwargs
        self.result = None

    def compose(self):
        with Container(id="loading_dialog"):
            yield Label(self.message, id="loading_message")
        
    async def on_mount(self) -> None:
        # Wait for the modal to be fully mounted before loading data
        self.run_worker(self.load())
        
    async def load(self, **kwargs) -> None:
        if not self.function:
            return
        
        try:
            # Run the blocking function in a worker thread to avoid blocking the UI
            if self.kwargs:
                self.result = await asyncio.to_thread(self.function, **self.kwargs)
            else:
                self.result = await asyncio.to_thread(self.function)
        except Exception as e:
            self.result = None
            error_str: str = str(e).replace("[", "").replace("]", "").replace("'", "")
            self.app.push_screen(ErrorModal(f"Error loading data:\n{error_str}"))
        finally:
            self.dismiss(self.result)
    

class LoadingDataModal(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss()", "Close"),
    ]
    
    def __init__(self, message="Loading data, please wait...", function: Optional[callable] = None, kwargs: Optional[dict] = None):
        super().__init__()
        self.message = message
        self.function = function
        self.kwargs = kwargs

    def compose(self):
        with Container(id="loading_data_dialog"):
            yield Log(highlight=True, id="loading_message")
            yield Button("Close", variant="primary", id="close-button")
    
    async def on_mount(self) -> None:
        # Wait for the modal to be fully mounted before loading data
        self.run_worker(self.load())
        
    async def load(self, **kwargs) -> None:
        log_widget = self.query_one("#loading_message", Log)
        log_widget.clear()
        log_widget.write_line(self.message)
        
        if not self.function:
            log_widget.write_line("No function provided to load data.")
            return
        
        try:
            # Run the blocking function in a worker thread to avoid blocking the UI
            if self.kwargs:
                # result = await self.app.run_in_thread(self.function, **self.kwargs)
                result = await asyncio.to_thread(self.function, **self.kwargs)
            else:
                result = await asyncio.to_thread(self.function)
            result = str(result)

            log_widget.clear()
            
            if not result.strip():
                log_widget.write_line("Data loaded successfully. No output to display.")
                return
            
            lines: list[str] = result.split("\n")
            log_widget.write_line(f"Data loaded successfully. Count: {len(lines)}")
            for line in lines:
                if line.strip():
                    log_widget.write_line(line)
        except Exception as e:
            log_widget.clear()
            log_widget.write_line(f"Error loading data: {str(e)}")

    @on(Button.Pressed, "#close-button")
    def on_close_button_pressed(self, event: Button.Pressed):
        self.dismiss()
    
    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss()
            
class StepUpdateModal(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss()", "Close"),
    ]
    
    def __init__(self, step_name: str, step_description: str, available_processes: list[str], processes: list[str]):
        super().__init__()
        self.step_name = step_name
        self.step_description = step_description
        self.available_processes_options: list[tuple[str, str]] = [
            (f"{proc} - {NeuProcess.from_process_id(proc, username=self.app.global_vars.get('username')).process_dir.logic.about.name}", proc) for proc in available_processes
        ]
        self.processes: list[str] = [proc for proc in processes]
        self.extra_parameters: list[str] = []

    def compose(self):
        with Horizontal(id="step_dialog"):
            with Vertical(id="step_info"):
                yield Label(f"Step: {self.step_name}", id="step_name")
                yield Input(value=self.step_name, id="step_name_input", placeholder="Step Name", classes="medium_input")
            with Vertical(id="step_description"):
                yield Label("Step Description:", id="step_description_label")
                yield TextArea(text=self.step_description, id="step_description_input", placeholder="Step Description")
            with Vertical(id="process_selection"):
                yield Label("Select Process for this Step:", id="process_label")
                yield Select(
                    options=self.available_processes_options,
                    id="processes_available_select",
                    prompt="Select a process"
                )
                yield Button("+", variant="default", id="add_process_button", classes="arithmetic_buttons")
                yield Button("-", variant="default", id="remove_process_button", classes="arithmetic_buttons")
            with Vertical(id="process_view"):
                yield Label("Processes in this Step:", id="processes_in_step_label")
                yield ListView(
                    *[ListItem(Label(proc)) for i, proc in enumerate(self.processes)],
                    id="selected_processes_list"
                )
                
            yield Button("Save and Exit", variant="primary", id="save-button")
            yield Button("Close", variant="primary", id="close-button")

    @on(Button.Pressed, "#add_process_button")
    def add_process(self) -> None:
        def handle_extra_parameters_added(result: dict | None) -> None:
            if result:
                self.extra_parameters.append(result)
                self.app.notify(f"Added extra parameters: {result}")
        
        processes_available_select = self.query_one("#processes_available_select", Select)
        selected_processes_list = self.query_one("#selected_processes_list", ListView)
        selected_process = processes_available_select.value
        if selected_process and selected_process not in self.processes:
            self.processes.append(selected_process)
            selected_processes_list.append(ListItem(Label(selected_process), id=f"proc_{len(selected_processes_list.children)}"))
            
            # Add extra parameters
            process: NeuProcess = NeuProcess.from_process_id(selected_process, username=self.app.global_vars.get("username"))
            self.app.notify(f"Extra parameters: {process.get_non_standard_parameters()}")
            self.app.push_screen(
                AddParametersModal(selected_process),
                callback=handle_extra_parameters_added
            )
            

    @on(Button.Pressed, "#remove_process_button")
    def remove_process(self) -> None:
        selected_processes_list = self.query_one("#selected_processes_list", ListView)
        for idx, item in enumerate(selected_processes_list.children):
            if item.highlighted:
                self.processes.remove(item.query_one(Label).content)
                break
            
        # Re-mount the ListView with updated IDs
        selected_processes_list.clear()
        for i, proc in enumerate(self.processes):
            selected_processes_list.append(ListItem(Label(proc)))

    @on(Button.Pressed, "#save-button")
    def save_and_exit(self) -> None:
        step_name_input = self.query_one("#step_name_input", Input)
        step_description_input = self.query_one("#step_description_input", TextArea)
        processes_list = self.query_one("#selected_processes_list", ListView)
        
        self.step_name = step_name_input.value
        self.step_description = step_description_input.text
        self.processes = [item.query_one(Label).content for item in processes_list.children]
        
        self.dismiss({
            "step_name": self.step_name,
            "step_description": self.step_description,
            "processes": self.processes,
            "extra_parameters": self.extra_parameters
        })
    
    @on(Button.Pressed, "#close-button")
    def close_modal(self) -> None:
        self.dismiss()
        
class AddParametersModal(ModalScreen[dict[str, str] | None]):
    BINDINGS = [
        Binding("escape", "dismiss()", "Cancel"),
    ]
    
    def __init__(self, process_id: str):
        super().__init__()
        self.process_id: list[str] = [process_id]
        self.parameters: dict[str, any] = {}
        process: NeuProcess = NeuProcess.from_process_id(process_id, username=self.app.global_vars.get("username"))
        self.parameters = {
            "bind_paths": {item: None for item in process.get_non_standard_bind_paths()},
            "environment_variables": {item: None for item in process.get_non_standard_environment_variables()}
            }
        self.result: dict[str, str] = {"bind_paths": {}, "environment_variables": {}}
        if not self.parameters["bind_paths"] and not self.parameters["environment_variables"]:
            self.app.notify("No extra parameters required for this process.", severity="info")
            self.dismiss(self.result)

    def compose(self):
        with Container(id="parameters_dialog"):
            for idx, param in enumerate(self.parameters["bind_paths"].keys()):
                yield Label(f"Bind Path Parameter: {param}", id=f"label_bind_{idx}")
                yield Input(placeholder=f"Enter value for {param}", id=f"input_bind_{idx}")
            for idx, param in enumerate(self.parameters["environment_variables"].keys()):
                yield Label(f"Environment Variable Parameter: {param}", id=f"label_env_{idx}")
                yield Input(placeholder=f"Enter value for {param}", id=f"input_env_{idx}")
            with Horizontal():
                yield Button("Submit", variant="primary", id="submit-button")
                yield Button("Cancel", variant="default", id="cancel-button")

    @on(Button.Pressed, "#submit-button")
    def on_submit_pressed(self) -> None:
        for param in self.parameters["bind_paths"].keys():
            input_field = self.query_one(f"#input_bind_{list(self.parameters['bind_paths'].keys()).index(param)}", Input)
            self.result["bind_paths"][param] = input_field.value.strip()
        for param in self.parameters["environment_variables"].keys():
            input_field = self.query_one(f"#input_env_{list(self.parameters['environment_variables'].keys()).index(param)}", Input)
            self.result["environment_variables"][param] = input_field.value.strip()
                
        if any(value is None or len(value) == 0 for value in self.result["bind_paths"].values()):
            self.app.push_screen(ErrorModal("All parameters in bind_paths must be filled out."))
            return
        if any(value is None or len(value) == 0 for value in self.result["environment_variables"].values()):
            self.app.push_screen(ErrorModal("All parameters in environment_variables must be filled out."))
            return

        self.dismiss(self.result)
        
    @on(Button.Pressed, "#cancel-button")
    def on_cancel_pressed(self) -> None:
        self.dismiss()
            
    def on_input_submitted(self, event: Input.Submitted):
        self.on_submit_pressed()