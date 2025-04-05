"""
Edit pretty JSON to submit to the API.
"""
import json, requests, traceback
from typing import Optional

from textual import on, log
from textual.app import ComposeResult, RenderResult
from textual.widget import Widget
from textual.containers import Vertical
from textual.widgets import Input, Button, TextArea
import pyperclip

class JSONViewerWidget(Widget):
    """
    Widget to view and edit JSON data, and submit it to the API.
    """
    json_data: Optional[str] = None
    submit_url: Optional[str] = None
    default_json_data: Optional[str] = None
    about_text: str = "No additional information available."
    
    def get_default_json(self) -> str:
        """
        Get the default JSON data to display.
        """
        default_dict = {
            "name": "example",
            "description": "example description",
            "parameters": {
                "param1": "value1",
                "param2": "value2"
            }
        }
        default_json = json.dumps(default_dict, indent=4)
        return default_json
    
    def __init__(self, json_data: Optional[str] = None, submit_url: Optional[str] = None, default_json_data: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.default_json_data = default_json_data if default_json_data is not None else self.get_default_json()
        json_data = self.default_json_data if json_data is None else json_data
        self.json_data = json_data
        submit_url = "https://example.com/api/submit" if submit_url is None else submit_url
        self.submit_url = submit_url
        # self.is_build_pipeline = is_build_pipeline
        
    def compose(self) -> ComposeResult:
        """
        Compose the layout of the JSON viewer.
        """
        yield TextArea(
            text=self.json_data,
            classes="json-input",
            id="json_input",
            language="json",
        )
        with Vertical(classes="json-submit-buttons"):
            yield Button("Submit", id="submit-button", classes="json-submit-button")
            yield Button("Reset", id="reset-button", classes="json-submit-button")
            yield Button("Clear", id="clear-button", classes="json-submit-button")
            yield Button("About", id="about-button", classes="json-submit-button")
            yield Button("Save", id="save-button", classes="json-submit-button")
            yield Button("Copy", id="copy-button", classes="json-submit-button")
            
    @on(Button.Pressed, "#submit-button")
    def submit_button(self, event: Button.Pressed):
        # Validate the JSON data
        try:
            text = self.query_one("#json_input").text
            json.loads(text)
            self.notify("JSON data is valid.", severity="information")
        except json.JSONDecodeError as e:
            self.notify(f"Invalid JSON data: {e}", severity="error")
            return
        
        # Submit POST request to the API
        try:
            # response = requests.post(self.submit_url, json=json.loads(text))
            response = requests.post(self.submit_url, data={"form_data": json.dumps(json.loads(text))})
            if response.status_code in [200, 201]:
                self.notify("JSON data submitted successfully.", severity="information")
            else:
                self.notify(f"Error submitting JSON data: {response.status_code}", severity="error")
                try:
                    pyperclip.copy(response.json())
                    response_dict: dict = json.loads(response.text)
                    self.notify(f"{response_dict["detail"]}", severity="error")
                    self.notify("Error response copied to clipboard!")
                except:
                    self.notify("Tried copying error response. FAILED.")
        except requests.RequestException as e:
            # self.notify(f"POST Request Error: {e}: {traceback.format_exc()}", severity="error")
            self.notify(f"POST Request Error: {e}", severity="error")
            # self.notify(traceback.extract_stack().__str__)
            try:
                pyperclip.copy(response.json())
                # self.notify("Error response copied to clipboard!")
            except:
                self.notify("Tried copying error response. FAILED.")
    
    @on(Button.Pressed, "#reset-button")
    def reset_button(self, event: Button.Pressed):
        """
        Reset the JSON data to the default value.
        """
        self.query_one("#json_input").text = self.default_json_data if self.default_json_data is not None else self.get_default_json()
        self.notify("JSON data has been reset to default.", severity="information")
        
    @on(Button.Pressed, "#clear-button")
    def clear_button(self, event: Button.Pressed):
        """
        Clear the JSON data.
        """
        self.query_one("#json_input").text = ""
        self.notify("JSON data has been cleared.", severity="information")
    
    @on(Button.Pressed, "#about-button")
    def about_button(self, event: Button.Pressed):
        """
        Show the about text.
        """
        self.notify(self.about_text, severity="information")
        
    @on(Button.Pressed, "#save-button")
    def save_button(self, event: Button.Pressed):
        """
        Save the JSON data as a checkpoint.
        """
        text = self.query_one("#json_input").text
        try:
            json.loads(text)
            self.default_json_data = text
            # self.notify("JSON data has been saved as a checkpoint.", severity="information")
        except json.JSONDecodeError as e:
            self.notify(f"Invalid JSON data: {e}", severity="error")
    
    @on(Button.Pressed, "#copy-button")
    def copy_button(self, event: Button.Pressed):
        """
        Copy the JSON data to the clipboard.
        """
        text = self.query_one("#json_input").text
        try:
            pyperclip.copy(text)
            self.notify("JSON data has been copied to the clipboard.", severity="information")
        except Exception as e:
            self.notify(f"Error copying JSON data: {e}", severity="error")