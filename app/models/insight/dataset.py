from .connection import LLMConnection
from ...utils.db import Connection
from ...utils.constants import *

from pathlib import Path, PosixPath

from pydantic import BaseModel, Field, DirectoryPath
from pydantic_ai import Agent
import pandas as pd

class BIDSPipeline(BaseModel):
    name: str = Field(description="Name of the pipeline")
    description: str = Field(description="Description of the dataset if available in dataset")
    outputs: list[str] = Field(description="Types of outputs generated.")
    subjects: list[str] = Field(description="Subjects present in this pipeline.")
    summary: str = Field(description="Detailed summary of the pipeline after analyzing all the available data.")

class BIDSDataset(BaseModel):
    root_dir: DirectoryPath = Field(description="Root of the BIDS dataset.")
    participants: pd.DataFrame = Field(description="Information loaded from participants.tsv or similar. Demographic and behavioral information of the subjects.")
    datatypes: list[str] = Field(description="Different datatypes available in the dataset.")
    pipelines: list[BIDSPipeline] = Field(description="Available pipelines.")
    subjects: list[str] = Field(description="Subjects present in this pipeline.")
    summary: str = Field(description="Detailed summary of the dataset after analyzing the information in the raw dataset and then its derivatives.")
    
with open(Path(SYSTEM_PROMPTS_PATH) / "data.txt", "r") as f:
    data_system_prompt: str = f.read()
    
connection: LLMConnection = LLMConnection.from_defaults()

data_agent: Agent = Agent(model=connection.model, system_prompt=data_system_prompt)

@data_agent.tool_plain
def get_datasets() -> list[str]:
    """
    Fetch all datasets that were used for analysis.
    """
    connection: Connection = Connection.from_defaults()
    