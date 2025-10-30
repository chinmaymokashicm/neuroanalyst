import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[4]))
from neuroanalyst.models.process.logic.core import ALLOWED_PYBIDS_ENTITY_KEYS
from neuroanalyst.models.pipeline.core import NeuPipeline
from neuroanalyst.utils.constants import NeuroAnalystPaths
from neuroanalyst.utils.bids import get_bids_files

from .modal import InputModal, SelectModal, StepUpdateModal, InfoModal, ErrorModal, LoadingDataModal
from ..utils.data import build_tree

from typing import Optional

from textual.widgets import (
    Static,
    TextArea,
    Label,
    Button,
    Input,
    Select,
    RadioSet,
    RadioButton,
    Tree,
    DataTable,
    Switch,
    ProgressBar
    )
from textual.containers import Horizontal, Vertical, Container
from textual.app import ComposeResult
from textual.reactive import reactive
from textual import on

SEPARATOR: str = "___________"


class CustomListComponent(Vertical):
    """A reusable list component with a title and action buttons."""

    def __init__(self, type_suffix: str, title: str, labels: list[str]):
        super().__init__()
        self.type_suffix = type_suffix
        self.title = title
        self.labels = labels
        self.selected_index: Optional[int] = None

        # Add a CSS id to the root component for styling/selection
        self.id = f"{self.type_suffix}_component"
        self.classes = "custom_list_component"
        
        self.ids: dict[str, str] = {
            "text_area": f"{self.type_suffix}_text_area",
            "add_button": f"add_{self.type_suffix}_btn",
            "remove_button": f"remove_{self.type_suffix}_btn",
            "item_select": f"{self.type_suffix}_item_select"
        }

    def compose(self) -> ComposeResult:
        """Compose the UI elements of the custom list component."""
        yield Label(f"{self.title}", id=f"{self.type_suffix}_list_title", classes="list_title")
        yield Horizontal(
            Button("+", id=self.ids["add_button"], variant="success", classes="arithmetic_buttons"),
            Button("-", id=self.ids["remove_button"], variant="error", classes="arithmetic_buttons"),
            Select(
                options=[(label, i) for i, label in enumerate(self.labels)],
                prompt="Select item to remove",
                id=self.ids["item_select"],
                classes="item_select"
            ),
            classes="arithmetic_button_row"
        )
        # Create TextArea with comma-separated quoted values
        text_content = self._format_labels_as_text()
        yield TextArea(text_content, read_only=True, id=self.ids["text_area"], classes="custom_text_area")
    
    def on_mount(self) -> None:
        """Called when the component is mounted."""
        self._update_text_area()
        self._update_select_options()
        
    def _format_labels_as_text(self) -> str:
        """Format labels as comma-separated quoted values."""
        if not self.labels:
            return ""
        quoted_labels = [f'"{label}"' if " " in label else label for label in self.labels]
        return ", ".join(quoted_labels)
        
    def update_labels(self, new_labels: list[str]) -> None:
        """Update the labels in the text area."""
        self.labels = new_labels
        self._update_text_area()
        self._update_select_options()
    
    def _update_text_area(self) -> None:
        """Update the text area content."""
        text_area = self.query_one(f"#{self.type_suffix}_text_area", TextArea)
        formatted_text = self._format_labels_as_text()
        text_area.text = formatted_text
        
        # Calculate height based on content length
        if len(formatted_text) > 100:  # If content is long, give more height
            text_area.styles.height = 6
        elif len(formatted_text) > 50:
            text_area.styles.height = 4
        else:
            text_area.styles.height = 3
    
    def _update_select_options(self) -> None:
        """Update the Select widget options."""
        item_select = self.query_one(f"#{self.type_suffix}_item_select", Select)
        options = [(label, i) for i, label in enumerate(self.labels)]
        item_select.set_options(options)
    
    def _handle_add_label(self, label: str) -> None:
        """Callback to handle adding a new label."""
        label = label.strip() if label else None
        if label:
            self.labels.append(label)
            self._update_text_area()
            self._update_select_options()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == self.ids["add_button"]:
            self.app.push_screen(
                InputModal(
                    prompt="Enter label:",
                ),
                callback=self._handle_add_label
            )
        
        elif button_id == self.ids["remove_button"]:
            # Get the selected item from the select widget
            item_select = self.query_one(f"#{self.type_suffix}_item_select", Select)
            selected_index = item_select.value
            
            if selected_index is not None and 0 <= selected_index < len(self.labels):
                del self.labels[selected_index]
                self._update_text_area()
                self._update_select_options()
                # Reset the select widget to show no selection
                item_select.value = Select.BLANK
                
                
