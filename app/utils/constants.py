import os
from dotenv import load_dotenv

load_dotenv()

# Environment variable names
ENV_NEUROANALYST_HOME: str = "NEUROANALYST_HOME"
ENV_NEUROANALYST_IMAGES: str = "NEUROANALYST_IMAGES"
ENV_NEUROANALYST_DOCS: str = "NEUROANALYST_DOCS"
ENV_NEUROANALYST_WORKDIR: str = "NEUROANALYST_WORKDIR"
ENV_NEUROANALYST_REPORTS: str = "NEUROANALYST_REPORTS"
ENV_NEUROANALYST_LOGS: str = "NEUROANALYST_LOGS"
ENV_NEUROANALYST_DATASETS: str = "NEUROANALYST_DATASETS"

# DB Connection
MONGO_URI: str = "mongodb://localhost:27017/"
DB_NAME: str = "neuroanalyst"

# Fast API
FASTAPI_HOSTNAME: str = "localhost"
FASTAPI_PORT: str = 3001
FASTAPI_LOGS_FILENAME: str = "fastapi.log"
FASTAPI_LOGS_FILEPATH: str = os.path.join(os.getenv(ENV_NEUROANALYST_LOGS), FASTAPI_LOGS_FILENAME)

# DB Collections
COLLECTION_PROCESS_IMAGES: str = "process_images"
COLLECTION_PROCESS_EXECS: str = "process_execs"
COLLECTION_PIPELINES: str = "pipelines"
COLLECTION_SUMMARIES: str = "summaries"

# Directory paths
TEMPLATES_DIR: str = "docs/templates"

# Default values
DEFAULT_CONTAINER_ENVS: list[str] = ["DERIVATIVES", "BIDS_FILTERS", "PIPELINE_NAME", "OVERWRITE", "PROCESS_ID", "PROCESS_EXEC_ID", "PIPELINE_ID"]

# Redis broker (locally-running, on a HPC)
REDIS_BROKER_URL = "redis://localhost:6379/0"

# Insight API
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
OPENAI_CLIENT_BASE_URL: str = "https://apimd.mdanderson.edu/dig/llm/llama31-70b/v1/"
OPENAI_CLIENT_DEFAULT_HEADERS: dict = {"Ocp-Apim-Subscription-Key": OPENAI_API_KEY, "Content-Type": "application/json"}
OPENAI_DEFAULT_MODEL: str = "meta-llama/Llama-3.1-70B-Instruct"
SYSTEM_PROMPTS_PATH: str = "app/models/insight/prompts"

# Textual
TEXTUAL_LAYOUT_MAIN_CSS_PATH: str = "app/frontend/textual/css/layouts/main.tcss"
TEXTUAL_LAYOUT_RESOURCE_CSS_PATH: str = "app/frontend/textual/css/layouts/resource.tcss"

with open("docs/references/about_textual_app.md", "r") as f:
    TEXTUAL_ABOUT_TEXT: str = f.read()
# TEXTUAL_ABOUT_TEXT: str = ""
TEXTUAL_LEFT_WELCOME_TEXT: str = """Submit Jobs
- Creating new Process definitions via JSON input
- Instantiating ProcessExecs from Processes with parameter specifications
- Building Pipelines by chaining ProcessExecs
- Submitting user queries to the Insight API for LLM-powered knowledge discovery
"""
TEXTUAL_RIGHT_WELCOME_TEXT: str = """Visualization
- Lists of all defined Processes, ProcessExecs, and Pipelines
- Detailed view of selected items, including parameter values and status
- Results metrics and analysis outputs
- Responses from the LLM-powered Insight API"""