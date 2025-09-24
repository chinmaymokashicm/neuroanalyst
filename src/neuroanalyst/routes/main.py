"""
NeuroAnalyst Web API

This module defines the main FastAPI application for the NeuroAnalyst framework.
It provides endpoints to interact with the NeuroAnalyst components such as NeuProcesses,
NeuPipelines, and their executions.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from .logic import router as logic_router
from .process_dir import router as process_dir_router
from .process import router as process_router
from .process_exec import router as process_exec_router
from .pipeline import router as pipeline_router
from .dataset import router as dataset_router
from .bids import router as bids_router
from .file import router as file_router

# Create FastAPI app
app = FastAPI(
    title="NeuroAnalyst API",
    description="API for the NeuroAnalyst framework that enables neuroimaging data processing pipelines",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(logic_router, prefix="/logic", tags=["Logic"])
app.include_router(process_dir_router, prefix="/dir", tags=["NeuProcessDir"])
app.include_router(process_router, prefix="/process", tags=["NeuProcess"])
app.include_router(process_exec_router, prefix="/process/exec", tags=["NeuProcessExec"])
app.include_router(pipeline_router, prefix="/pipeline", tags=["NeuPipeline"])
app.include_router(dataset_router, prefix="/dataset", tags=["Dataset"])
app.include_router(bids_router, prefix="/bids", tags=["BIDS"])
app.include_router(file_router, prefix="/file", tags=["File"])

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that returns a welcome message and basic information about the API.
    """
    return {
        "message": "Welcome to the NeuroAnalyst API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Run the app if executed directly
if __name__ == "__main__":
    uvicorn.run("src.neuroanalyst.routes.main:app", host="0.0.0.0", port=8000, reload=True)