class MultiParameterListComponent(Horizontal):
    """
    A component to manage multiple parameter lists side by side.
    
    Layout:
    - On the left, a RadioSet to select the category.
    - Next to it, two buttons to add/remove items from the selected category. 
        - Add button opens the InputModal to input new item.
        - Remove button opens the SelectModal to choose item to remove.
    - On the right, a tree view of all categories and their items.
    """
    
    title: str
    categories: dict[str, list[str]] = {}
    selected_category: Optional[str] = None
    
    def __init__(self, categories: dict[str, list[str]], title: str = "Parameters"):
        super().__init__()
        self.categories = categories
        self.selected_category = next(iter(categories)) if categories else None
        self.title = title
        self.classes = "multi_parameter_list_component"
    
    def compose(self) -> ComposeResult:
        """Compose the UI elements of the multi-parameter list component."""
        
        with Vertical(id="category_selection"):
            yield Label(self.title, id="category_label", classes="list_title")
            with RadioSet(id="category_radios"):
                for category in self.categories.keys():
                    yield RadioButton(category, id=f"radio_{category.replace(' ', SEPARATOR)}", value=category)
        
        with Vertical(id="parameter_management"):
            yield Button("+", id="add_parameter_btn", variant="success", classes="arithmetic_buttons")
            yield Button("-", id="remove_parameter_btn", variant="error", classes="arithmetic_buttons")
        
        yield Tree(label="Parameters", id="parameter_tree_view")
        
    def on_mount(self) -> None:
        """Called when the component is mounted."""
        self._update_tree_view()
        
    def _update_tree_view(self) -> None:
        """Update the tree view content."""
        tree: Tree = self.query_one("#parameter_tree_view", Tree)
        tree.clear()
        updated_tree = build_tree(self.categories, tree)
        tree.mount(updated_tree)
        tree.root.label = "Parameters"
        for item in tree.root.children:
            item.expand()

        # Adjust height based on content length
        lines = sum(len(items) for items in self.categories.values()) + len(self.categories)
        tree.styles.height = min(max(lines, 3), 15)  # Between 3 and 15 lines tall
        
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle category selection changes."""
        print(f"Radio changed: {event.pressed}")
        id: int = event.pressed.id
        category_name: str = id.replace("radio_", "").replace(SEPARATOR, " ")
        if category_name not in self.categories:
            raise ValueError(f"Unknown category selected: {category_name}")
        self.selected_category = category_name

    @on(Button.Pressed, "#add_parameter_btn")
    def handle_add_parameter(self) -> None:
        """Handle adding a new parameter to the selected category."""
        if not self.selected_category:
            return  # No category selected
        
        def add_callback(label: str) -> None:
            label = label.strip() if label else None
            labels: list[str] = [item.strip() for item in label.split(",")] if label else []
            self.categories[self.selected_category].extend(labels)
            self._update_tree_view()
            # if label:
            #     self.categories[self.selected_category].append(label)
            #     self._update_tree_view()
        
        self.app.push_screen(
            InputModal(
                prompt=f"Enter new parameter for '{self.selected_category}'. For multiple parameters, separate with commas:",
            ),
            callback=add_callback
        )
        
    @on(Button.Pressed, "#remove_parameter_btn")
    def handle_remove_parameter(self) -> None:
        """Handle removing a parameter from the selected category. Delete highlighted item in tree view."""
        
        # Delete the highlighted item in the tree view
        tree: Tree = self.query_one("#parameter_tree_view", Tree)
        selected_node = tree.cursor_node
        
        if selected_node and selected_node is not tree.root:
            parent_node = selected_node.parent
            
            if parent_node is tree.root:
                # Removing an entire category
                category_to_remove = str(selected_node.label)
                if category_to_remove in self.categories:
                    del self.categories[category_to_remove]
                    # Update selected category
                    self.selected_category = next(iter(self.categories)) if self.categories else None
            else:
                print(f"Removing parameter '{selected_node.label}' from category '{parent_node.label}'")
                # Removing a specific parameter from a category
                category_name = str(parent_node.label)
                parameter_to_remove = str(selected_node.label)
                if category_name in self.categories:
                    existing_parameters = self.categories[category_name]
                    if parameter_to_remove in existing_parameters:
                        existing_parameters.remove(parameter_to_remove)
                        if len(existing_parameters) == 0:
                            del self.categories[category_name]
                            # Update selected category
                            self.selected_category = next(iter(self.categories)) if self.categories else None
            self._update_tree_view()
        
        

class BIDSEntityListComponent(Horizontal):
    """A specialized list component for managing BIDS entities."""
    
    def __init__(self, bids_root: Optional[str] = None, scope: Optional[str] = None):
        self.allowed_entities = sorted(ALLOWED_PYBIDS_ENTITY_KEYS)
        self.bids_entities: dict[str, str] = {}
        self.bids_root = bids_root if bids_root else None
        self.scope = scope
        super().__init__()
        
    def compose(self) -> ComposeResult:
        """Compose the UI elements of the BIDS entity list component."""
        yield Vertical(
            Select(
                options=[(entity, entity) for entity in self.allowed_entities],
                prompt="Select BIDS Entity",
                id="bids_entity_select",
                classes="bids_entity_select",
                type_to_search=True
            ),
            Horizontal(
                Input(placeholder="Add Entity", id="bids_entity_input", classes="bids_entity_input"),
                Switch(value=False, id="bids_entity_value_is_None"),
                Label("None?", id="bids_entity_value_is_None_label")
            ),
            Horizontal(
                Button("+", id="add_bids_entity_btn", variant="success", classes="bids_entity_add_btn"),
                Button("-", id="remove_bids_entity_btn", variant="error", classes="bids_entity_remove_btn"),
                Button("Check", id="load_bids_files_btn", variant="primary", classes="bids_entity_load_btn")
            ),
            classes="bids_entity_button_column"
        )
        yield Horizontal(
            Button("Clear", id="clear_bids_entity_btn", variant="warning", classes="bids_entity_clear_btn"),
            id="bids_entity_action_row",
        )
        yield Tree(label="BIDS Entities", id="bids_entity_tree_view")
        
    def _update_tree_view(self) -> None:
        """Update the tree view content."""
        tree: Tree = self.query_one("#bids_entity_tree_view", Tree)
        tree.clear()
        updated_tree = build_tree(self.bids_entities, tree)
        tree.mount(updated_tree)
        tree.root.label = "BIDS Entities"
        for item in tree.root.children:
            item.expand()

        # Adjust height based on content length
        lines = len(self.bids_entities) + 1
        tree.styles.height = min(max(lines, 3), 15)  # Between 3 and 15 lines tall
    
    @on(Button.Pressed, "#add_bids_entity_btn")
    def handle_add_bids_entity(self) -> None:
        """Handle adding a new BIDS entity."""
        entity_select: Select = self.query_one("#bids_entity_select", Select)
        entity_input: Input = self.query_one("#bids_entity_input", Input)
        
        selected_entity = entity_select.value
        # Avoid entity being Select.BLANK
        if selected_entity == Select.BLANK:
            selected_entity = None
        
        input_value = entity_input.value.strip()
        if len(input_value) == 0:
            input_value = None

        if selected_entity:
            if selected_entity in self.bids_entities:
                existing_value: str | None | list[str] = self.bids_entities[selected_entity]
                if isinstance(existing_value, str | None):
                    self.bids_entities[selected_entity] = list(set([existing_value, input_value]))
                elif isinstance(existing_value, list):
                    self.bids_entities[selected_entity].append(input_value)
                    self.bids_entities[selected_entity] = list(set(self.bids_entities[selected_entity]))
            else:
                self.bids_entities[selected_entity] = input_value
            self._update_tree_view()
            entity_input.value = ""  # Clear input after adding
            
    @on(Button.Pressed, "#remove_bids_entity_btn")
    def handle_remove_bids_entity(self) -> None:
        """Handle removing a BIDS entity. Delete the highlighted entry, entity or individual value."""
        tree: Tree = self.query_one("#bids_entity_tree_view", Tree)
        selected_node = tree.cursor_node

        if selected_node and selected_node is not tree.root:
            parent_node = selected_node.parent

            if parent_node is tree.root:
                # Removing an entire entity
                entity_to_remove = str(selected_node.label).split(":")[0] # Get entity name before any ":" - noticed in tree view when there is only one value
                if entity_to_remove in self.bids_entities:
                    del self.bids_entities[entity_to_remove]
            else:
                print(f"Removing value '{selected_node.label}' from entity '{parent_node.label}'")
                # Removing a specific value from an entity
                entity_name = str(parent_node.label)
                value_to_remove = str(selected_node.label)
                if entity_name in self.bids_entities:
                    existing_value = self.bids_entities[entity_name]
                    if isinstance(existing_value, str) and existing_value == value_to_remove:
                        del self.bids_entities[entity_name]
                    elif isinstance(existing_value, list) and value_to_remove in existing_value:
                        existing_value.remove(value_to_remove)
                        if len(existing_value) == 1:
                            self.bids_entities[entity_name] = existing_value[0]
                        elif len(existing_value) == 0:
                            del self.bids_entities[entity_name]
            self._update_tree_view()

    @on(Button.Pressed, "#clear_bids_entity_btn")
    def handle_clear_bids_entities(self) -> None:
        """Handle clearing all BIDS entities."""
        self.bids_entities.clear()
        self._update_tree_view()

    @on(Input.Submitted, "#bids_entity_input")
    def handle_entity_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key press in the entity input field."""
        self.handle_add_bids_entity()
        
    @on(Switch.Changed, "#bids_entity_value_is_None")
    def handle_bids_entity_value_is_None_changed(self, event: Switch.Changed) -> None:
        """Handle the change of the switch for BIDS entity value being None."""
        self.bids_entity_value_is_None = event.value
        # Disable or enable the input field based on the switch state
        entity_input: Input = self.query_one("#bids_entity_input", Input)
        entity_input.disabled = event.value
        
        #! Set input value to None if switch is on
        # Set input value to an empty string if switch is off (None is not allowed in Input widget)
        if event.value:
            self.query_one("#bids_entity_input", Input).value = ""
            
    @on(Button.Pressed, "#load_bids_files_btn")
    def handle_load_bids_files(self) -> None:
        """Handle loading BIDS files based on current entities."""
        if not self.bids_root or not self.scope:
            self.app.push_screen(
                ErrorModal(
                    error_message="BIDS root or scope not set. Cannot load BIDS files."
                )
            )
            return
        self.load_bids_files(scope=self.scope, bids_root=self.bids_root)
    
    def load_bids_files(self, scope: str, bids_root: Path) -> None:
        """Load BIDS entities from BIDS files in the specified scope."""
        
        self.app.push_screen(
            LoadingDataModal(
                function=get_bids_files,
                kwargs={
                    "bids_filters": self.bids_entities,
                    "scope": scope,
                    "bids_root": bids_root,
                    "relative_path": True,
                    "return_as_list": False
                    },
                message=f"Loading BIDS files matching BIDS entities {self.bids_entities} in {bids_root} within scope '{scope}'..."
            )
        )

