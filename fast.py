from app.routes.process import image, exec, workdir
from app.routes import pipeline
from app.routes.utils import log_reader
from app.utils.constants import *
from app.utils.envs import set_neuroanalyst_root_dirs
from app.routes.utils import AppTypeEnum

import asyncio, logging, os, json
from pathlib import Path

from fastapi import FastAPI, WebSocket, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

set_neuroanalyst_root_dirs()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(FASTAPI_LOGS_FILEPATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
app.include_router(image.router, prefix="/process/image", tags=["process", "image"])
app.include_router(exec.router, prefix="/process/exec", tags=["process", "exec"])
app.include_router(workdir.router, prefix="/process/workdir", tags=["workdir"])

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
    logging.info("Hello World")
    return {"message": "Hello World"}

@app.websocket("/ws/log")
async def stream(websocket: WebSocket, app_type: AppTypeEnum = Query(...)):
    logger.info(f"Loading logs for {app_type.value}")
    last_line_number: int = 0
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(1)
            log_filepath: str = os.path.join(os.getenv(ENV_NEUROANALYST_LOGS), f"{app_type.value}.log")
            logs = await log_reader(log_filepath, start_line=last_line_number)
            last_line_number += len(logs)  # Update the last line number
            await websocket.send_text("\n".join(logs))
    except Exception as e:
        logging.error(f"Websocket closed. Error: {e}")
        await websocket.close()
    finally:
        logging.info("Websocket closed.")
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, log_level="trace", port=FASTAPI_PORT, reload=True)