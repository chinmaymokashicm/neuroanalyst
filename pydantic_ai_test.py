from dotenv import load_dotenv
import os, httpx
import nest_asyncio
from typing import Optional

from imagelib.datasets.bids import BIDSTree, SelectBIDSDatasetInfo

from pydantic import BaseModel, Field
from bids import BIDSLayout
from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from openai import AsyncOpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(
    base_url="https://apimd.mdanderson.edu/dig/llm/llama31-70b/v1/",
    # api_key="unused",
    default_headers={"Ocp-Apim-Subscription-Key": api_key, "Content-Type": "application/json"},
)
provider = OpenAIProvider(openai_client=client)
model = OpenAIModel("meta-llama/Llama-3.1-70B-Instruct", provider=provider)

class UserInput(BaseModel):
    bids_root: str = Field(description="The root directory of the BIDS dataset")
    markdown: str = Field(description="The path to the markdown file containing the BIDS specification")

class BIDSDatasetInfo(BaseModel):
    dataset_name: str = Field(description="The name of the dataset. This should be a human-readable name that describes the dataset.")
    dataset_description: str = Field(description="A description of the dataset. This should include information about the data, its purpose, and any relevant details.")
    analysis_description: str = Field(description="A description of the analysis performed on the dataset. This should include information about the methods used, the results obtained, and any relevant details.")
    analysis_results: str = Field(description="The results of the analysis performed on the dataset. This should include any relevant metrics, visualizations, or other information that summarizes the results.")
    detailed_summary: str = Field(description="A detailed summary of the dataset and analysis. This should include any relevant information that is not covered in the other fields, such as limitations, future work, or other details.")

bids_specification_md_filepath: str = "bids_specification.md"
# bids_agent_system_prompt = f"""You are an expert in the BIDS (Brain Imaging Data Structure) format. 
# You are tasked with answering questions about the BIDS specification and providing information about datasets that follow this format.
# You have access to the BIDS specification documentation at {bids_specification_md_filepath} and a dataset tree that contains information about BIDS datasets.
# You can use this information to read and understand the BIDS specification and provide accurate answers to questions about it.

# You should follow these steps -
# 1. Load the BIDS specification documentation from the markdown file.
# 2. Load the dataset from the path provided by the user.
# 4. Analyze the dataset and provide a detailed summary of its contents, according to the structured output specification.
# """

bids_agent_system_prompt = f"""You are an expert in the BIDS (Brain Imaging Data Structure) format.
You are tasked with answering questions about a BIDS dataset, including its structure, contents, and pipelines.
You are provided with a BIDSTree object that contains information about the BIDS dataset. Interpret and analyze it.
"""

bids_agent: Agent = Agent(
    model=model,
    system_prompt=bids_agent_system_prompt,
    result_type=BIDSDatasetInfo,
    deps_type=BIDSTree,
    retries=3
)

# @bids_agent.tool_plain
# def load_bids_dataset(bids_root: str) -> BIDSLayout:
#     """
#     Load the BIDS dataset.
#     """
#     layout = BIDSLayout(bids_root)
#     # bids_tree = BIDSTree(layout)
#     return layout

# @bids_agent.tool_plain
# def read_markdown_file(filepath: str) -> str:
#     """
#     Read a markdown file and return its content.
#     """
#     with open(filepath, "r") as file:
#         content = file.read()
#     return content

bids_root: str = "/Users/cmokashi/data/bids_datasets/open_neuro/ds005596-1.1.1"

usage_limits = UsageLimits(
    request_tokens_limit=4000,
    response_tokens_limit=5000,
    total_tokens_limit=9000,
)

result = bids_agent.run_sync(
    user_prompt="Tell me about this dataset.",
    # deps=UserInput(
    #     bids_root=bids_root,
    #     markdown=bids_specification_md_filepath
    # ),
    deps=BIDSTree.from_path(bids_root),
    # usage_limits=usage_limits,
)

# print(result.data.model_dump_json(indent=4))
# print(result.all_messages_json(indent=4))

print(result.data)