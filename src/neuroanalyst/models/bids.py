from typing import List, Optional, Dict

from pydantic import BaseModel, Field

class BIDSGeneratedByToolInfo(BaseModel):
    """Tool information for BIDS dataset_description.json GeneratedBy field."""
    Name: str = Field(..., description="Name of the tool that generated this dataset")
    Version: str = Field(..., description="Version of the tool")
    CodeURL: Optional[str] = Field(default=None, description="URL where the code for the tool can be found")
    Container: Optional[Dict[str, str]] = Field(default=None, description="Container information")


class BIDSDatasetDescription(BaseModel):
    """
    BIDS dataset_description.json model as per BIDS specification.
    
    This model ensures all required fields are present according to BIDS spec.
    Reference: https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html#dataset_descriptionjson
    """
    Name: str = Field(..., description="Name of the dataset")
    BIDSVersion: str = Field("1.8.0", description="The version of the BIDS standard that was used")
    DatasetType: str = Field("derivative", description="Type of the dataset, must be 'derivative' for processed data")
    GeneratedBy: List[BIDSGeneratedByToolInfo] = Field(
        ..., 
        description="A list of tools that generated this dataset"
    )
    
    # Optional fields
    License: Optional[str] = Field(default=None, description="The license for the dataset")
    Authors: Optional[List[str]] = Field(default=None, description="List of individuals who contributed to the dataset")
    Acknowledgements: Optional[str] = Field(default=None, description="Text acknowledging contributions of individuals or institutions")
    HowToAcknowledge: Optional[str] = Field(default=None, description="Instructions on how to acknowledge this dataset")
    Funding: Optional[List[str]] = Field(default=None, description="List of funding sources")
    EthicsApprovals: Optional[List[str]] = Field(default=None, description="List of ethics committee approvals")
    ReferencesAndLinks: Optional[List[str]] = Field(default=None, description="List of references and links")
    DatasetDOI: Optional[str] = Field(default=None, description="The DOI of the dataset if available")
    PipelineDescription: Optional[str] = Field(default=None, description="Description of the processing pipeline applied to the dataset")
    PipelineSteps: Optional[List[str]] = Field(default=None, description="Description of the processing steps applied to the dataset")
    
    class Config:
        extra = "allow"  # Allow additional fields for forward compatibility