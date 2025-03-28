from dotenv import load_dotenv
import os

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found in environment variables.")

base_url: str = "https://apimd.mdanderson.edu/dig/llm/llama31-70b/v1/"
default_headers: dict[str, str] = {"Ocp-Apim-Subscription-Key": api_key, "Content-Type": "application/json"}

system_prompt: str = """You are a skilled neuroimaging researcher. You understand how the BIDS format for storing neuroimaging data works."""

