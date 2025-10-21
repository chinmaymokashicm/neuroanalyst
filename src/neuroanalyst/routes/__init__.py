"""
NeuroAnalyst API Routes

This module contains the routers for the NeuroAnalyst API endpoints.
"""
from neuroanalyst.routes.process import router as process_router
from neuroanalyst.routes.pipeline import router as pipeline_router
from neuroanalyst.routes.logic import router as logic_router
from neuroanalyst.routes.logs import router as logs_router
from neuroanalyst.routes.datasets import router as datasets_router

__all__ = ["process_router", "pipeline_router", "logic_router", "logs_router", "datasets_router"]
