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

class DataSubmitterWidget(Widget):
    """
    Widget to view and edit data, and submit it to the API.
    """
    data: Optional[str] = None
    submit_url: Optional[str] = None
    default_data: Optional[str] = None
    language: Optional[str] = None
    about_text: str = "No additional information available."
    
    def get_default_data(self) -> str:
        """
        Get the default data to display.
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
    
    def __init__(self, data: Optional[str] = None, submit_url: Optional[str] = None, default_data: Optional[str] = None, language: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.default_data = default_data if default_data is not None else self.get_default_data()
        self.language = language if language is not None else "json"
        data = self.default_data if data is None else data
        self.data = data
        submit_url = "https://example.com/api/submit" if submit_url is None else submit_url
        self.submit_url = submit_url
        
    def compose(self) -> ComposeResult:
        """
        Compose the layout of the JSON viewer.
        """
        yield TextArea(
            text=self.data,
            classes="data-input",
            id="data_input",
            language=self.language,
        )
        with Vertical(classes="data-submit-buttons"):
            yield Button("Submit", id="submit-button", classes="data-submit-button")
            yield Button("Reset", id="reset-button", classes="data-submit-button")
            yield Button("Clear", id="clear-button", classes="data-submit-button")
            yield Button("About", id="about-button", classes="data-submit-button")
            yield Button("Save", id="save-button", classes="data-submit-button")
            yield Button("Copy", id="copy-button", classes="data-submit-button")
            
    @on(Button.Pressed, "#submit-button")
    def submit_button(self, event: Button.Pressed):
        # Validate the data if it is JSON
        if self.language == "json":
            try:
                text = self.query_one("#data_input").text
                json.loads(text)
                self.notify("JSON data is valid.", severity="information", title="JSON Validation")
            except json.JSONDecodeError as e:
                self.notify(f"Invalid JSON data: {e}", severity="error", title="JSON Validation")
                return
        
        # Submit POST request to the API
        try:
            form_data_submission: str = json.dumps(json.loads(text)) if self.language == "json" else text
            response = requests.post(self.submit_url, data={"form_data": form_data_submission})
            if response.status_code in [200, 201]:
                self.notify("Data submitted successfully.", severity="information")
            else:
                self.notify(f"Error submitting data: {response.status_code}", severity="error")
                try:
                    pyperclip.copy(response.json())
                    response_dict: dict = json.loads(response.text)
                    self.notify(f"{response_dict["detail"]}", severity="error", title="Submission Error")
                    self.notify("Error response copied to clipboard!", severity="information", title="Submission Error")
                except:
                    self.notify("Tried copying error response. FAILED.", severity="error", title="Submission Error")
        except requests.RequestException as e:
            # self.notify(f"POST Request Error: {e}: {traceback.format_exc()}", severity="error")
            self.notify(f"POST Request Error: {e}", severity="error")
            try:
                pyperclip.copy(response.json())
                self.notify("Error response copied to clipboard!")
            except:
                self.notify("Tried copying error response. FAILED.")
    
    @on(Button.Pressed, "#reset-button")
    def reset_button(self, event: Button.Pressed):
        """
        Reset the data to the default value.
        """
        self.query_one("#data_input").text = self.default_data if self.default_data is not None else self.get_default_data()
        self.notify("Data has been reset to default.", severity="information", title="Reset Data")
        
    @on(Button.Pressed, "#clear-button")
    def clear_button(self, event: Button.Pressed):
        """
        Clear the data.
        """
        self.query_one("#data_input").text = ""
        self.notify("Data has been cleared.", severity="information", title="Clear Data")
    
    @on(Button.Pressed, "#about-button")
    def about_button(self, event: Button.Pressed):
        """
        Show the about text.
        """
        self.notify(self.about_text, severity="information", title="About")
        
    @on(Button.Pressed, "#save-button")
    def save_button(self, event: Button.Pressed):
        """
        Save the data as a checkpoint.
        """
        text = self.query_one("#data_input").text
        if self.language == "json":
            try:
                json.loads(text)
            except json.JSONDecodeError as e:
                self.notify(f"Invalid JSON data: {e}", severity="error", title="JSON Validation")
                return
        self.default_data = text
        self.notify("JSON data has been saved as a checkpoint.", severity="information", title="Save Data")
    
    @on(Button.Pressed, "#copy-button")
    def copy_button(self, event: Button.Pressed):
        """
        Copy the data to the clipboard.
        """
        text = self.query_one("#data_input").text
        try:
            pyperclip.copy(text)
            self.notify("Data has been copied to the clipboard.", severity="information", title="Copy Data")
        except Exception as e:
            self.notify(f"Error copying data: {e}", severity="error", title="Copy Data")