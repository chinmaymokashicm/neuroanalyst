from .....utils.constants import *

import json, requests, asyncio, websockets

from textual import on, log
from textual.app import App, ComposeResult
from textual.widgets import Static, TextArea
from textual.widget import Widget
from textual.containers import ScrollableContainer
from textual.message import Message
import pyperclip

class LineUpdate(Message):
    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        super().__init__()

class StreamingLogWidget(Widget):
    app_type: str
    
    def __init__(self, app_type: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.app_type = app_type
        self.stream_area = None
        self.last_file_position = 0
    
    def compose(self) -> ComposeResult:
        yield ScrollableContainer(TextArea(id="stream_area", classes="stream-area", language="html"), classes="stream-container")

    async def on_mount(self) -> None:
        self.stream_area = self.query_one("#stream_area", TextArea)
        asyncio.create_task(self.stream_log(self.app_type))
        # Schedule initial scroll after the first render.
        # self.set_timer(2, self.scroll_to_bottom)
    
    async def scroll_to_bottom(self) -> None:
        self.query_one(ScrollableContainer).y = self.query_one("#stream_area").virtual_size.height
        self.notify("Scrolled to bottom", severity="info", title="Info")

    async def stream_log(self, app_type: str) -> None:
        uri = f"ws://{FASTAPI_HOSTNAME}:{FASTAPI_PORT}/ws/log?app_type={app_type}"
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    message = await websocket.recv()
                    lines = message.splitlines()
                    lines.reverse()
                    # Add space between lines
                    lines = [line + "\n" for line in lines]
                    # last_line_number += len(lines)
                    if lines:
                        self.post_message(LineUpdate(lines))
                    await asyncio.sleep(0.1) # Check every 0.1 seconds
        except websockets.exceptions.ConnectionClosed as e:
            # self.stream_area.update(f"WebSocket connection closed: {str(e)}")
            self.stream_area.text = f"WebSocket connection closed: {str(e)}"
            self.notify(f"WebSocket connection closed: {str(e)}", severity="error", title="Error")
            # pyperclip.copy(str(e))
        except json.JSONDecodeError as e:
            self.stream_area.text = f"JSON Decode Error: {str(e)}"
            self.notify(f"JSON Decode Error: {str(e)}", severity="error", title="Error")
            # pyperclip.copy(str(e))
        except Exception as e:
            # self.stream_area.update(f"An error occurred: {str(e)}")
            self.stream_area.text = f"An error occurred: {str(e)}"
            self.notify(f"An error occurred: {str(e)}", severity="error", title="Error")
            # pyperclip.copy(str(e))

    async def on_line_update(self, message: LineUpdate) -> None:
        self.stream_area.text += "".join(message.lines)
        self.query_one(ScrollableContainer).y = self.stream_area.styles.height  # Scroll to the bottom