#!/bin/bash
# Run the NeuroAnalyst API server

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Set Python path to include the src directory
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Run the FastAPI server using uvicorn
uvicorn src.neuroanalyst.main:app --reload --host 0.0.0.0 --port 8000