class PipelineStepsComponent(Horizontal):
    """A component to manage pipeline steps in order."""
    
    PROCESS_SEPARATOR: str = " + "
    
    n_steps: int = reactive(1)
    selected_step_index: Optional[int] = None
    steps: list[tuple[str, str, list[str], dict]] = []
    
    def __init__(self, n_steps: int = 1, process_separator: str = " + "):
        super().__init__()
        self.n_steps = n_steps
        self.steps = [(f"Step {i+1}", "", [], {}) for i in range(n_steps)]
        self.table = DataTable(id="pipeline_steps_table", cursor_type="row", zebra_stripes=True)
        self.process_separator = process_separator
        self.id = "pipeline_steps_component"
        paths = NeuroAnalystPaths(username=self.app.global_vars.get("username"))
        self.available_processes: list[str] = [subdir.name for subdir in paths.workdir.iterdir() if subdir.is_dir()]
        
    def on_mount(self) -> None:
        """Called when the component is mounted."""
        self.update_table()
    
    def compose(self) -> ComposeResult:
        """Compose the UI elements of the pipeline steps component."""
        yield Vertical(
            Label("Pipeline Steps", id="pipeline_steps_label", classes="list_title"),
            Button("+", id="add_pipeline_step_btn", variant="success", classes="arithmetic_buttons"),
            Button("-", id="remove_pipeline_step_btn", variant="error", classes="arithmetic_buttons"),
            Button("Update", id="update_pipeline_step_btn", variant="primary", classes="arithmetic_buttons"),
            classes="pipeline_steps_button_column"
        )
        yield self.table
        
    def _reset_table(self) -> None:
        """Update the DataTable content."""
        table: DataTable = self.query_one("#pipeline_steps_table", DataTable)
        table.clear(columns=True)
        # Skip extra parameters for table display for simplicity
        self.table.add_columns("Name", "Description", "Processes")
        self.steps = []
        for i in range(self.n_steps):
            self.steps.append((f"Step {i+1}", "", [], {}))
            self.update_table()
            
    def add_row(self, step_name: str, step_description: str, step_processes: list[str], extra_parameters: dict) -> None:
        """Add a new row to the DataTable."""
        table: DataTable = self.query_one("#pipeline_steps_table", DataTable)
        table.add_row(step_name, step_description, self.process_separator.join(step_processes))
        self.steps.append((step_name, step_description, step_processes, extra_parameters))
        self.n_steps += 1
        
    def remove_row(self, index: int) -> None:
        """Remove a row from the DataTable by index."""
        self.app.notify(f"Steps before removal: {self.steps}", severity="debug")
        if 0 <= index < len(self.steps):
            self.steps.pop(index)
            self.n_steps -= 1
        self.update_table()

    def update_table(self) -> None:
        """Update the DataTable content based on current steps."""
        table: DataTable = self.query_one("#pipeline_steps_table", DataTable)
        table.clear(columns=True)
        table.add_columns("Name", "Description", "Processes")
        for step in self.steps:
            print(f"Updating table with step: {step}")
            step_name, step_description, step_processes, extra_parameters = step
            processes_str = self.process_separator.join(step_processes)
            table.add_row(step_name, step_description, processes_str)
            
        self.selected_step_index = 0 if self.n_steps > 0 else None
            
    @on(Button.Pressed, "#add_pipeline_step_btn")
    def handle_add_pipeline_step(self) -> None:
        """Handle adding a new pipeline step."""
        self.add_row(f"Step {self.n_steps}", "", [], {})
        
    @on(Button.Pressed, "#remove_pipeline_step_btn")
    def handle_remove_pipeline_step(self) -> None:
        """Handle removing the selected pipeline step."""
        if self.selected_step_index is not None:
            self.remove_row(self.selected_step_index)
            self.selected_step_index = 0 # Reset selection to first row
            
    @on(DataTable.RowSelected, "#pipeline_steps_table")
    def handle_step_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle pipeline step row selection."""
        table: DataTable = self.query_one("#pipeline_steps_table", DataTable)
        self.selected_step_index = table.get_row_index(event.row_key)
        
    @on(Button.Pressed, "#update_pipeline_step_btn")
    def handle_update_pipeline_step(self) -> None:
        """Handle updating the selected pipeline step."""
        if self.selected_step_index is None:
            self.app.notify("No pipeline step selected to update", severity="warning")
            return
        
        step_index = self.selected_step_index
        processes_in_step = self.steps[step_index][2] if len(self.steps) > step_index else []
        
        def update_callback(result: Optional[dict]) -> None:
            if result is None:
                return
            table: DataTable = self.query_one("#pipeline_steps_table", DataTable)
            if 0 <= step_index < table.row_count:
                # Update the step in the internal list
                updated_step = (
                    result["step_name"],
                    result["step_description"],
                    result["processes"],
                    result["extra_parameters"]
                )
                self.steps[step_index] = updated_step
                self.update_table()
        
        self.app.push_screen(
            StepUpdateModal(
                step_name=self.steps[step_index][0],
                step_description=self.steps[step_index][1],
                available_processes=self.available_processes,
                processes=processes_in_step,
            ),
            callback=update_callback
        )

class StepBar(Horizontal):
    """A single step bar showing progress segments."""
    CSS = """
    .step_bar_container {
        height: 3;
        width: 100%;
        margin-bottom: 1;
        border: tall transparent;
    }

    .step_bar_container.failed {
        border: tall red;
    }

    .step_label {
        width: 10%;
        color: white;
        text-align: right;
        padding-right: 1;
    }

    .segment {
        # height: 100%;
        height: 25
    }

    .segment.complete {
        background: green;
    }

    .segment.running {
        background: yellow;
    }

    .segment.not_started {
        background: gray;
    }

    .segment.failed {
        background: red;
    }
    """
    
    def __init__(self, step_index: int, stats: dict):
        super().__init__()
        self.step_index = step_index
        self.stats = stats
        self.id = f"step_bar_{step_index}"
        
    def compose(self) -> ComposeResult:
        total = sum(self.stats.values())
        if total == 0:
            total = 1  # avoid divide-by-zero
        
        failed = self.stats.get("FAILED", 0) > 0
        
        # Compute segment widths proportionally
        segments = []
        for state, color in {
            "COMPLETE": "green",
            "RUNNING": "yellow",
            "NOT_STARTED": "gray",
            "FAILED": "red"
        }.items():
            count = self.stats.get(state, 0)
            width_percent = (count / total) * 100
            if width_percent > 0:
                segments.append((state, color, width_percent))
        
        # Compose horizontally
        with Horizontal(classes=f"step_bar_container{' failed' if failed else ''}"):
            yield Label(f"Step {self.step_index}", classes="step_label")
            for state, color, width in segments:
                static_widget = Static(
                    f"{count if count > 0 else ''}",
                    classes=f"segment {state.lower()}",
                    id=f"segment_{self.step_index}_{state.lower()}",
                )
                static_widget.styles.width = f"{width}%"  # Set width proportionally
                static_widget.styles.background = color
                yield static_widget

class PipelineProgressComponent(Vertical):
    """A component to display and manage pipeline execution progress."""
    CSS = """
    #pipeline_progress_component {
        padding: 1;
        width: 100%;
    }
    """
    
    def __init__(self, pipeline_id: str):
        super().__init__()
        self.id = "pipeline_progress_component"
        
        self.pipeline_id = pipeline_id
        self.pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id)
        self.pipeline_progress: dict = self.pipeline.get_pipeline_status().get_stats("all")
        
    def compose(self) -> ComposeResult:
        """Compose the UI elements of the pipeline progress component."""
        yield Label("Pipeline Progress", id="pipeline_progress_label", classes="list_title")
        for step_idx, stats in self.pipeline_progress.items():
            yield StepBar(step_idx, stats)
    
    def on_mount(self) -> None:
        """Called when the component is mounted."""
        # Periodically refresh progress every 5 seconds
        self.set_interval(5, self.refresh_progress)
            
    def refresh_progress(self) -> None:
        """Refresh the progress display."""
        self.pipeline_progress = self.pipeline.get_pipeline_status().get_stats("all")
        for step_idx, stats in self.pipeline_progress.items():
            step_bar: StepBar = self.query_one(f"#step_bar_{step_idx}", StepBar)
            step_bar.stats = stats
            step_bar.refresh()
        