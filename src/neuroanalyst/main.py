"""
NeuroAnalyst API Server

This module sets up the FastAPI application for the NeuroAnalyst framework.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from neuroanalyst.routes import process_router, pipeline_router, logic_router, logs_router, datasets_router

app = FastAPI(
    title="NeuroAnalyst API",
    description="API for the NeuroAnalyst framework for neuroimaging data processing",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(process_router, prefix="/api/v1", tags=["process"])
app.include_router(pipeline_router, prefix="/api/v1", tags=["pipeline"])
app.include_router(logic_router, prefix="/api/v1", tags=["logic"])
app.include_router(logs_router, prefix="/api/v1", tags=["logs"])
app.include_router(datasets_router, prefix="/api/v1", tags=["datasets"])

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint that returns basic information about the API.
    """
    return {
        "message": "Welcome to the NeuroAnalyst API",
        "version": app.version,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)