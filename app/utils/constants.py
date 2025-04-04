import os
from dotenv import load_dotenv

load_dotenv()

# DB Connection
MONGO_URI: str = "mongodb://localhost:27017/"
DB_NAME: str = "neuroanalyst"

# DB Collections
COLLECTION_PROCESS_IMAGES: str = "process_images"
COLLECTION_PROCESS_EXECS: str = "process_execs"
COLLECTION_PIPELINES: str = "pipelines"
COLLECTION_SUMMARIES: str = "summaries"

# Directory paths
TEMPLATES_DIR: str = "docs/templates"

# Default values
DEFAULT_CONTAINER_ENVS: list[str] = ["DERIVATIVES", "BIDS_FILTERS", "PIPELINE_NAME", "OVERWRITE", "PROCESS_ID", "PROCESS_EXEC_ID", "PIPELINE_ID"]

# Environment variable names
ENV_NEUROANALYST_HOME: str = "NEUROANALYST_HOME"
ENV_NEUROANALYST_IMAGES: str = "NEUROANALYST_IMAGES"
ENV_NEUROANALYST_DOCS: str = "NEUROANALYST_DOCS"
ENV_NEUROANALYST_WORKDIR: str = "NEUROANALYST_WORKDIR"
ENV_NEUROANALYST_REPORTS: str = "NEUROANALYST_REPORTS"

# Insight API
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
OPENAI_CLIENT_BASE_URL: str = "https://apimd.mdanderson.edu/dig/llm/llama31-70b/v1/"
OPENAI_CLIENT_DEFAULT_HEADERS: dict = {"Ocp-Apim-Subscription-Key": OPENAI_API_KEY, "Content-Type": "application/json"}
OPENAI_DEFAULT_MODEL: str = "meta-llama/Llama-3.1-70B-Instruct"
SYSTEM_PROMPTS_PATH: str = "app/models/insight/prompts"


# Textual CSS
TEXTUAL_LAYOUT_MAIN_CSS_PATH: str = "app/frontend/textual/css/layouts/main.tcss"
TEXTUAL_LAYOUT_RESOURCE_CSS_PATH: str = "app/frontend/textual/css/layouts/resource.tcss"