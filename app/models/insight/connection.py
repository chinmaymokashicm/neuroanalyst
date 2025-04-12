from ...utils.constants import *

from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncOpenAI

class LLMConnection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    client: AsyncOpenAI
    provider: OpenAIProvider
    model: OpenAIModel
    
    @classmethod
    def from_defaults(cls) -> "LLMConnection":
        client = AsyncOpenAI(
            base_url=OPENAI_CLIENT_BASE_URL,
            default_headers=OPENAI_CLIENT_DEFAULT_HEADERS
        )
        provider = OpenAIProvider(openai_client=client)
        model = OpenAIModel(OPENAI_DEFAULT_MODEL, provider=provider)
        
        return cls(
            client=client,
            provider=provider,
            model=model
        )