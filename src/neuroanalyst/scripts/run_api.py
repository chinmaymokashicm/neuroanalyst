#!/usr/bin/env python
"""
Run the NeuroAnalyst API server.

This script starts the FastAPI application using uvicorn.
"""

import uvicorn
import argparse
from ..routes import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the NeuroAnalyst API server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")
    
    args = parser.parse_args()
    
    print(f"Starting NeuroAnalyst API server on {args.host}:{args.port}")
    uvicorn.run("src.neuroanalyst.routes:app", host=args.host, port=args.port, reload=args.reload)
