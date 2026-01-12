from ..bids import BIDSDatasetDescription
from .core import KGGraph, KGNode, KGEdge
from ..process.process.core import NeuProcess
from ..process.logic.core import NeuProcessLogic, Metric

from typing import Optional, Self
from pathlib import Path
import json

from pydantic import BaseModel, Field, DirectoryPath, FilePath
from bids.layout import BIDSLayout, parse_file_entities

class BIDSDataset(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    layout: BIDSLayout = Field(..., description="BIDS Layout object for dataset querying")
    bids_root: DirectoryPath = Field(..., description="Root directory of the BIDS dataset")
    dataset_description: BIDSDatasetDescription = Field(..., description="Parsed dataset_description.json content")
    derivatives: list[Self] = Field(description="List of BIDSLayout objects for derivatives directories")
    is_raw: bool = Field(..., description="Indicates if the dataset is raw or derived")
    subjects_sessions: Optional[dict[str, list[str]]] = Field(None, description="Mapping of subjects to their sessions")
    graph: Optional[KGGraph] = Field(None, description="Knowledge graph representation of the dataset")
    
    @classmethod
    def from_directory(cls, path: str | Path, derivatives_paths: Optional[list[Path]] = None) -> "BIDSDataset":
        path = Path(path).resolve()
        layout: BIDSLayout = BIDSLayout(str(path), validate=False, derivatives=[str(p) for p in derivatives_paths] if derivatives_paths else None)
        with open(path / "dataset_description.json", 'r') as f:
            dataset_description_data: dict = json.load(f)
        dataset_description: BIDSDatasetDescription = BIDSDatasetDescription(**dataset_description_data)
        
        # Load derivatives datasets
        internal_derivative_paths: list[Path] = list(path.resolve() for path in path.glob("derivatives/*") if path.is_dir())
        all_derivative_paths: list[Path] = list(set(internal_derivative_paths + (derivatives_paths if derivatives_paths else [])))
        
        derivatives: list[Self] = [
            BIDSDataset.from_directory(p) for p in all_derivative_paths
        ] if all_derivative_paths else []
        
        return cls(
            layout=layout,
            bids_root=path,
            dataset_description=dataset_description,
            derivatives=derivatives,
            is_raw=True
        )
        
    def set_subjects_sessions(self):
        # Set separately to avoid repeating subjects-sessions extraction in derivatives
        subjects: list[str] = self.layout.get_subjects()
        subjects_sessions: dict[str, list[str]] = {}
        for subj in subjects:
            sessions: list[str] = self.layout.get_sessions(subject=subj)
            subjects_sessions[subj] = sessions
        self.subjects_sessions = subjects_sessions
        
    def get_dataset_node_id(self) -> str:
        """
        Get the node ID for the dataset in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = f"dataset:{self.bids_root.name}"
        return dataset_node_id
    
    def get_subject_node_id(self, subject_id: str) -> str:
        """
        Get the node ID for a given subject in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        subject_node_id: str = f"{dataset_node_id}::subject:{subject_id}"
        return subject_node_id
    
    def get_session_node_id(self, session_id: str) -> str:
        """
        Get the node ID for a given session in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        session_node_id: str = f"{dataset_node_id}::session:{session_id}"
        return session_node_id
    
    def get_file_node_id(self, file_no_extension: str | Path) -> str:
        """
        Get the node ID for a given file (without extension) in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        file_node_id: str = f"{dataset_node_id}::file:{file_no_extension}"
        return file_node_id
    
    def get_raw_file_node_id(self, file_no_extension: str | Path) -> str:
        """
        Get the node ID for a given raw file (without extension) in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        raw_file_node_id: str = f"{dataset_node_id}::rawfile:{file_no_extension}"
        return raw_file_node_id
    
    def get_derived_file_node_id(self, derivative_name: str, file_no_extension: str | Path) -> str:
        """
        Get the node ID for a given derivative file (without extension) in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        derivative_file_node_id: str = f"{dataset_node_id}::derivative:{derivative_name}::file:{file_no_extension}"
        return derivative_file_node_id
    
    def get_dicomheaders_node_id(self, file_no_extension: str | Path) -> str:
        """
        Get the node ID for the DICOMHeaders node of a given file in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        file_node_id: str = self.get_raw_file_node_id(file_no_extension)
        dicomheaders_node_id: str = f"{file_node_id}::DICOMHeaders"
        return dicomheaders_node_id
    
    def get_BIDSEntity_node_id(self, entity_name: str, entity_value: str) -> str:
        """
        Get the node ID for a given BIDSEntity of a file in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        bids_entity_node_id: str = f"BIDSEntity:{entity_name}:{entity_value}"
        return bids_entity_node_id
    
    def get_pipeline_node_id(self, pipeline_name: str) -> str:
        """
        Get the node ID for a given pipeline in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        pipeline_node_id: str = f"{dataset_node_id}::pipeline:{pipeline_name}"
        return pipeline_node_id
    
    def get_pipeline_step_node_id(self, pipeline_name: str, step_name: str) -> str:
        """
        Get the node ID for a given pipeline step in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        pipeline_node_id: str = self.get_pipeline_node_id(pipeline_name)
        step_node_id: str = f"{pipeline_node_id}::step:{step_name}"
        return step_node_id
    
    def get_process_node_id(self, process_id: str) -> str:
        """
        Get the node ID for a given process in a pipeline in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        return f"process:{process_id}"
    
    def get_process_execution_node_id(self, process_id: str, process_exec_id: str) -> str:
        """
        Get the node ID for a given process execution in a pipeline in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        process_node_id: str = self.get_process_node_id(process_id)
        process_exec_node_id: str = f"{process_node_id}::execution:{process_exec_id}"
        return process_exec_node_id
    
    def get_logic_node_id(self, logic_name: str) -> str:
        """
        Get the node ID for a given process logic in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        logic_node_id: str = f"logic:{logic_name}"
        return logic_node_id
    
    def get_metric_node_id(self, metric: Metric) -> str:
        """
        Get the node ID for a given metric in the knowledge graph.
        """
        return f"metric:{metric.name}:{metric.value}:{metric.description}:{metric.category}:{metric.labels}"
    
    def get_sidecar_data(self, file_no_extension: str | Path) -> dict:
        """
        Get the JSON sidecar data for a given file in the dataset.
        """
        sidecar_path: str = file_no_extension + ".json"
        try:
            with open(sidecar_path, 'r') as f:
                sidecar_data: dict = json.load(f)
            return sidecar_data
        except FileNotFoundError:
            raise FileNotFoundError(f"Sidecar file not found: {sidecar_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON sidecar file: {sidecar_path}")
        
    def remove_file_extension(self, file_path: str | Path) -> str:
        """
        Remove the file extension from a given file path.
        """
        file_path = Path(file_path)
        return str(file_path.parent / file_path.name.split(".")[0])
    
    def get_files_no_extension(self, scope: str, subjects: Optional[str | list[str]] = None, sessions: Optional[str | list[str]] = None) -> set[str]:
        """
        Get set of file paths (without extensions) in the dataset for a given scope, subject, and session.
        """
        if subjects is None and sessions is not None:
            raise ValueError("Subject ID must be provided if session ID is specified.")
        
        if scope == "raw":
            layout = self.layout
        else:
            if len(self.derivatives) == 0:
                raise ValueError("No derivatives available in this dataset.")
            derivative_datasets: list[Self] = [d for d in self.derivatives if d.dataset_description.Name == scope]
            layout = derivative_datasets[0].layout
        
        if subjects is None:
            files = layout.get(return_type="file", scope=scope)
        elif subjects is not None and sessions is None:
            files = layout.get(subject=subjects, return_type="file", scope=scope)
        else:
            files = layout.get(subject=subjects, session=sessions, return_type="file", scope=scope)
        
        file_no_extensions = {self.remove_file_extension(f) for f in files}
        return file_no_extensions
    
    def normalize_file_path(self, file_path: str |Path) -> Path:
        try:
            file_path = Path(file_path)
            relative_path = file_path.relative_to("/data")
            normalized_path = self.bids_root / relative_path
            return normalized_path
        except ValueError:
            return file_path
    
    def create_dataset_node(self) -> KGNode:
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        return KGNode(id=dataset_node_id, label="Dataset", layer="data", properties={"identifier": dataset_node_id})
    
    def add_dataset_node(self):
        self.graph.add_node(self.create_dataset_node())
    
    def create_subject_node(self, subject: str) -> KGNode:
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        subject_node_id: str = self.get_subject_node_id(subject)
        return KGNode(id=subject_node_id, label="Subject", layer="data", properties={"identifier": subject, "dataset_id": dataset_node_id, "subject_id": subject})
    
    def add_subject_node(self, subject: str):
        self.graph.add_node(self.create_subject_node(subject))
        
    def create_session_node(self, session_id: str) -> KGNode:
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        session_node_id: str = self.get_session_node_id(session_id)
        return KGNode(id=session_node_id, label="Session", layer="data", properties={"identifier": session_id, "dataset_id": dataset_node_id, "session_id": session_id})
    
    def add_session_node(self, session_id: str):
        self.graph.add_node(self.create_session_node(session_id))
        
    def create_dicomheaders_node(self, file_no_extension: str | Path, dicom_data: dict) -> KGNode:
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dicomheaders_node_id: str = self.get_dicomheaders_node_id(file_no_extension)
        return KGNode(id=dicomheaders_node_id, label="DICOMHeaders", layer="data", properties=dicom_data)
    
    def add_dicomheaders_node(self, file_no_extension: str | Path, dicom_data: dict):
        self.graph.add_node(self.create_dicomheaders_node(file_no_extension, dicom_data))
    
    def create_raw_file_node(self, file_no_extension: str | Path, subject: str, session_id: Optional[str] = None) -> KGNode:
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        raw_file_node_id: str = self.get_raw_file_node_id(file_no_extension)
        return KGNode(id=raw_file_node_id, label="RawFile", layer="data", properties={"stem": file_no_extension, "subject_id": subject, "session_id": session_id, "dataset_id": dataset_node_id})
    
    def add_raw_file_node(self, file_no_extension: str | Path, subject: str, session_id: Optional[str] = None):
        self.graph.add_node(self.create_raw_file_node(file_no_extension, subject, session_id))
    
    def create_BIDSEntity_node(self, entity_name: str, entity_value: str) -> KGNode:
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        bids_entity_node_id: str = self.get_BIDSEntity_node_id(entity_name, entity_value)
        return KGNode(id=bids_entity_node_id, label="BIDSEntity", layer="data", properties={"name": entity_name, "value": entity_value})
    
    def add_BIDSEntity_node(self, entity_name: str, entity_value: str):
        self.graph.add_node(self.create_BIDSEntity_node(entity_name, entity_value))
        
    def create_pipeline_node(self, derivative_name: str) -> tuple[KGNode, BIDSDatasetDescription]:
        try:
            derivative_dataset: Self = [d for d in self.derivatives if d.dataset_description.Name == derivative_name][0]
        except IndexError:
            raise ValueError(f"No derivative dataset found with name: {derivative_name}")
        
        pipeline_node_id: str = self.get_pipeline_node_id(derivative_name)
        
        dataset_description: BIDSDatasetDescription = derivative_dataset.dataset_description
        pipeline_id: str = dataset_description.GeneratedBy[0].model_dump().get("ID", "unknown_pipeline_id")
        
        return KGNode(
            id=pipeline_node_id,
            label="Pipeline",
            layer="provenance",
            properties={
                "name": derivative_name,
                "pipeline_id": pipeline_id
            }
        ), dataset_description
    
    def add_pipeline_node(self, derivative_name: str) -> BIDSDatasetDescription:
        pipeline_node, dataset_description = self.create_pipeline_node(derivative_name)
        self.graph.add_node(pipeline_node)
        return dataset_description
    
    def create_derived_file_node(self, derivative_name: str, file_no_extension: str | Path) -> KGNode:
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        derivative_file_node_id: str = self.get_derived_file_node_id(derivative_name, file_no_extension)
        return KGNode(
            id=derivative_file_node_id,
            label="DerivedFile",
            layer="data",
            properties={
                "stem": file_no_extension,
                "derivative_name": derivative_name,
                "dataset_id": dataset_node_id
            }
        )
    
    def add_derived_file_node(self, derivative_name: str, file_no_extension: str | Path):
        self.graph.add_node(self.create_derived_file_node(derivative_name, file_no_extension))
    
    def create_pipeline_step_node(self, derivative_name: str, step_name: str, step_description: str) -> KGNode:
        pipeline_step_node_id: str = self.get_pipeline_step_node_id(derivative_name, step_name)
        return KGNode(
            id=pipeline_step_node_id,
            label="PipelineStep",
            layer="provenance",
            properties={
                "name": step_name,
                "description": step_description
            }
        )
    
    def add_pipeline_step_node(self, derivative_name: str, step_name: str, step_description: str):
        self.graph.add_node(self.create_pipeline_step_node(derivative_name, step_name, step_description))
    
    def create_process_node(self, process_id: str) -> KGNode:
        process_node_id: str = self.get_process_node_id(process_id)
        return KGNode(
            id=process_node_id,
            label="Process",
            layer="provenance",
            properties={
                "process_id": process_id
            }
        )
    
    def add_process_node(self, process_id: str):
        self.graph.add_node(self.create_process_node(process_id))
    
    def create_process_execution_node(self, process_id: str, process_exec_id: str) -> KGNode:
        process_exec_node_id: str = self.get_process_execution_node_id(process_id, process_exec_id)
        return KGNode(
            id=process_exec_node_id,
            label="ProcessExecution",
            layer="provenance",
            properties={
                "process_exec_id": process_exec_id,
                "process_id": process_id
            }
        )
    
    def add_process_execution_node(self, process_id: str, process_exec_id: str):
        self.graph.add_node(self.create_process_execution_node(process_id, process_exec_id))
        
    def create_logic_node(self, logic: NeuProcessLogic) -> KGNode:
        logic_node_id: str = self.get_logic_node_id(logic.about.name)
        return KGNode(
            id=logic_node_id,
            label="Logic",
            layer="provenance",
            properties={
                "name": logic.about.name,
                "description": logic.about.description,
                "code": logic.code
            }
        )
    
    def add_logic_node(self, logic: NeuProcessLogic):
        self.graph.add_node(self.create_logic_node(logic))
        
    def create_metric_node(self, metric: Metric) -> KGNode:
        metric_node_id: str = self.get_metric_node_id(metric)
        return KGNode(
            id=metric_node_id,
            label="Metric",
            layer="provenance",
            properties=metric.model_dump()
        )
    
    def add_metric_node(self, metric: Metric):
        self.graph.add_node(self.create_metric_node(metric))
        
    def create_subject_hasSession_edge(self, subject: str, session_id: str) -> KGEdge:
        """
        Subject -hasSession-> Session
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        return KGEdge(
            source=self.get_subject_node_id(subject),
            target=self.get_session_node_id(session_id),
            relation="hasSession",
            properties={
                "subject_id": subject,
                "session_id": session_id,
                "relationship": "hasSession"
            }
        )
    
    def add_subject_hasSession_edge(self, subject: str, session_id: str):
        """
        Subject -hasSession-> Session
        """
        self.graph.add_edge(self.create_subject_hasSession_edge(subject, session_id))
        
    def create_rawFile_hasSession_edge(self, file_no_extension: str | Path, session_id: str) -> KGEdge:
        """
        RawFile -hasSession-> Session
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        raw_file_node_id: str = self.get_raw_file_node_id(file_no_extension)
        session_node_id: str = self.get_session_node_id(session_id)
        return KGEdge(
            source=raw_file_node_id,
            target=session_node_id,
            relation="hasSession",
            properties={
                "stem": file_no_extension,
                "session_id": session_id,
                "relationship": "hasSession"
            }
        )
    
    def add_rawFile_hasSession_edge(self, file_no_extension: str | Path, session_id: str):
        """
        RawFile -hasSession-> Session
        """
        self.graph.add_edge(self.create_rawFile_hasSession_edge(file_no_extension, session_id))
    
    def create_derivedFile_hasSession_edge(self, derivative_name: str, file_no_extension: str | Path, session_id: str) -> KGEdge:
        """
        DerivedFile -hasSession-> Session
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        derivative_file_node_id: str = self.get_derived_file_node_id(derivative_name, file_no_extension)
        session_node_id: str = self.get_session_node_id(session_id)
        return KGEdge(
            source=derivative_file_node_id,
            target=session_node_id,
            relation="hasSession",
            properties={
                "stem": file_no_extension,
                "derivative_name": derivative_name,
                "session_id": session_id,
                "relationship": "hasSession"
            }
        )    
    
    def add_derivedFile_hasSession_edge(self, derivative_name: str, file_no_extension: str | Path, session_id: str):
        """
        DerivedFile -hasSession-> Session
        """
        self.graph.add_edge(self.create_derivedFile_hasSession_edge(derivative_name, file_no_extension, session_id))
        
    def create_hasRawFile_edge(self, file_no_extension: str | Path) -> KGEdge:
        """
        Dataset -hasRawFile-> RawFile
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        raw_file_node_id: str = self.get_raw_file_node_id(file_no_extension)
        return KGEdge(
            source=dataset_node_id,
            target=raw_file_node_id,
            relation="hasRawFile",
            properties={
                "dataset_id": dataset_node_id,
                "stem": file_no_extension,
                "relationship": "hasRawFile"
            }
        )
    
    def add_hasRawFile_edge(self, file_no_extension: str | Path):
        """
        Dataset -hasRawFile-> RawFile
        """
        self.graph.add_edge(self.create_hasRawFile_edge(file_no_extension))
    
    def create_rawFile_hasSubject_edge(self, file_no_extension: str | Path, subject: str) -> KGEdge:
        """
        RawFile -hasSubject-> Subject
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        raw_file_node_id: str = self.get_raw_file_node_id(file_no_extension)
        subject_node_id: str = self.get_subject_node_id(subject)
        return KGEdge(
            source=raw_file_node_id,
            target=subject_node_id,
            relation="hasSubject",
            properties={
                "subject_id": subject,
                "stem": file_no_extension,
                "relationship": "hasSubject"
            }
        )
    
    def add_rawFile_hasSubject_edge(self, file_no_extension: str | Path, subject: str):
        """
        RawFile -hasSubject-> Subject
        """
        self.graph.add_edge(self.create_rawFile_hasSubject_edge(file_no_extension, subject))
    
    def create_derivedFile_hasSubject_edge(self, derivative_name: str, file_no_extension: str | Path, subject: str) -> KGEdge:
        """
        DerivedFile -hasSubject-> Subject
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        derivative_file_node_id: str = self.get_derived_file_node_id(derivative_name, file_no_extension)
        subject_node_id: str = self.get_subject_node_id(subject)
        return KGEdge(
            source=derivative_file_node_id,
            target=subject_node_id,
            relation="hasSubject",
            properties={
                "subject_id": subject,
                "stem": file_no_extension,
                "derivative_name": derivative_name,
                "relationship": "hasSubject"
            }
        )
    
    def add_derivedFile_hasSubject_edge(self, derivative_name: str, file_no_extension: str | Path, subject: str):
        """
        DerivedFile -hasSubject-> Subject
        """
        self.graph.add_edge(self.create_derivedFile_hasSubject_edge(derivative_name, file_no_extension, subject))
    
    def create_hasDICOMHeaders_edge(self, file_no_extension: str | Path) -> KGEdge:
        """
        RawFile -hasDICOMHeaders-> DICOMHeaders
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        raw_file_node_id: str = self.get_raw_file_node_id(file_no_extension)
        dicomheaders_node_id: str = self.get_dicomheaders_node_id(file_no_extension)
        return KGEdge(
            source=raw_file_node_id,
            target=dicomheaders_node_id,
            relation="hasDICOMHeaders",
            properties={
                "stem": file_no_extension,
                "relationship": "hasDICOMHeaders"
            }
        )
    
    def add_hasDICOMHeaders_edge(self, file_no_extension: str | Path):
        """
        RawFile -hasDICOMHeaders-> DICOMHeaders
        """
        self.graph.add_edge(self.create_hasDICOMHeaders_edge(file_no_extension))
        
    def create_rawFile_hasBIDSEntity_edge(self, file_no_extension: str | Path, entity_name: str, entity_value: str) -> KGEdge:
        """
        RawFile -hasBIDSEntity-> BIDSEntity
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        raw_file_node_id: str = self.get_raw_file_node_id(file_no_extension)
        bids_entity_node_id: str = self.get_BIDSEntity_node_id(entity_name, entity_value)
        return KGEdge(
            source=raw_file_node_id,
            target=bids_entity_node_id,
            relation="hasBIDSEntity",
            properties={
                "stem": file_no_extension,
                "name": entity_name,
                "value": entity_value,
                "relationship": "hasBIDSEntity"
            }
        )
    
    def add_rawFile_hasBIDSEntity_edge(self, file_no_extension: str | Path, entity_name: str, entity_value: str):
        """
        RawFile -hasBIDSEntity-> BIDSEntity
        """
        self.graph.add_edge(self.create_rawFile_hasBIDSEntity_edge(file_no_extension, entity_name, entity_value))
        
    def create_derivedFile_hasBIDSEntity_edge(self, derivative_name: str, file_no_extension: str | Path, entity_name: str, entity_value: str) -> KGEdge:
        """
        DerivedFile -hasBIDSEntity-> BIDSEntity
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        derivative_file_node_id: str = self.get_derived_file_node_id(derivative_name, file_no_extension)
        bids_entity_node_id: str = self.get_BIDSEntity_node_id(entity_name, entity_value)
        return KGEdge(
            source=derivative_file_node_id,
            target=bids_entity_node_id,
            relation="hasBIDSEntity",
            properties={
                "stem": file_no_extension,
                "derivative_name": derivative_name,
                "name": entity_name,
                "value": entity_value,
                "relationship": "hasBIDSEntity"
            }
        )
    
    def add_derivedFile_hasBIDSEntity_edge(self, derivative_name: str, file_no_extension: str | Path, entity_name: str, entity_value: str):
        """
        DerivedFile -hasBIDSEntity-> BIDSEntity
        """
        self.graph.add_edge(self.create_derivedFile_hasBIDSEntity_edge(derivative_name, file_no_extension, entity_name, entity_value))
        
    def create_hasPipeline_edge(self, derivative_name: str) -> KGEdge:
        """
        Dataset -hasPipeline-> Pipeline
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        pipeline_node_id: str = self.get_pipeline_node_id(derivative_name)
        return KGEdge(
            source=dataset_node_id,
            target=pipeline_node_id,
            relation="hasPipeline",
            properties={
                "dataset_id": dataset_node_id,
                "derivative_name": derivative_name,
                "relationship": "hasPipeline"
            }
        )
    
    def add_hasPipeline_edge(self, derivative_name: str):
        """
        Dataset -hasPipeline-> Pipeline
        """
        self.graph.add_edge(self.create_hasPipeline_edge(derivative_name))
        
    def create_hasStep_edge(self, derivative_name: str, step_name: str) -> KGEdge:
        """
        Pipeline -hasStep-> PipelineStep
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        pipeline_node_id: str = self.get_pipeline_node_id(derivative_name)
        step_node_id: str = self.get_pipeline_step_node_id(derivative_name, step_name)
        return KGEdge(
            source=pipeline_node_id,
            target=step_node_id,
            relation="hasStep",
            properties={
                "derivative_name": derivative_name,
                "step_name": step_name,
                "relationship": "hasStep"
            }
        )
    
    def add_hasStep_edge(self, derivative_name: str, step_name: str):
        """
        Pipeline -hasStep-> PipelineStep
        """
        self.graph.add_edge(self.create_hasStep_edge(derivative_name, step_name))
    
    def create_realizesProcess_edge(self, pipeline_name: str, step_name: str, process_id: str) -> KGEdge:
        """
        PipelineStep -realizesProcess-> Process
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        step_node_id: str = self.get_pipeline_step_node_id(pipeline_name, step_name)
        process_node_id: str = self.get_process_node_id(process_id)
        return KGEdge(
            source=step_node_id,
            target=process_node_id,
            relation="realizesProcess",
            properties={
                "pipeline_name": pipeline_name,
                "step_name": step_name,
                "process_id": process_id,
                "relationship": "realizesProcess"
            }
        )
    
    def add_realizesProcess_edge(self, pipeline_name: str, step_name: str, process_id: str):
        """
        PipelineStep -realizesProcess-> Process
        """
        self.graph.add_edge(self.create_realizesProcess_edge(pipeline_name, step_name, process_id))
        
    def create_executes_edge(self, process_id: str, process_exec_id: str) -> KGEdge:
        """
        Process -executes-> ProcessExecution
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        process_node_id: str = self.get_process_node_id(process_id)
        process_exec_node_id: str = self.get_process_execution_node_id(process_id, process_exec_id)
        return KGEdge(
            source=process_node_id,
            target=process_exec_node_id,
            relation="executes",
            properties={
                "process_id": process_id,
                "process_exec_id": process_exec_id,
                "relationship": "executes"
            }
        )
    
    def add_executes_edge(self, process_id: str, process_exec_id: str):
        """
        Process -executes-> ProcessExecution
        """
        self.graph.add_edge(self.create_executes_edge(process_id, process_exec_id))
    
    def create_usesLogic_edge(self, process_id: str, logic_name: str) -> KGEdge:
        """
        Process -usesLogic-> Logic
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        process_node_id: str = self.get_process_node_id(process_id)
        logic_node_id: str = self.get_logic_node_id(logic_name)
        return KGEdge(
            source=process_node_id,
            target=logic_node_id,
            relation="usesLogic",
            properties={
                "process_id": process_id,
                "logic_name": logic_name,
                "relationship": "usesLogic"
            }
        )
    
    def add_usesLogic_edge(self, process_id: str, logic_name: str):
        """
        Process -usesLogic-> Logic
        """
        self.graph.add_edge(self.create_usesLogic_edge(process_id, logic_name))
        
    def create_hasDerivedFile_edge(self, derivative_name: str, file_no_extension: str | Path) -> KGEdge:
        """
        Pipeline -hasDerivedFile-> DerivedFile
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        pipeline_node_id: str = self.get_pipeline_node_id(derivative_name)
        derivative_file_node_id: str = self.get_derived_file_node_id(derivative_name, file_no_extension)
        return KGEdge(
            source=pipeline_node_id,
            target=derivative_file_node_id,
            relation="hasDerivedFile",
            properties={
                "derivative_name": derivative_name,
                "stem": str(file_no_extension),
                "relationship": "hasDerivedFile"
            }
        )
    
    def add_hasDerivedFile_edge(self, derivative_name: str, file_no_extension: str | Path):
        """
        Pipeline -hasDerivedFile-> DerivedFile
        """
        self.graph.add_edge(self.create_hasDerivedFile_edge(derivative_name, file_no_extension))
        
    def create_generates_edge(self, derivative_name: str, process_id: str, process_exec_id: str, file_no_extension: str | Path) -> KGEdge:
        """
        ProcessExecution -generates-> DerivedFile
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        process_exec_node_id: str = self.get_process_execution_node_id(process_id, process_exec_id)
        derivative_file_node_id: str = self.get_derived_file_node_id(derivative_name, file_no_extension)
        return KGEdge(
            source=process_exec_node_id,
            target=derivative_file_node_id,
            relation="generates",
            properties={
                "process_id": process_id,
                "process_exec_id": process_exec_id,
                "stem": str(file_no_extension),
                "relationship": "generates"
            }
        )
    
    def add_generates_edge(self, derivative_name: str, process_id: str, process_exec_id: str, file_no_extension: str | Path):
        """
        ProcessExecution -generates-> DerivedFile
        """
        self.graph.add_edge(self.create_generates_edge(derivative_name, process_id, process_exec_id, file_no_extension))
        
    def create_derivedFrom_edge(self, src_derivative_name: str, src_derivative_file_no_extension: str | Path, dst_file_node_id: str) -> KGEdge:
        """
        DerivedFile -derivedFrom-> RawFile or DerivedFile -derivedFrom-> DerivedFile
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        derivative_file_node_id: str = self.get_derived_file_node_id(src_derivative_name, src_derivative_file_no_extension)
        return KGEdge(
            source=derivative_file_node_id,
            target=dst_file_node_id,
            relation="derivedFrom",
            properties={
                "derivative_name": src_derivative_name,
                "derivative_stem": str(src_derivative_file_no_extension),
                "src_file_node_id": derivative_file_node_id,
                "dst_file_node_id": dst_file_node_id,
                "relationship": "derivedFrom"
            }
        )
    
    def add_derivedFrom_edge(self, src_derivative_name: str, src_derivative_file_no_extension: str | Path, dst_file_node_id: str):
        """
        DerivedFile -derivedFrom-> RawFile or DerivedFile -derivedFrom-> DerivedFile
        """
        self.graph.add_edge(self.create_derivedFrom_edge(src_derivative_name, src_derivative_file_no_extension, dst_file_node_id))
    
    def create_usedBy_edge(self, input_file_node_id: str, process_id: str, process_exec_id: str) -> KGEdge:
        """
        RawFile -usedBy-> ProcessExecution or DerivedFile -usedBy-> ProcessExecution
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        process_exec_node_id: str = self.get_process_execution_node_id(process_id, process_exec_id)
        return KGEdge(
            source=input_file_node_id,
            target=process_exec_node_id,
            relation="usedBy",
            properties={
                "process_id": process_id,
                "process_exec_id": process_exec_id,
                "relationship": "usedBy"
            }
        )
    
    def add_usedBy_edge(self, input_file_node_id: str, process_id: str, process_exec_id: str):
        """
        RawFile -usedBy-> ProcessExecution or DerivedFile -usedBy-> ProcessExecution
        """
        self.graph.add_edge(self.create_usedBy_edge(input_file_node_id, process_id, process_exec_id))
        
    def create_hasMetric_edge(self, src_node_id: str, metric: Metric) -> KGEdge:
        """
        DerivedFile -hasMetric-> Metric
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        metric_node_id: str = self.get_metric_node_id(metric)
        return KGEdge(
            source=src_node_id,
            target=metric_node_id,
            relation="hasMetric",
            properties={
                "node_id": src_node_id,
                "metric_name": metric.name,
                "relationship": "hasMetric",
                "metric": metric.model_dump()
            }
        )
    
    def add_hasMetric_edge(self, src_node_id: str, metric: Metric):
        """
        DerivedFile -hasMetric-> Metric
        """
        self.graph.add_edge(self.create_hasMetric_edge(src_node_id, metric))
    
    def build_basic_graph(self):
        self.graph = KGGraph(nodes={}, edges=[])
        
        # Dataset node
        dataset_node_id: str = self.get_dataset_node_id()
        self.add_dataset_node()
        
        # Subject and session nodes
        if not self.subjects_sessions:
            self.set_subjects_sessions()
        for subject, session_ids in self.subjects_sessions.items():
            self.add_subject_node(subject)
            for session_id in session_ids:
                sess_node_id: str = self.get_session_node_id(session_id)
                self.add_session_node(session_id)
                self.add_subject_hasSession_edge(subject, session_id) # Subject -hasSession-> Session
                # Raw file nodes
                for raw_file_no_extension in self.get_files_no_extension(scope="raw", subjects=subject):
                    raw_file_node_id: str = self.get_raw_file_node_id(raw_file_no_extension)
                    self.add_raw_file_node(raw_file_no_extension, subject, session_id)
                    self.add_hasRawFile_edge(raw_file_no_extension) # Dataset -hasRawFile-> RawFile
                    self.add_rawFile_hasSubject_edge(raw_file_no_extension, subject) # RawFile -hasSubject-> Subject
                    self.add_rawFile_hasSession_edge(raw_file_no_extension, session_id) # RawFile -hasSession-> Session
                    
                    # DICOMHeaders node
                    try:
                        dicom_data: dict = self.get_sidecar_data(raw_file_no_extension)
                        self.add_dicomheaders_node(raw_file_no_extension, dicom_data)
                        self.add_hasDICOMHeaders_edge(raw_file_no_extension) # RawFile -hasDICOMHeaders-> DICOMHeaders
                    except Exception as e:
                        print(f"Error processing raw file sidecar {raw_file_no_extension}.json: {e}")
                    
                    # Add BIDSEntity nodes from sidecar
                    bids_entities: dict = {key: value for key, value in parse_file_entities(raw_file_no_extension).items() if key not in ['subject', 'session']}
                    for entity_name, entity_value in bids_entities.items():
                        self.add_BIDSEntity_node(entity_name, entity_value)
                        self.add_rawFile_hasBIDSEntity_edge(raw_file_no_extension, entity_name, entity_value) # RawFile -hasBIDSEntity-> BIDSEntity
                
    def add_derivative_to_graph(self, derivative_name: str):
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        
        dataset_node_id: str = self.get_dataset_node_id()
        pipeline_node_id: str = self.get_pipeline_node_id(derivative_name)
        
        dataset_description: BIDSDatasetDescription = self.add_pipeline_node(derivative_name)
        
        self.add_hasPipeline_edge(derivative_name) # Dataset -hasPipeline-> Pipeline
        
        # Get pipeline steps
        for step_idx, pipeline_step in enumerate(dataset_description.PipelineSteps):
            step_name: str = pipeline_step.get("Name", step_idx+1)
            step_node_id: str = self.get_pipeline_step_node_id(derivative_name, step_name)
            step_description: str = pipeline_step.get("Description", "")
            self.add_pipeline_step_node(derivative_name, step_name, step_description)
            self.add_hasStep_edge(derivative_name, step_name) # Pipeline -hasStep-> PipelineStep
            
            # Get process_ids from this step
            processes: dict[str, list[str]] = {}
            for item in pipeline_step.get("processes", []):
                process_id: str = item.get("process_id", "")
                if process_id not in processes:
                    processes[process_id] = []
                processes[process_id].append(item.get("process_exec_id", ""))
            for process_id, exec_ids in processes.items():
                process_node_id: str = self.get_process_node_id(process_id)
                self.add_process_node(process_id)
                self.add_realizesProcess_edge(derivative_name, step_name, process_id) # PipelineStep -realizesProcess-> Process
                
                for exec_id in exec_ids:
                    process_exec_node_id: str = f"{process_node_id}::execution:{exec_id}"
                    self.add_process_execution_node(process_id, exec_id)
                    self.add_executes_edge(process_id, exec_id) # Process -executes-> ProcessExecution
                
                # Logic node
                process: NeuProcess = NeuProcess.from_process_id(process_id)
                logic: NeuProcessLogic = process.logic
                logic_node_id: str = self.get_logic_node_id(logic.about.name)
                self.add_logic_node(logic)
                self.add_usesLogic_edge(process_id, logic.about.name) # Process -usesLogic-> Logic
                
        # Derivative file nodes
        for deriv_file_no_extension in self.get_files_no_extension(scope=derivative_name):
            deriv_file_node_id: str = self.get_derived_file_node_id(derivative_name, deriv_file_no_extension)
            self.add_derived_file_node(derivative_name, deriv_file_no_extension)
            self.add_hasDerivedFile_edge(derivative_name, deriv_file_no_extension) # Pipeline -hasDerivedFile-> DerivedFile
            
            # Get BIDSEntity nodes
            bids_entities: dict = {key: value for key, value in parse_file_entities(deriv_file_no_extension).items()}
            subject_id: str = bids_entities.get("subject")
            session_id: str = bids_entities.get("session")
            subj_node_id: str = self.get_subject_node_id(subject_id)
            sess_node_id: str = self.get_session_node_id(session_id)
            if subject_id is not None:
                self.add_derivedFile_hasSubject_edge(derivative_name, deriv_file_no_extension, subject_id) # DerivedFile -hasSubject-> Subject
            if session_id is not None:
                self.add_derivedFile_hasSession_edge(derivative_name, deriv_file_no_extension, session_id) # DerivedFile -hasSession-> Session
            
            try:
                sidecar_data: dict = self.get_sidecar_data(deriv_file_no_extension)
            except Exception as e:
                # print(f"Error loading derivative file sidecar {deriv_file_stem}.json: {e}")
                continue
                
            process_exec_id: str = sidecar_data.get("ProcessExecID")
            process_exec_node_id: str = self.get_process_execution_node_id(process_id, process_exec_id)
            self.add_process_execution_node(process_id, process_exec_id)
            self.add_generates_edge(derivative_name, process_id, process_exec_id, deriv_file_no_extension) # ProcessExecution -generates-> DerivedFile
            
            for entity_name, entity_value in bids_entities.items():
                if entity_name in ["subject", "session"]:
                    continue
                self.add_BIDSEntity_node(entity_name, entity_value)
                self.add_derivedFile_hasBIDSEntity_edge(derivative_name, deriv_file_no_extension, entity_name, entity_value) # DerivedFile -hasBIDSEntity-> BIDSEntity
                
            # Find the RawFile/DerivedFile it was derived from
            input_file: str = sidecar_data.get("InputFile")
            if input_file:
                input_file_path: Path = Path(input_file)
                normalized_input_path: Path = self.normalize_file_path(input_file_path)
                input_file_no_extension: str = self.remove_file_extension(normalized_input_path)
                # Determine if input file is RawFile or DerivedFile
                # DerivedFile would have the derivative name in its path - {bids_root}/derivatives/{derivative_name}/...
                label: str = "RawFile"
                if f"derivatives/" in str(normalized_input_path):
                    input_derivative_name: str = normalized_input_path.parts[normalized_input_path.parts.index("derivatives") + 1]
                    input_file_node_id: str = self.get_derived_file_node_id(input_derivative_name, input_file_no_extension)
                    label = "DerivedFile"
                else:
                    input_file_node_id: str = self.get_raw_file_node_id(input_file_no_extension)
                if not input_file_node_id in self.graph.nodes:
                    print(f"Input file node {input_file_node_id} not found in graph for file {deriv_file_no_extension}. Creating.")
                    self.add_derived_file_node(input_derivative_name, input_file_no_extension) if label == "DerivedFile" else self.add_raw_file_node(input_file_no_extension, subject_id, session_id)
                self.add_derivedFrom_edge(derivative_name, deriv_file_no_extension, input_file_node_id) # DerivedFile -derivedFrom-> RawFile/DerivedFile
                self.add_usedBy_edge(input_file_node_id, process_id, process_exec_id) # RawFile/DerivedFile -usedBy-> ProcessExecution
                
            # Get Metric nodes from sidecar
            metrics: list[Metric] = Metric.from_dict(sidecar_data, sub_key="metrics")
            for metric in metrics:
                self.add_metric_node(metric)
                self.add_hasMetric_edge(deriv_file_node_id, metric) # DerivedFile -hasMetric-> Metric
                
    def prune_unconnected_derived_files(self):
        """
        Remove DerivedFile nodes that are not connected to any ProcessExecution
        via provenance relations (usedBy / generates).
        Both edges should not exist for such DerivedFile nodes-
            - DerivedFile -usedBy-> ProcessExecution
            - ProcessExecution -generates-> DerivedFile
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        
        n_derived_files_removed: int = 0
        for derived_file_node in list(self.graph.search_nodes(label="DerivedFile")):
            node_edges: list[KGEdge] = self.graph.get_node_edges(derived_file_node.id)
            if not any(
                (edge.relation == "usedBy" and edge.source == derived_file_node.id) or
                (edge.relation == "generates" and edge.target == derived_file_node.id)
                for edge in node_edges
            ):
                self.graph.remove_node(derived_file_node.id)
                n_derived_files_removed += 1
        
        print(f"Removed {n_derived_files_removed} supplementary DerivedFile nodes from the graph.")
