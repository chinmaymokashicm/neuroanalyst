"""
Register logic screen for the NeuroAnalyst TUI application.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))
from neuroanalyst.models.process.logic.core import NeuProcessLogic
from neuroanalyst.models.process.logic.code.python.decoder import PythonDecoder

sys.path.append(str(Path(__file__).resolve().parents[3]))
from tui.utils.data import build_tree
# from tui.constants import SCREEN_NAMES
from tui.components.modal import InfoModal, ConfirmModal
from tui.constants import SCREEN_NAMES
from tui.screens.base import BaseScreen

from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Header,
    Footer,
    Static,
    Button,
    Input,
    TextArea,
    Label,
    Select,
    Markdown,
    Switch,
    Tree
    )
from textual.screen import Screen
from textual.reactive import reactive

CHOOSE_LOGIC_DEFAULT: str = "Choose Logic to Edit"

with open("text/register_logic.md", "r") as f:
    register_logic_text: str = f.read()

# class RegisterLogicScreen(Screen):
class RegisterLogicScreen(BaseScreen):
    """Screen for registering or editing a logic."""
    title: reactive[str] = reactive("# Register New Logic")
    submit_text: reactive[str] = reactive("Register Logic")
    logic_name: reactive[str] = reactive("")
    
    def __init__(self, logic_name: str = ""):
        super().__init__()
        
        logic_name: str = str(logic_name)
        
        self.set_updated_logics_select_options(logic_name)
        
        self.title = "# Edit Logic" if logic_name and logic_name != CHOOSE_LOGIC_DEFAULT else "# Register New Logic"
        self.submit_text = "Update Logic" if logic_name and logic_name != CHOOSE_LOGIC_DEFAULT else "Register Logic"
    
    def on_mount(self) -> None:
        self.update_logic_fields(self.logic_name)
        
    def if_logic_already_registered(self, logic_name: str) -> bool:
        all_logics: list[NeuProcessLogic] = NeuProcessLogic.get_all_registered_logics(username=self.app.global_vars.get("username"))
        for logic in all_logics:
            if logic.about.name == logic_name:
                return True
        return False
    
    def set_updated_logics_select_options(self, default_logic_name: Optional[str] = None) -> list[tuple[str, str]]:
        all_logics: list[NeuProcessLogic] = NeuProcessLogic.get_all_registered_logics(username=self.app.global_vars.get("username"))
        all_logic_names: list[str] = [logic.about.name for logic in all_logics]
        
        logic_select_options: list[tuple[str, str]] = [(option, option) for option in all_logic_names + [CHOOSE_LOGIC_DEFAULT]]
        
        if default_logic_name not in all_logic_names:
            # self.logic_name = all_logic_names[0] if all_logic_names else CHOOSE_LOGIC_DEFAULT
            self.logic_name = CHOOSE_LOGIC_DEFAULT
        else:
            self.logic_name = default_logic_name
        
        self.logic_select = Select(
            logic_select_options,
            id="logic_select",
            prompt="Select Logic to Edit",
            type_to_search=True,
            value=self.logic_name
        )
                
    def update_logic_fields(self, logic_name: str) -> None:
        self.logic_name: str = logic_name
        logic_name: str = self.logic_select.value
        if logic_name and logic_name != "Choose Logic to Edit":
            logic: NeuProcessLogic = NeuProcessLogic.from_func_name(logic_name, username=self.app.global_vars.get("username"))
            self.query_one("#logic_name_input", TextArea).text = logic.about.name
            self.query_one("#logic_description_input", TextArea).text = logic.about.description if logic.about.description else ""
            self.query_one("#logic_version_input", TextArea).text = logic.about.version if logic.about.version else ""
            self.query_one("#logic_author_input", TextArea).text = logic.about.author if logic.about.author else ""
            self.query_one("#logic_tag_input", TextArea).text = logic.about.tag if logic.about.tag else ""
            self.query_one("#logic_code_input", TextArea).text = logic.code if logic.code else ""
            self.title = f"# Edit Logic: {logic.about.name}"
            self.query_one("#markdown_title", Markdown).update(self.title)
            self.submit_text = "Update Logic"
            self.query_one("#submit_btn", Button).label = self.submit_text
            self.query_one("#logic_metrics_switch", Switch).value = logic.has_metrics
            self.query_one("#output_entities_tree", Tree).clear()
            # output_entities_tree = build_tree(logic.get_output_entities_dict(), self.query_one("#output_entities_tree", Tree))
            output_entities_tree: Tree[str] = build_tree(logic.output_entities, self.query_one("#output_entities_tree", Tree))
            self.query_one("#output_entities_tree", Tree).mount(output_entities_tree)
            if logic.language.lower() == "python":
                self.query_one("#logic_code_input", TextArea).language = logic.language.lower()
        else:
            self.clean_up_fields()
    
    def clean_up_fields(self) -> None:
        self.query_one("#logic_name_input", TextArea).text = ""
        self.query_one("#logic_description_input", TextArea).text = ""
        # self.query_one("#logic_version_input", TextArea).text = ""
        # self.query_one("#logic_author_input", TextArea).text = ""
        # self.query_one("#logic_tag_input", TextArea).text = ""
        self.query_one("#logic_code_input", TextArea).text = ""
        self.title = "# Register New Logic"
        self.query_one("#markdown_title", Markdown).update(self.title)
        self.submit_text = "Register Logic"
        self.query_one("#submit_btn", Button).label = self.submit_text
        self.query_one("#logic_metrics_switch", Switch).value = False
        self.query_one("#output_entities_tree", Tree).clear()
    
    def decode_logic_fields(self) -> None:
        logic_code: str = self.query_one("#logic_code_input", TextArea).text
        if logic_code:
            decoder: PythonDecoder = PythonDecoder()
            try:
                decoded_logic: Optional[NeuProcessLogic] = decoder.decode_from_string(logic_code)
            except Exception as e:
                # Clean up error string to avoid MarkupError in notify
                error_str: str = str(e).replace("[", "").replace("]", "").replace("'", "")
                self.notify(f"Error decoding logic: {error_str}", severity="error")
                decoded_logic = None
                self.query_one("#logic_name_input", TextArea).text = logic_code
            print(decoded_logic, type(decoded_logic))
            if decoded_logic:
                self.query_one("#logic_name_input", TextArea).text = decoded_logic.about.name
                self.query_one("#logic_description_input", TextArea).text = decoded_logic.about.description if decoded_logic.about.description else ""
                self.query_one("#logic_metrics_switch", Switch).value = decoded_logic.has_metrics
                self.query_one("#output_entities_tree", Tree).clear()
                output_entities_tree = build_tree(decoded_logic.output_entities, self.query_one("#output_entities_tree", Tree))
                self.query_one("#output_entities_tree", Tree).mount(output_entities_tree)
                
                # If the decoded logic name is already registered, notify the user
                if self.if_logic_already_registered(decoded_logic.about.name):
                    self.notify(f"Logic '{decoded_logic.about.name}' is already registered. Editing it will update the existing logic.", severity="warning")
                    # Update title and submit text accordingly
                    self.title = f"# Edit Logic: {decoded_logic.about.name}"
                    self.submit_text = "Update Logic"
                    self.query_one("#markdown_title", Markdown).update(self.title)
                    self.query_one("#submit_btn", Button).label = self.submit_text
                else:
                    self.title = "# Register New Logic"
                    self.submit_text = "Register Logic"
                    self.query_one("#markdown_title", Markdown).update(self.title)
                    self.query_one("#submit_btn", Button).label = self.submit_text

                self.notify("Logic decoded successfully", severity="success")
            else:
                self.notify("Failed to decode logic code", severity="error")
        else:
            self.notify("Logic code is empty", severity="warning")
    
    def compose_content(self) -> ComposeResult:
        """Create the UI layout for the register logic screen."""
        yield Markdown(self.title, classes="title", id="markdown_title")
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
                Label("Description:"),
                TextArea(
                    placeholder="Description",
                    id="logic_description_input",
                    read_only=True
                ),
                Horizontal(
                    Label("Version:"),
                    TextArea(placeholder="Version", id="logic_version_input", classes="small_input"),
                    Label("Tag:"),
                    TextArea(placeholder="Tag", id="logic_tag_input", classes="small_input"),
                    Label("Metrics:"),
                    Switch(value=False, id="logic_metrics_switch", disabled=True),
                    id="logic_meta_container_0"
                ),
                Horizontal(
                    Label("Name:"),
                    TextArea(
                        placeholder="Name",
                        id="logic_name_input",
                        read_only=True,
                        classes="small_input"
                    ),
                    Label("Author:"),
                    TextArea(placeholder="Author", id="logic_author_input", classes="medium_input"),
                    id="logic_meta_container_1"
                ),
                Tree(label="Output Entities", id="output_entities_tree"),
                Horizontal(
                    Button(self.submit_text, id="submit_btn", variant="success"),
                    classes="button_row"
                ),
                id="logic_description_container"
            ),
            id="logic_form_container",
        ),
        Horizontal(
            Button("Decode", id="decode_btn", variant="success"),
            Button("Cancel", id="cancel_btn", variant="warning"),
            Button("Help", variant="default", id="help_btn"),
            classes="button_row"
        ),
        id="register_logic_container"
    )
        
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle logic selection change."""
        selected_logic_name: str = event.value
        self.update_logic_fields(selected_logic_name)
    
    @on(Button.Pressed, "#decode_btn")
    def handle_decode_button(self) -> None:
        """Handle decode button press."""
        try:
            self.decode_logic_fields()
        except Exception as e:
            # self.notify(f"Error decoding logic: {str(e)}", severity="error")
            pass
    
    @on(Button.Pressed, "#help_btn")
    def handle_help_button(self, event: Button.Pressed) -> None:
        """Handle help button press to show info modal."""
        info_text = register_logic_text
        self.app.push_screen(
            InfoModal(
                message=info_text,
            )
        )
    
    @on(Button.Pressed, "#cancel_btn")
    def handle_cancel_button(self) -> None:
        """Handle cancel button press."""
        self.app.pop_screen()
        #! Clear fields of every select
        self.app.clear_selection()
        
    @on(Button.Pressed, "#submit_btn")
    def handle_register_button(self) -> None:
        """Handle register button press."""
        # Implement the logic for registering the logic here
        if not self.logic_name or len(self.logic_name) == 0:
            self.notify("Please select a logic to edit before submitting.", severity="warning")
            return
        decoder: PythonDecoder = PythonDecoder()
        try:
            logic: NeuProcessLogic = decoder.decode_from_string(
            self.query_one("#logic_code_input", TextArea).text)
            logic.about.version = self.query_one("#logic_version_input", TextArea).text
            logic.about.author = self.query_one("#logic_author_input", TextArea).text
            logic.about.tag = self.query_one("#logic_tag_input", TextArea).text
            logic.username = self.app.global_vars.get("username")
            
            # Determine if we are updating or registering new
            if self.logic_name == logic.about.name:
                confirm_message: str = f"Are you sure you want to update the logic '{logic.about.name}'?"
            else:
                confirm_message: str = f"Are you sure you want to register the new logic '{logic.about.name}'?"
            self.app.push_screen(ConfirmModal(message=confirm_message), callback=lambda result: self.after_register_callback(result, logic))
            self.clean_up_fields()
            self.set_updated_logics_select_options(logic.about.name)
        except Exception as e:
            self.notify(f"Error decoding logic: {str(e)}", severity="error")
            
    def after_register_callback(self, result: bool, logic: NeuProcessLogic) -> None:
        """Callback after modal confirmation for registering logic."""
        if result:
            # logic.register()
            action: str = "updated" if self.logic_name == logic.about.name else "registered"
            if action == "registered" and self.if_logic_already_registered(logic.about.name):
                logic.register(overwrite=True)
            else:
                logic.register()
            self.notify(f"Logic {action} successfully", severity="success")
            self.app.pop_screen()
            # self.app.push_screen(SCREEN_NAMES["logic"]["list"])
            
            #! Clear fields of every select
            self.app.clear_selection()