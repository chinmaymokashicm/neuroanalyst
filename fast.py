# from lib.api.process import image, exec
# from lib.api import pipeline
# from lib.api.utils import log_reader
from app.routes.process import image, exec
from app.routes import pipeline
from app.routes.utils import log_reader

import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
app.include_router(image.router, prefix="/process/image", tags=["process", "image"])
app.include_router(exec.router, prefix="/process/exec", tags=["process", "exec"])

# app.mount("/static", StaticFiles(directory="logs/templates/", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# @app.websocket("/ws/log")
# async def stream(websocket: WebSocket, ):
#     await websocket.accept()
#     try:
#         while True:
#             await asyncio.sleep(1)
#             logs = await log_reader("logs/app.log")
#             await websocket.send_text("".join(logs))
#     except Exception as e:
#         await websocket.close()
#         print(f"Websocket closed. Error: {e}")
#     finally:
#         await websocket.close()
#         print("Websocket closed.")