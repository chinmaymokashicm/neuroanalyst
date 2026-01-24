from ..process.exec.core import NeuProcessExec
from ..bids import BIDSDatasetDescription
from .core import KGGraph, KGNode, KGEdge
from ..process.process.core import NeuProcess
from ..process.logic.core import NeuProcessLogic, Metric

from typing import Optional, Self
from collections import deque
import os, json
from pathlib import Path

from pydantic import BaseModel, Field, DirectoryPath, FilePath
from bids.layout import BIDSLayout, parse_file_entities
import pandas as pd

class BIDSDataset(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    layout: BIDSLayout = Field(..., description="BIDS Layout object for dataset querying")
    bids_root: DirectoryPath = Field(..., description="Root directory of the BIDS dataset")
    dataset_description: BIDSDatasetDescription = Field(..., description="Parsed dataset_description.json content")
    derivatives: list[Self] = Field(description="List of BIDSLayout objects for derivatives directories")
    is_raw: bool = Field(..., description="Indicates if the dataset is raw or derived")
    subjects_sessions: Optional[dict[str, list[str]]] = Field(None, description="Mapping of subjects to their sessions. This will be used to create smaller subgraphs")
    scopes: Optional[list[str]] = Field(None, description="List of scopes to consider in the dataset. This will be used to create smaller subgraphs.")
    graph: Optional[KGGraph] = Field(None, description="Knowledge graph representation of the dataset")
    
    @staticmethod
    def identify_process_execs_from_file_stem(bids_root: str, pipeline_name: str, file_stem: str, process_id: str) -> list[str]:
        """
        Identify ProcessExecution IDs associated with a given file stem and process ID in the BIDS dataset.
        
        Args:
            bids_root (str): Root directory of the BIDS dataset.
            pipeline_name (str): Name of the pipeline (derivative) to search within.
            file_stem (str): File stem (without extension) to identify associated ProcessExecutions.
            process_id (str): Process ID to filter ProcessExecutions.
        Returns:
            list[str]: List of matching ProcessExecution IDs.
        """
        with open(Path(bids_root) / "derivatives" / pipeline_name / "dataset_description.json", "r") as f:
            dataset_description_json = json.load(f)
        dataset_description: BIDSDatasetDescription = BIDSDatasetDescription.model_validate(dataset_description_json)
        all_execs: list[NeuProcessExec] = []
        for step in dataset_description.PipelineSteps:
            for info in step.get("processes", []):
                if info.get("process_id") == process_id:
                    execs: NeuProcessExec = NeuProcessExec.from_exec_id(info.get("process_exec_id"))
                    all_execs.append(execs)
        print(f"Number of ProcessExecutions found for process ID {process_id}: {len(all_execs)}")
        bids_entities: dict = parse_file_entities(file_stem)
        if "subject" in bids_entities:
            subject_id: str = bids_entities["subject"]
        else:
            raise ValueError(f"Subject entity not found in file stem: {file_stem}")
        if "session" in bids_entities:
            session_id: str = bids_entities["session"]
        else:
            session_id = None
        execs_with_matching_subject: list[NeuProcessExec] = []
        for exec in all_execs:
            subjects: list[str] | str = exec.bids_filters.get("subject")
            if isinstance(subjects, str):
                condition: bool = subject_id == subjects
            elif isinstance(subjects, list):
                condition: bool = subject_id in subjects
            else:
                condition: bool = False
            if condition:
                execs_with_matching_subject.append(exec)
        if not execs_with_matching_subject:
            raise ValueError(f"No matching ProcessExecution found for {subject_id=}, {session_id=}, {pipeline_name=} file stem: {file_stem} and process ID: {process_id} in BIDS root: {bids_root}")
        matched_exec_ids: list[str] = []
        for exec in execs_with_matching_subject:
            if "session" in exec.bids_filters:
                sessions: list[str] | str = exec.bids_filters.get("session")
                if isinstance(sessions, str):
                    condition: bool = session_id == sessions
                elif isinstance(sessions, list):
                    condition: bool = session_id in sessions
                else:
                    condition: bool = False
                if condition and exec.env_var_values.get("PIPELINE_NAME") == pipeline_name:
                    matched_exec_ids.append(exec.exec_id)
            else:
                matched_exec_ids.append(exec.exec_id)
        if matched_exec_ids:
            return matched_exec_ids
        raise ValueError(f"No matching ProcessExecution found for file stem: {file_stem} and process ID: {process_id} in BIDS root: {bids_root}")
    
    @classmethod
    def from_directory(cls, path: str | Path, derivatives_paths: Optional[object] = None, scopes: Optional[list[str]] = None) -> "BIDSDataset":
        """
        Load a BIDS dataset from a directory, including its derivatives.
        
        Args:
            path (str | Path): Path to the BIDS dataset root directory.
            derivatives_paths (Optional[object]): List of paths to derivative datasets or scopes to include.
            scopes (Optional[list[str]]): List of scopes to filter derivative datasets.
        Returns:
            BIDSDataset: Loaded BIDS dataset object.
        """
        path = Path(path).resolve()

        # If derivatives_paths was mistakenly passed as a scope (e.g., "raw" or ["raw"]),
        # treat it as scopes and ignore derivatives_paths.
        if isinstance(derivatives_paths, (str, list)) and not (
            isinstance(derivatives_paths, list) and all(isinstance(p, Path) for p in derivatives_paths)
        ):
            scopes = [derivatives_paths] if isinstance(derivatives_paths, str) else derivatives_paths
            derivatives_paths = None

        # Normalize derivative layout paths only if real Paths are provided
        derivative_layout_paths: Optional[list[str]] = None
        if isinstance(derivatives_paths, list) and derivatives_paths:
            derivative_layout_paths = [str(Path(p).resolve()) for p in derivatives_paths]

        layout: BIDSLayout = BIDSLayout(str(path), validate=False, derivatives=derivative_layout_paths)
        with open(path / "dataset_description.json", "r") as f:
            dataset_description_data: dict = json.load(f)
        dataset_description: BIDSDatasetDescription = BIDSDatasetDescription(**dataset_description_data)

        # Collect internal derivative directories correctly
        internal_derivative_paths: list[Path] = [p.resolve() for p in path.glob("derivatives/*") if p.is_dir()]
        external_derivative_paths: list[Path] = [Path(p).resolve() for p in derivatives_paths] if derivatives_paths else []
        all_derivative_paths: list[Path] = list(set(internal_derivative_paths + external_derivative_paths))

        # Derive scopes if not provided
        if scopes is None:
            scopes = sorted({p.name for p in all_derivative_paths}) + ["raw"]

        # Filter derivative dirs by scopes
        filtered_derivative_paths: list[Path] = [p for p in all_derivative_paths if p.name in scopes]

        # Recursively load derivative datasets
        derivatives: list[Self] = [
            BIDSDataset.from_directory(p, scopes=scopes) for p in filtered_derivative_paths
        ] if filtered_derivative_paths else []

        # Determine raw vs derivative dataset based on path
        is_raw: bool = "derivatives" not in path.parts

        return cls(
            layout=layout,
            bids_root=path,
            dataset_description=dataset_description,
            derivatives=derivatives,
            is_raw=is_raw,
            scopes=scopes,
        )
        
    @staticmethod
    def files_per_process(process_node_id: str, graph: KGGraph):
        """
        Get all DerivedFile nodes associated with a Process in the knowledge graph.
        Process -executes-> ProcessExecution -generates-> DerivedFile
        """
        derived_files: list[KGNode] = []
        print([e for e in graph.get_node_edges(process_node_id)])
        for edge in [e for e in graph.get_node_edges(process_node_id, position="source") if e.relation == "executes"]:
            process_exec_node: KGNode = graph.nodes[edge.target]
            for gen_edge in [e for e in graph.get_node_edges(process_exec_node.id, position="source") if e.relation == "generates"]:
                derived_file_node: KGNode = graph.nodes[gen_edge.target]
                derived_files.append(derived_file_node)
        return derived_files
        
    def set_subjects_sessions(self, subjects_sessions: Optional[dict[str, list[str]]] = None) -> None:
        if subjects_sessions is not None:
            self.subjects_sessions = subjects_sessions
            return
        subjects: list[str] = self.layout.get_subjects()
        subjects_sessions: dict[str, list[str]] = {}
        for subject in subjects:
            sessions: list[str] = self.layout.get_sessions(subject=subject)
            subjects_sessions[subject] = sessions
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
        raw_file_node_id: str = f"{dataset_node_id}::rawfile:{self.normalize_file_path(file_no_extension)}"
        return raw_file_node_id
    
    def get_derived_file_node_id(self, derivative_name: str, file_no_extension: str | Path) -> str:
        """
        Get the node ID for a given derivative file (without extension) in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        dataset_node_id: str = self.get_dataset_node_id()
        derivative_file_node_id: str = f"{dataset_node_id}::derivative:{derivative_name}::file:{self.normalize_file_path(file_no_extension)}"
        return derivative_file_node_id
    
    def get_dicomheaders_node_id(self, file_no_extension: str | Path) -> str:
        """
        Get the node ID for the DICOMHeaders node of a given file in the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        file_node_id: str = self.get_raw_file_node_id(self.normalize_file_path(file_no_extension))
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
        
        file_no_extensions = {self.remove_file_extension(self.normalize_file_path(f)) for f in files}
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
        derivative_file_node_id: str = self.get_derived_file_node_id(derivative_name, self.normalize_file_path(file_no_extension))
        try:
            sidecar_data: dict = self.get_sidecar_data(file_no_extension)
        except FileNotFoundError:
            sidecar_data = {}
        process_id: str = sidecar_data.get("ProcessID")
        process_exec_id: str = sidecar_data.get("ProcessExecID")
        return KGNode(
            id=derivative_file_node_id,
            label="DerivedFile",
            layer="data",
            properties={
                "stem": self.normalize_file_path(file_no_extension),
                "derivative_name": derivative_name,
                "dataset_id": dataset_node_id,
                "process_id": process_id,
                "process_exec_id": process_exec_id
            }
        )
    
    def add_derived_file_node(self, derivative_name: str, file_no_extension: str | Path):
        self.graph.add_node(self.create_derived_file_node(derivative_name, file_no_extension))
    
    def create_pipeline_step_node(self, step_number: int, derivative_name: str, step_name: str, step_description: str) -> KGNode:
        pipeline_step_node_id: str = self.get_pipeline_step_node_id(derivative_name, step_name)
        return KGNode(
            id=pipeline_step_node_id,
            label="PipelineStep",
            layer="provenance",
            properties={
                "id": pipeline_step_node_id,
                "name": step_name,
                "description": step_description,
                "step_number": step_number,
                "derivative_name": derivative_name
            }
        )
    
    def add_pipeline_step_node(self, step_number: int, derivative_name: str, step_name: str, step_description: str):
        self.graph.add_node(self.create_pipeline_step_node(step_number, derivative_name, step_name, step_description))
    
    def create_process_node(self, process_id: str) -> KGNode:
        process_node_id: str = self.get_process_node_id(process_id)
        return KGNode(
            id=process_node_id,
            label="Process",
            layer="provenance",
            properties={
                "process_id": process_id,
                "id": process_node_id
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
                "process_id": process_id,
                "id": process_exec_node_id
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
            layer="data",
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
        raw_file_node_id: str = self.get_raw_file_node_id(self.normalize_file_path(file_no_extension))
        session_node_id: str = self.get_session_node_id(session_id)
        return KGEdge(
            source=raw_file_node_id,
            target=session_node_id,
            relation="hasSession",
            properties={
                "stem": self.normalize_file_path(file_no_extension),
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
                "stem": self.normalize_file_path(file_no_extension),
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
        raw_file_node_id: str = self.get_raw_file_node_id(self.normalize_file_path(file_no_extension))
        return KGEdge(
            source=dataset_node_id,
            target=raw_file_node_id,
            relation="hasRawFile",
            properties={
                "dataset_id": dataset_node_id,
                "stem": self.normalize_file_path(file_no_extension),
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
        raw_file_node_id: str = self.get_raw_file_node_id(self.normalize_file_path(file_no_extension))
        subject_node_id: str = self.get_subject_node_id(subject)
        return KGEdge(
            source=raw_file_node_id,
            target=subject_node_id,
            relation="hasSubject",
            properties={
                "subject_id": subject,
                "stem": self.normalize_file_path(file_no_extension),
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
                "stem": self.normalize_file_path(file_no_extension),
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
        raw_file_node_id: str = self.get_raw_file_node_id(self.normalize_file_path(file_no_extension))
        dicomheaders_node_id: str = self.get_dicomheaders_node_id(self.normalize_file_path(file_no_extension))
        return KGEdge(
            source=raw_file_node_id,
            target=dicomheaders_node_id,
            relation="hasDICOMHeaders",
            properties={
                "stem": self.normalize_file_path(file_no_extension),
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
        raw_file_node_id: str = self.get_raw_file_node_id(self.normalize_file_path(file_no_extension))
        bids_entity_node_id: str = self.get_BIDSEntity_node_id(entity_name, entity_value)
        return KGEdge(
            source=raw_file_node_id,
            target=bids_entity_node_id,
            relation="hasBIDSEntity",
            properties={
                "stem": self.normalize_file_path(file_no_extension),
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
        derivative_file_node_id: str = self.get_derived_file_node_id(derivative_name, self.normalize_file_path(file_no_extension))
        bids_entity_node_id: str = self.get_BIDSEntity_node_id(entity_name, entity_value)
        return KGEdge(
            source=derivative_file_node_id,
            target=bids_entity_node_id,
            relation="hasBIDSEntity",
            properties={
                "stem": self.normalize_file_path(file_no_extension),
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
        
    def create_hasStep_edge(self, step_number: int, derivative_name: str, step_name: str) -> KGEdge:
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
                "step_number": step_number,
                "relationship": "hasStep"
            }
        )
    
    def add_hasStep_edge(self, step_number: int, derivative_name: str, step_name: str):
        """
        Pipeline -hasStep-> PipelineStep
        """
        self.graph.add_edge(self.create_hasStep_edge(step_number, derivative_name, step_name))
    
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
    
    def build_graph(self):
        self.graph = KGGraph(nodes={}, edges=[])
        self.add_dataset_node()
        self.set_subjects_sessions()
        for subject, session_ids in self.subjects_sessions.items():
            self.add_subject_node(subject)
            for session_id in session_ids:
                self.add_session_node(session_id)
                self.add_subject_hasSession_edge(subject, session_id) # Subject -hasSession-> Session
        
        if "raw" in self.scopes:
            self.build_basic_graph()
        for scope in self.scopes:
            if scope != "raw":
                self.add_derivative_to_graph(scope)
    
    def build_basic_graph(self):
        """
        Build the knowledge graph for the raw dataset.
        """
        
        # Subject and session nodes
        if not self.subjects_sessions:
            self.set_subjects_sessions()
        for subject, session_ids in self.subjects_sessions.items():
            # self.add_subject_node(subject)
            for session_id in session_ids:
                sess_node_id: str = self.get_session_node_id(session_id)
                # self.add_session_node(session_id)
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
        """
        Add a derivative dataset and its provenance to the knowledge graph.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        if derivative_name not in self.scopes:
            self.scopes.append(derivative_name)
        
        dataset_description: BIDSDatasetDescription = self.add_pipeline_node(derivative_name)
        
        # Add Pipeline, PipelineSteps, Process, ProcessExecution, Logic nodes and edges
        for step_number, step in enumerate(dataset_description.PipelineSteps):
            step_name: str = step["name"]
            step_description: str = step.get("description", "")
            self.add_pipeline_step_node(step_number, derivative_name, step_name, step_description)
            self.add_hasStep_edge(step_number, derivative_name, step_name) # Pipeline -hasStep-> PipelineStep
            # Collect process_ids and their respective process_exec_ids
            processes: dict[str, list[str]] = {}
            for info in step.get("processes"):
                process_id: str = info["process_id"]
                process_exec_id: str = info["process_exec_id"]
                if process_id not in processes:
                    processes[process_id] = []
                processes[process_id].append(process_exec_id)
            for process_id, process_exec_ids in processes.items():
                self.add_process_node(process_id)
                self.add_realizesProcess_edge(derivative_name, step_name, process_id) # PipelineStep -realizesProcess-> Process
                
                process: NeuProcess = NeuProcess.from_process_id(process_id)
                logic: NeuProcessLogic = process.logic
                self.add_logic_node(logic)
                self.add_usesLogic_edge(process_id, logic.about.name) # Process -usesLogic-> Logic
                for process_exec_id in process_exec_ids:
                    self.add_process_execution_node(process_id, process_exec_id)
                    self.add_executes_edge(process_id, process_exec_id) # Process -executes-> ProcessExecution
                    
        # Add DerivedFile nodes and edges
        for derivative_file_no_extension in self.get_files_no_extension(scope=derivative_name):
            self.add_derived_file_node(derivative_name, derivative_file_no_extension)
            self.add_hasDerivedFile_edge(derivative_name, derivative_file_no_extension) # Pipeline -hasDerivedFile-> DerivedFile
            
            # Link DerivedFile to Session and Subject
            bids_entities: dict = parse_file_entities(derivative_file_no_extension)
            subject: str = bids_entities.get("subject")
            session_id: Optional[str] = bids_entities.get("session")
            if subject:
                self.add_derivedFile_hasSubject_edge(derivative_name, derivative_file_no_extension, subject) # DerivedFile -hasSubject-> Subject
            if session_id:
                self.add_derivedFile_hasSession_edge(derivative_name, derivative_file_no_extension, session_id) # DerivedFile -hasSession-> Session
                
            try:
                derived_file_sidecar: dict = self.get_sidecar_data(derivative_file_no_extension)
            except FileNotFoundError:
                continue
            if "BIDSEntities" not in derived_file_sidecar:
                continue
            for key, value in {key: value for key, value in derived_file_sidecar.get("BIDSEntities").items() if key not in ['subject', 'session']}.items():
                self.add_BIDSEntity_node(key, value)
                self.add_derivedFile_hasBIDSEntity_edge(derivative_name, derivative_file_no_extension, key, value) # DerivedFile -hasBIDSEntity-> BIDSEntity
            
            process_id: str = derived_file_sidecar.get("ProcessID")
            process_exec_id: str = derived_file_sidecar.get("ProcessExecID")
            self.add_executes_edge(process_id, process_exec_id) # Process -executes-> ProcessExecution
            self.add_generates_edge(derivative_name, process_id, process_exec_id, derivative_file_no_extension) # ProcessExecution -generates-> DerivedFile
            
            input_file: str = derived_file_sidecar.get("InputFile")
            input_file_no_extension: str = self.remove_file_extension(self.normalize_file_path(input_file))
            # Determine if input file is RawFile or DerivedFile - add usedBy and derivedFrom edges accordingly
            # DerivedFile path has */derivatives/... structure
            if Path(input_file_no_extension).is_relative_to(Path(self.bids_root) / "derivatives"):
                # Input file is a DerivedFile
                input_file_derivative_name: str = Path(input_file_no_extension).relative_to(Path(self.bids_root) / "derivatives").parts[0]
                self.add_derived_file_node(input_file_derivative_name, input_file_no_extension)
                self.add_derivedFrom_edge(derivative_name, derivative_file_no_extension, self.get_derived_file_node_id(input_file_derivative_name, input_file_no_extension)) # DerivedFile -derivedFrom-> DerivedFile
                self.add_usedBy_edge(self.get_derived_file_node_id(input_file_derivative_name, input_file_no_extension), process_id, process_exec_id) # DerivedFile -usedBy-> ProcessExecution
            else:
                # Input file is a RawFile
                input_file_bids_entities: dict = parse_file_entities(input_file_no_extension)
                input_file_subject: str = input_file_bids_entities.get("subject")
                input_file_session_id: Optional[str] = input_file_bids_entities.get("session")
                self.add_raw_file_node(input_file_no_extension, input_file_subject, input_file_session_id)
                if input_file_subject:
                    self.add_rawFile_hasSubject_edge(input_file_no_extension, input_file_subject) # RawFile -hasSubject-> Subject
                if input_file_session_id:
                    self.add_rawFile_hasSession_edge(input_file_no_extension, input_file_session_id) # RawFile -hasSession-> Session
                self.add_derivedFrom_edge(derivative_name, derivative_file_no_extension, self.get_raw_file_node_id(input_file_no_extension)) # DerivedFile -derivedFrom-> RawFile
                self.add_usedBy_edge(self.get_raw_file_node_id(input_file_no_extension), process_id, process_exec_id) # RawFile -usedBy-> ProcessExecution
                
            # Add Metric nodes and edges
            metrics: list[Metric] = Metric.from_dict(derived_file_sidecar, "metrics")
            for metric in metrics:
                self.add_metric_node(metric)
                self.add_hasMetric_edge(self.get_derived_file_node_id(derivative_name, derivative_file_no_extension), metric) # DerivedFile -hasMetric-> Metric
            
                
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
    
    def identify_erroneous_execs(self) -> list[NeuProcessExec]:
        """
        Identify ProcessExecutions that have missing derived files in their audit trails.
        Returns a list of NeuProcessExec objects corresponding to the erroneous executions.
        1. For each DerivedFile in the graph, retrieve its full audit trail.
        2. Split the audit trail by pipeline.
        3. For each pipeline-specific audit trail, identify missing files.
        4. Collect and return the corresponding NeuProcessExec objects for processes with missing files.
        5. Limit to first 3 DerivedFile nodes for efficiency.
        6. Print out the exec log paths for easy access.
        7. Return the list of NeuProcessExec objects.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        
        erroneous_execs: list[NeuProcessExec] = []
        
        for derived_file_node in self.graph.search_nodes(label="DerivedFile")[:3]:
            derived_file_node_id: str = derived_file_node.id
            audit_trail: AuditTrail = AuditTrail(self.graph, derived_file_node_id)
            # print(f"Derived File: {derived_file_node.properties.get('file_name', derived_file_node.id).split('::')[-1].split(':')[-1].split('/')[-1]}")
            
            all_pipeline_audit_trails: dict[str, AuditTrail] = {pipeline_name: AuditTrail(graph=pipeline_graph, file_node_id=derived_file_node_id) for pipeline_name, pipeline_graph in audit_trail.split_by_pipeline(forward_only=False).items()}
            
            for pipeline_name, pipeline_audit_trail in all_pipeline_audit_trails.items():
                if derived_file_node.properties.get("derivative_name", "") != pipeline_name:
                    continue
                print(f"Checking missing files for pipeline: {pipeline_name}")
                for process_id, missing_file_count in pipeline_audit_trail.identify_missing_files(self.bids_root, forward_only=False).items():
                    if missing_file_count > 0:
                        process_exec_ids: list[str] = BIDSDataset.identify_process_execs_from_file_stem(self.bids_root, pipeline_name, derived_file_node.properties.get('file_name', derived_file_node.id).split('::')[-1].split(':')[-1], process_id)
                        print(f"Missing files for Process ID {process_id}: {missing_file_count}. Check exec logs here:")
                        print("\n".join([f"  - {NeuProcessExec.from_exec_id(exec_id).exec_log_path}" for exec_id in process_exec_ids]))
                        erroneous_execs.extend([NeuProcessExec.from_exec_id(exec_id) for exec_id in process_exec_ids])
                print()
            print()
        
        return erroneous_execs
    
    def get_metric_connections(self) -> pd.DataFrame:
        """
        Retrieve a DataFrame of all Metric nodes and their connections to DerivedFile nodes.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        
        metric_connections: list[dict[str, any]] = []
        
        for edge in self.graph.edges:
            if edge.relation == "hasMetric":
                derived_file_node: KGNode = self.graph.nodes[edge.source]
                metric_node: KGNode = self.graph.nodes[edge.target]
                metric_connections.append({
                    "derived_file_id": derived_file_node.id,
                    "derived_file_name": Path(derived_file_node.properties.get("stem", "")).name,
                    "metric_id": metric_node.id,
                    "metric_name": metric_node.properties.get("name", ""),
                    "metric_value": metric_node.properties.get("value", None),
                    "metric_unit": metric_node.properties.get("unit", ""),
                    "metric_description": metric_node.properties.get("description", "")
                })
        
        return pd.DataFrame(metric_connections)

class AuditTrail:
    """
    Class to retrieve the audit trail (provenance chain) for a given file node.
    Only contains RawFile and DerivedFile nodes connected via `derivedFrom` edges.
    """
    graph: KGGraph # Reference to the complete knowledge graph
    file_node_id: str
    
    def __init__(self, graph: KGGraph, file_node_id: str):
        self.graph = graph
        self.file_node_id = file_node_id
    
    def __get_audit_trail(self, forward_only: bool, show_metrics: bool = True) -> KGGraph:
        """
        Retrieve the audit trail graph for the specified file node.
        If forward_only is True, only follow edges in the forward direction (from source to target).
        If forward_only is False, follow edges in both directions.
        If show_metrics is True, include Metric nodes connected to DerivedFile nodes.
        """
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")

        if self.file_node_id not in self.graph.nodes:
            raise ValueError(f"File node {self.file_node_id} not found in graph.")

        audit_trail_graph = KGGraph(nodes={}, edges=[])
        visited: set[str] = set()
        queue = deque([self.file_node_id])

        audit_trail_graph.add_node(self.graph.nodes[self.file_node_id])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            current_node = self.graph.nodes[current]

            # RawFile is always a terminal sink
            if current_node.label == "RawFile":
                continue
            
            relations_to_consider = ["derivedFrom"]
            if show_metrics and current_node.label == "DerivedFile":
                relations_to_consider.append("hasMetric")

            for edge in self.graph.get_node_edges(current):
                if edge.relation not in relations_to_consider:
                    continue

                if forward_only and current != edge.source:
                    # Only follow edges in the forward direction
                    continue
                
                if edge.relation == "hasMetric":
                    # Always add Metric nodes without further traversal
                    audit_trail_graph.add_node(self.graph.nodes[edge.target])
                    audit_trail_graph.add_edge(edge)
                    continue
                
                neighbor = (
                    edge.target if edge.source == current
                    else edge.source
                )

                audit_trail_graph.add_node(self.graph.nodes[neighbor])
                audit_trail_graph.add_edge(edge)

                if neighbor not in visited:
                    queue.append(neighbor)

        return audit_trail_graph
    
    @property
    def forward_only(self) -> KGGraph:
        return self.__get_audit_trail(forward_only=True)
    
    @property
    def full(self) -> KGGraph:
        return self.__get_audit_trail(forward_only=False)
    
    @property
    def signature(self, forward_only: bool) -> str:
        """
        Generate a signature string for the audit trail graph.
        Iterate over nodes and edges in a consistent order to create a unique signature.
        """
        audit_trail: KGGraph = self.__get_audit_trail(forward_only=forward_only)
        
        node_signatures: list[str] = []
        for node_id in sorted(audit_trail.nodes.keys()):
            node = audit_trail.nodes[node_id]
            props_str = ",".join(f"{k}={v}" for k, v in sorted(node.properties.items()))
            node_signatures.append(f"Node(id={node.id},label={node.label},properties={{ {props_str} }})")
            
        edge_signatures: list[str] = []
        for edge in sorted(audit_trail.edges, key=lambda e: (e.source, e.target, e.relation)):
            props_str = ",".join(f"{k}={v}" for k, v in sorted(edge.properties.items()))
            edge_signatures.append(f"Edge(source={edge.source},target={edge.target},relation={edge.relation},properties={{ {props_str} }})")
            
        signature_str = " | ".join(node_signatures + edge_signatures)
        return signature_str
    
    def is_equal_to(self, other: Self, forward_only: bool = True) -> bool:
        """
        Check if the audit trail of this file node is equal to that of another file node.
        """
        self_audit_trail: Self = self.__get_audit_trail(forward_only=forward_only)
        other_audit_trail: Self = other.__get_audit_trail(forward_only=forward_only)
        return self_audit_trail.signature == other_audit_trail.signature
    
    def filter_by_pipeline(self, pipeline_name: str) -> KGGraph:
        """
        Filter the audit trail graph to include only nodes and edges related to a specific pipeline.
        """
        audit_trail: KGGraph = self.full
        filtered_graph = KGGraph(nodes={}, edges=[])
        
        # Identify relevant nodes
        relevant_node_ids: set[str] = set()
        for node in audit_trail.nodes.values():
            if node.label == "DerivedFile":
                derivative_name: str = node.properties.get("derivative_name", "")
                if derivative_name == pipeline_name:
                    relevant_node_ids.add(node.id)
            elif node.label == "RawFile":
                relevant_node_ids.add(node.id) # Include RawFile nodes since they are sources
            else:
                continue
            
        # Add relevant nodes and edges
        for node_id in relevant_node_ids:
            filtered_graph.add_node(audit_trail.nodes[node_id])
            for edge in audit_trail.get_node_edges(node_id):
                if edge.source in relevant_node_ids and edge.target in relevant_node_ids:
                    filtered_graph.add_node(audit_trail.nodes[edge.source])
                    filtered_graph.add_node(audit_trail.nodes[edge.target])
                    filtered_graph.add_edge(edge)
        return filtered_graph
    
    def split_by_pipeline(self, forward_only: bool = False) -> dict[str, KGGraph]:
        """
        Split the audit trail graph into multiple graphs, each corresponding to a different pipeline.
        Returns a dictionary mapping pipeline names to their respective audit trail graphs.
        """
        audit_trail: KGGraph = self.__get_audit_trail(forward_only=forward_only)
        pipeline_graphs: dict[str, KGGraph] = {}
        
        # Identify pipelines in the audit trail
        for node in audit_trail.nodes.values():
            if node.label == "DerivedFile":
                derivative_name: str = node.properties.get("derivative_name", "")
                if derivative_name not in pipeline_graphs:
                    pipeline_graphs[derivative_name] = KGGraph(nodes={}, edges=[])
        
        # Populate each pipeline graph
        for pipeline_name, graph in pipeline_graphs.items():
            for node in audit_trail.nodes.values():
                if node.label == "DerivedFile" and node.properties.get("derivative_name", "") == pipeline_name:
                    graph.add_node(node)
                    for edge in audit_trail.get_node_edges(node.id):
                        if edge.source in graph.nodes and edge.target in graph.nodes:
                            graph.add_node(audit_trail.nodes[edge.source])
                            graph.add_node(audit_trail.nodes[edge.target])
                            graph.add_edge(edge)
        return pipeline_graphs
    
    def identify_missing_files(self, bids_root: str, forward_only: bool = True) -> list[str]:
        """
        Every pipeline-specific audit trail should consist of a DerivedFile node associated with
        each process in the pipeline's steps. Identify any missing DerivedFile nodes in the audit trail.
        """
        if len(self.split_by_pipeline(forward_only=forward_only)) > 1:
            raise ValueError("Audit trail contains multiple pipelines; cannot identify missing files.")
        audit_trail: KGGraph = self.__get_audit_trail(forward_only=forward_only)
        missing_files: dict[str, int] = {}
        for node in audit_trail.nodes.values():
            if node.label == "DerivedFile":
                derivative_name: str = node.properties.get("derivative_name", "")
                with open(Path(bids_root) / "derivatives" / derivative_name / "dataset_description.json", "r") as f:
                    dataset_description_json = json.load(f)
                dataset_description: BIDSDatasetDescription = BIDSDatasetDescription.model_validate(dataset_description_json)
                # Get all process_ids in the pipeline with the number of times 
                all_process_ids: dict[str, int] = {}
                for step in dataset_description.PipelineSteps:
                    unique_process_ids: list[str] = list(set([info.get("process_id") for info in step.get("processes", [])]))
                    for process_id in unique_process_ids:
                        if process_id not in all_process_ids:
                            all_process_ids[process_id] = 0
                        all_process_ids[process_id] += 1
                # Count occurrences of each process_id in the audit trail
                audit_trail_process_counts: dict[str, int] = {}
                for node in audit_trail.nodes.values():
                    if node.label == "DerivedFile":
                        process_id: str = node.properties.get("process_id", "")
                        if process_id:
                            if process_id not in audit_trail_process_counts:
                                audit_trail_process_counts[process_id] = 0
                            audit_trail_process_counts[process_id] += 1
                # Identify missing process_ids
                for process_id, required_count in all_process_ids.items():
                    actual_count: int = audit_trail_process_counts.get(process_id, 0)
                    missing_files[process_id] = required_count - actual_count
                        
        return missing_files
    
    def visualize_str(self, forward_only: bool = True, include_properties: bool = False, max_property_length: int = 50) -> str:
        """
        Generate a string representation of the audit trail graph for visualization.
        
        Args:
        forward_only: Whether to follow edges only in forward direction
        include_properties: Whether to include node properties in the visualization
        max_property_length: Maximum length for property values before truncation
        """
        audit_trail: KGGraph = self.__get_audit_trail(forward_only=forward_only)
        lines: list[str] = []
        
        # Add header
        lines.append(f"=== Audit Trail for {self.file_node_id} ===")
        lines.append(f"Nodes: {len(audit_trail.nodes)} | Edges: {len(audit_trail.edges)}")
        lines.append("")
        
        # Group edges by relation type
        edges_by_relation: dict[str, list[KGEdge]] = {}
        for edge in audit_trail.edges:
            if edge.relation not in edges_by_relation:
                edges_by_relation[edge.relation] = []
            edges_by_relation[edge.relation].append(edge)
        
        # Visualize edges grouped by relation
        for relation, edges in sorted(edges_by_relation.items()):
            lines.append(f"[{relation}] ({len(edges)} edges):")
            for edge in edges:
                source_node = audit_trail.nodes[edge.source]
                target_node = audit_trail.nodes[edge.target]
                
                # Format node labels
                source_label = f"{source_node.label}"
                target_label = f"{target_node.label}"
                
                # Add properties if requested
                if include_properties:
                    source_props = self._format_properties(source_node.properties, max_property_length)
                    target_props = self._format_properties(target_node.properties, max_property_length)
                    lines.append(f"  {source_label}{source_props} --> {target_label}{target_props}")
                else:
                    source_id = source_node.id.split("::")[-1].split("/")[-1] if "::" in source_node.id else source_node.id
                    target_id = target_node.id.split("::")[-1].split("/")[-1] if "::" in target_node.id else target_node.id
                    lines.append(f"  {source_label}[{source_id}] --> {target_label}[{target_id}]")
                lines.append("")
        
        return "\n".join(lines)
    
    def _format_properties(self, properties: dict, max_length: int) -> str:
        """Helper method to format node properties for display."""
        if not properties:
            return ""
        
        key_props = ["stem", "subject_id", "session_id", "derivative_name", "process_id"]
        relevant_props = {k: v for k, v in properties.items() if k in key_props and v is not None}
        
        if not relevant_props:
            return ""
        
        props_str = ", ".join(f"{k}={str(v)[:max_length]}" for k, v in relevant_props.items())
        return f"[{props_str}]"