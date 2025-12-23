"""
Module working with extracting information from BIDS datasets.
"""
from src.neuroanalyst.models import NeuPipeline
from src.neuroanalyst.models.pipeline.constructor import PipelineConstructorConfig

from pathlib import Path
import os, sys, json

sys.path.append(str(Path(__file__).parents[3]))

from typing import Optional
from enum import Enum

from bids.layout import BIDSLayout
from bids.layout import parse_file_entities
from pydantic import BaseModel, Field, DirectoryPath, ConfigDict
import networkx as nx

class BIDSSidecarType(str, Enum):
    RAW = "raw"
    DERIVATIVE = "derivative"

class BIDSSidecarInfo(BaseModel):
    filepath: str = Field(..., description="Filepath to the BIDS sidecar JSON file.")
    entities: dict = Field(..., description="BIDS entities extracted from the sidecar filename.")
    sidecar_type: BIDSSidecarType = Field(..., description="Type of BIDS sidecar (raw).")
    subject_id: Optional[str] = Field(default=None, description="Subject ID if available.")
    session_id: Optional[str] = Field(default=None, description="Session ID if available.")
    
class RawBIDSSidecarInfo(BIDSSidecarInfo):
    sidecar_type: BIDSSidecarType = Field(default=BIDSSidecarType.RAW, description="Type of BIDS sidecar (raw).")
    dicom_headers: Optional[dict] = Field(default=None, description="DICOM headers if available.")
    
    @classmethod
    def from_filepath(cls, filepath: str) -> "RawBIDSSidecarInfo":
        entities = parse_file_entities(filepath)
        subject_id = entities.get("subject", None)
        session_id = entities.get("session", None)
        with open(filepath, 'r') as f:
            dicom_headers = json.load(f)
        return cls(
            filepath=filepath,
            entities=entities,
            subject_id=subject_id,
            session_id=session_id,
            dicom_headers=dicom_headers
        )
    
class DerivativeBIDSSidecarInfo(BIDSSidecarInfo):
    sidecar_type: BIDSSidecarType = Field(default=BIDSSidecarType.DERIVATIVE, description="Type of BIDS sidecar (derivative).")
    pipeline_id: str = Field(..., description="Pipeline ID associated with this derivative sidecar.")
    process_exec_id: str = Field(..., description="Process execution ID associated with this derivative sidecar.")
    process_id: str = Field(..., description="Process ID associated with this derivative sidecar.")
    input_file: str = Field(..., description="Input file from which this derivative was generated.")
    provenance: Optional[dict] = Field(default=None, description="Provenance information if available.")
    metrics: Optional[dict] = Field(default=None, description="Metrics information if available.")
    output_entities: Optional[dict] = Field(default=None, description="Output BIDS entities if available.")
    
    @classmethod
    def from_filepath(cls, filepath: str) -> "DerivativeBIDSSidecarInfo":
        entities = parse_file_entities(filepath)
        subject_id = entities.get("subject", None)
        session_id = entities.get("session", None)
        with open(filepath, 'r') as f:
            sidecar_data = json.load(f)
        metrics = sidecar_data.get("metrics", None)
        output_entities = sidecar_data.get("OutputEntities", None)
        pipeline_id = sidecar_data.get("PipelineID", "unknown_pipeline")
        process_exec_id = sidecar_data.get("ProcessExecID", "unknown_process_exec")
        process_id = sidecar_data.get("ProcessID", "unknown_process")
        input_file = sidecar_data.get("InputFile", "unknown_input_file")
        # Provenance would be everything else in the sidecar except metrics, output entities, and IDs
        provenance = {k: v for k, v in sidecar_data.items() if k not in ["metrics", "OutputEntities", "InputFile", "PipelineID", "ProcessExecID", "ProcessID"]}

        return cls(
            filepath=filepath,
            entities=entities,
            subject_id=subject_id,
            session_id=session_id,
            provenance=provenance,
            metrics=metrics,
            output_entities=output_entities,
            pipeline_id=pipeline_id,
            process_exec_id=process_exec_id,
            process_id=process_id,
            input_file=input_file
        )

class ProcessInfo(BaseModel):
    process_id: str = Field(..., description="Process ID.")
    process_exec_ids: list[str] = Field(..., description="List of process execution IDs for this process.")

class PipelineStepInfo(BaseModel):
    step_name: str = Field(..., description="Name of the pipeline step.")
    step_description: Optional[str] = Field(default=None, description="Description of the pipeline step.")
    processes: list[ProcessInfo] = Field(..., description="List of process executions in this step.")

class PipelineProvenanceInfo(BaseModel):
    pipeline_id: str = Field(..., description="Pipeline ID.")
    pipeline_name: str = Field(..., description="Name of the pipeline.")
    steps: list[PipelineStepInfo] = Field(..., description="List of steps in the pipeline.")

class BIDSDerivativeInfo(BaseModel):
    name: str = Field(..., description="Name of the BIDS derivative.")
    description: dict = Field(..., description="Contents of the dataset_description.json file for the derivative.")
    sidecars: Optional[list[DerivativeBIDSSidecarInfo]] = Field(default=None, description="List of BIDS sidecar files in the derivative.")
    readme: Optional[str] = Field(default=None, description="Contents of the README file if present.")
    pipeline_id: str = Field(..., description="Pipeline ID associated with the derivative.")
    pipeline_provenance: dict = Field(..., description="Provenance information of the pipeline that generated the derivative.")

class BIDSDatasetInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    root: DirectoryPath = Field(..., description="Root directory of the BIDS dataset.")
    layout: BIDSLayout = Field(..., description="BIDSLayout object representing the dataset structure.")
    description: dict = Field(..., description="Contents of the dataset_description.json file.")
    derivatives: Optional[list[BIDSDerivativeInfo]] = Field(default=None, description="List of BIDS derivatives in the dataset.")
    readme: Optional[str] = Field(default=None, description="Contents of the README file if present.")
    sidecars: Optional[list[RawBIDSSidecarInfo]] = Field(default=None, description="List of BIDS sidecar files in the dataset.")
    graph: Optional[nx.DiGraph] = Field(default=None, description="Provenance graph of the dataset if constructed.")
    
    @classmethod
    def from_root(cls, root_path: str) -> "BIDSDatasetInfo":
        layout = BIDSLayout(root_path, validate=False, derivatives=True)
        # Load dataset_description.json
        description_path = os.path.join(root_path, "dataset_description.json")
        with open(description_path, 'r') as f:
            description = json.load(f)
        
        # Load README if exists
        readme_path = os.path.join(root_path, "README")
        readme = None
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                readme = f.read()
        
        # Load raw sidecars
        raw_sidecars = []
        for filepath in layout.get(scope="raw", extension=".json", return_type="file"):
            if Path(filepath).name == "dataset_description.json":
                continue  # Skip dataset_description.json
            raw_sidecar = RawBIDSSidecarInfo.from_filepath(filepath)
            raw_sidecars.append(raw_sidecar)
        
        # Load derivatives
        derivatives_info = []
        for derivative_name in layout.derivatives.keys():
            derivative_path = os.path.join(root_path, "derivatives", derivative_name)
            derivative_layout = BIDSLayout(derivative_path, validate=False)
            
            # Load derivative dataset_description.json
            derivative_description_path = os.path.join(derivative_path, "dataset_description.json")
            with open(derivative_description_path, 'r') as f:
                derivative_description = json.load(f)
            
            # Load derivative README if exists
            derivative_readme_path = os.path.join(derivative_path, "README")
            derivative_readme = None
            if os.path.exists(derivative_readme_path):
                with open(derivative_readme_path, 'r') as f:
                    derivative_readme = f.read()
            
            # Load derivative sidecars
            derivative_sidecars = []
            for filepath in derivative_layout.get(extension=".json", return_type="file"):
                if Path(filepath).name == "dataset_description.json":
                    continue  # Skip dataset_description.json
                if Path(filepath).name.endswith("_sidecar.json"):
                    continue  # Skip sidecar files meant for other purposes
                derivative_sidecar = DerivativeBIDSSidecarInfo.from_filepath(filepath)
                derivative_sidecars.append(derivative_sidecar)
            
            # Extract pipeline ID from the first derivative sidecar if available
            pipeline_id = None
            if derivative_sidecars:
                pipeline_id = derivative_sidecars[0].pipeline_id
            else:
                pipeline_id = "unknown_pipeline"
                
            # Extract pipeline provenance from dataset_description if available
            pipeline_name: str = derivative_description.get("Name", "unknown_pipeline")
            steps: list[PipelineStepInfo] = []
            for step in derivative_description.get("PipelineSteps", []):
                step_name = step.get("name", "unknown_step")
                step_description = step.get("description", None)
                process_ids: set[str] = {value for key, value in step.get("processes", {}).items()}
                processes: list[ProcessInfo] = []
                for process_id in process_ids:
                    process_exec_ids = [key for key, value in step.get("processes", {}).items() if value == process_id]
                    process_info = ProcessInfo(
                        process_id=process_id,
                        process_exec_ids=process_exec_ids
                    )
                    processes.append(process_info)
                step_info = PipelineStepInfo(
                    step_name=step_name,
                    step_description=step_description,
                    processes=processes
                )
                steps.append(step_info)
                
            pipeline_provenance = PipelineProvenanceInfo(
                pipeline_id=pipeline_id,
                pipeline_name=pipeline_name,
                steps=steps
            )
            
            derivative_info = BIDSDerivativeInfo(
                name=derivative_name,
                description=derivative_description,
                sidecars=derivative_sidecars,
                readme=derivative_readme,
                pipeline_id=pipeline_id,
                pipeline_provenance=pipeline_provenance.dict()
            )
            derivatives_info.append(derivative_info)
            
        try:
            constructor: PipelineConstructorConfig = PipelineConstructorConfig.from_pipeline(NeuPipeline.from_pipeline_id(pipeline_id))
            constructor.construct_graph()
            graph = constructor.graph
        except Exception as e:
            print(f"Failed to construct provenance graph for dataset at {root_path}: {e}")
            graph = None
            
        return cls(
            root=Path(root_path),
            layout=layout,
            description=description,
            derivatives=derivatives_info,
            readme=readme,
            sidecars=raw_sidecars,
            graph=graph
        )
        
# class BIDSSubject(BaseModel)