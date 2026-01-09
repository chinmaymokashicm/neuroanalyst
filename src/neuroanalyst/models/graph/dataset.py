from ..bids import BIDSDatasetDescription
from .core import KGGraph, KGNode, KGEdge
from ..process.process.core import NeuProcess
from ..process.logic.core import NeuProcessLogic

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
    def from_directory(cls, path: Path, derivatives_paths: Optional[list[Path]] = None) -> "BIDSDataset":
        layout: BIDSLayout = BIDSLayout(str(path), validate=False, derivatives=[str(p) for p in derivatives_paths] if derivatives_paths else None)
        dataset_description_data: dict = layout.get_dataset_description()
        dataset_description: BIDSDatasetDescription = BIDSDatasetDescription(**dataset_description_data)
        
        # Load derivatives datasets
        internal_derivative_paths: list[Path] = list(path.glob("derivatives/*"))
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
        
    def get_file_stems(self, scope: str, subject_id: Optional[str] = None, session_id: Optional[str] = None) -> set[str]:
        """
        Get file stems for a given subject and session. Stems to exclude sidecar files or repeated files.
        """
        if subject_id is None and session_id is not None:
            raise ValueError("Subject ID must be provided if session ID is specified.")
        
        if scope == "raw":
            layout = self.layout
        else:
            derivative_datasets = [d for d in self.derivatives if d.dataset_description.Name == scope]
            if not derivative_datasets:
                raise ValueError(f"No derivative dataset found with name: {scope}")
            layout = derivative_datasets[0].layout
        
        files = layout.get(
            subject=subject_id,
            session=session_id,
            return_type="file"
        )
        
        file_stems = set([f.split(".")[0] for f in files])
        return file_stems

    def search_nodes(self, label: str, property_filters: Optional[dict] = None) -> list[KGNode]:
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        
        matched_nodes: list[KGNode] = []
        for node in self.graph.nodes.values():
            if node.label != label:
                continue
            if property_filters:
                if all(node.properties.get(k) == v for k, v in property_filters.items()):
                    matched_nodes.append(node)
            else:
                matched_nodes.append(node)
        return matched_nodes
    
    def normalize_file_path(self, file_path: str |Path) -> Path:
        try:
            file_path = Path(file_path)
            relative_path = file_path.relative_to("/data")
            normalized_path = self.bids_root / relative_path
            return normalized_path
        except ValueError:
            return file_path
    
    def build_basic_graph(self):
        self.graph = KGGraph(nodes={}, edges=[])
        
        # Dataset node
        dataset_node_id: str = f"dataset:{self.bids_root.name}"
        self.graph.add_node(KGNode(id=dataset_node_id, label="Dataset", layer="data", properties={"id": dataset_node_id}))
        
        # Subject and session nodes
        if not self.subjects_sessions:
            self.set_subjects_sessions()
        for subj, sessions in self.subjects_sessions.items():
            subj_node_id: str = f"{dataset_node_id}::subject:{subj}"
            self.graph.add_node(
                KGNode(id=subj_node_id, label="Subject", layer="data", properties={"id": subj, "dataset_id": dataset_node_id})
            )
            for sess in sessions:
                sess_node_id: str = f"{subj_node_id}::session:{sess}"
                self.graph.add_node(
                    KGNode(id=sess_node_id, label="Session", layer="data", properties={"id": sess, "subject_id": subj, "dataset_id": dataset_node_id})
                )
                self.graph.add_edge(
                    KGEdge(source=subj_node_id, target=sess_node_id, relation="hasSession", properties={})
                ) # Subject -hasSession-> Session
            # Raw file nodes
            for raw_file_stem in self.get_file_stems(scope="raw", subject_id=subj):
                raw_file_node_id: str = f"{dataset_node_id}::file:{raw_file_stem}"
                self.graph.add_node(
                    KGNode(id=raw_file_node_id, label="RawFile", layer="data", properties={"stem": raw_file_stem, "session_id": sess, "subject_id": subj, "dataset_id": dataset_node_id})
                )
                self.graph.add_edge(
                    KGEdge(source=dataset_node_id, target=raw_file_node_id, relation="hasRawFile", properties={})
                ) # Dataset -hasRawFile-> RawFile
                self.graph.add_edge(
                    KGEdge(source=raw_file_node_id, target=subj_node_id, relation="hasSubject", properties={})
                ) # RawFile -hasSubject-> Subject
                self.graph.add_edge(
                    KGEdge(source=raw_file_node_id, target=sess_node_id, relation="hasSession", properties={})
                ) # RawFile -hasSession-> Session
                
                # DICOMHeaders node
                raw_sidecar_path: Path = raw_file_stem + ".json"
                try:
                    with open(raw_sidecar_path, 'r') as f:
                        dicom_data: dict = json.load(f)
                    dicomheaders_node_id: str = f"{raw_file_node_id}::DICOMHeaders"
                    self.graph.add_node(
                        KGNode(id=dicomheaders_node_id, label="DICOMHeaders", layer="data", properties=dicom_data)
                    )
                    self.graph.add_edge(
                        KGEdge(source=raw_file_node_id, target=dicomheaders_node_id, relation="hasDICOMHeaders", properties={})
                    ) # RawFile -hasDICOMHeaders-> DICOMHeaders
                    
                    # Add BIDSEntity nodes from sidecar
                    bids_entities: dict = {key: value for key, value in parse_file_entities(str(raw_sidecar_path)).items() if key not in ['subject', 'session']}
                    for entity_name, entity_value in bids_entities.items():
                        bids_entity_node_id: str = f"{raw_file_node_id}::BIDSEntity:{entity_name}:{entity_value}"
                        self.graph.add_node(
                            KGNode(id=bids_entity_node_id, label="BIDSEntity", layer="data", properties={"name": entity_name, "value": entity_value})
                        )
                        self.graph.add_edge(
                            KGEdge(source=raw_file_node_id, target=bids_entity_node_id, relation="hasBIDSEntity", properties={})
                        ) # RawFile -hasBIDSEntity-> BIDSEntity
                    
                except FileNotFoundError:
                    print(f"No sidecar file found for {raw_file_stem} at {raw_sidecar_path}, skipping DICOMHeaders node.")
                    pass
                
    def add_derivative_to_graph(self, derivative_name: str):
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        
        try:
            derivative_dataset: Self = [d for d in self.derivatives if d.dataset_description.Name == derivative_name][0]
        except IndexError:
            raise ValueError(f"No derivative dataset found with name: {derivative_name}")
        
        dataset_node_id: str = self.search_nodes(label="Dataset", property_filters={"id": f"dataset:{self.bids_root.name}"})[0].id
        pipeline_node_id: str = f"{dataset_node_id}::pipeline:{derivative_name}"
        
        dataset_description: BIDSDatasetDescription = derivative_dataset.dataset_description
        pipeline_id: str = dataset_description.GeneratedBy[0].get("ID", "")
        
        self.graph.add_node(KGNode(
            id=pipeline_node_id,
            label="Pipeline",
            layer="provenance",
            properties={
                "name": derivative_name,
                "pipeline_id": pipeline_id
            }
        ))
        self.graph.add_edge(KGEdge(
            source=dataset_node_id,
            target=pipeline_node_id,
            relation="hasPipeline",
            properties={}
        )) # Dataset -hasPipeline-> Pipeline
        
        # Get pipeline steps
        for step_idx, pipeline_step in enumerate(dataset_description.PipelineSteps):
            step_name: str = pipeline_step.get("Name", step_idx+1)
            step_node_id: str = f"{pipeline_node_id}::step:{step_name}"
            step_description: str = pipeline_step.get("Description", "")
            self.graph.add_node(KGNode(
                id=step_node_id,
                label="PipelineStep",
                layer="provenance",
                properties={
                    "name": step_name,
                    "description": step_description,
                    "pipeline_id": pipeline_id
                }
            ))
            # Get process_ids from this step
            processes: dict[str, list[str]] = {}
            for item in pipeline_step.get("processes", []):
                process_id: str = item.get("process_id", "")
                if process_id not in processes:
                    processes[process_id] = []
                processes[process_id].append(item.get("process_exec_id", {}))
            for process_id, exec_ids in processes.items():
                process_node_id: str = f"{step_node_id}::process:{process_id}"
                self.graph.add_node(KGNode(
                    id=process_node_id,
                    label="Process",
                    layer="provenance",
                    properties={
                        "process_id": process_id,
                    }
                ))
                self.graph.add_edge(KGEdge(
                    source=step_node_id,
                    target=process_node_id,
                    relation="realizesProcess",
                    properties={}
                )) # PipelineStep -realizesProcess-> Process
                
                for exec_id in exec_ids:
                    process_exec_node_id: str = f"{process_node_id}::execution:{exec_id}"
                    self.graph.add_node(KGNode(
                        id=process_exec_node_id,
                        label="ProcessExecution",
                        layer="provenance",
                        properties={
                            "process_exec_id": exec_id,
                            "process_id": process_id,
                        }
                    ))
                    self.graph.add_edge(KGEdge(
                        source=process_node_id,
                        target=process_exec_node_id,
                        relation="executes",
                        properties={}
                    )) # Process -executes-> ProcessExecution
                
                # Logic node
                process: NeuProcess = NeuProcess.from_process_id(process_id)
                logic: NeuProcessLogic = process.logic
                logic_node_id: str = f"{process_node_id}::logic:{logic.logic_id}"
                self.graph.add_node(KGNode(
                    id=logic_node_id,
                    label="Logic",
                    layer="provenance",
                    properties={
                        "name": logic.about.name,
                        "description": logic.about.description,
                        "code": logic.code,
                    }
                ))
                self.graph.add_edge(KGEdge(
                    source=process_node_id,
                    target=logic_node_id,
                    relation="usesLogic",
                    properties={}
                )) # Process -usesLogic-> Logic
                
        # Derivative file nodes
        for deriv_file_stem in derivative_dataset.get_file_stems(scope=derivative_name):
            deriv_file_node_id: str = f"{pipeline_node_id}::file:{deriv_file_stem}"
            self.graph.add_node(
                KGNode(id=deriv_file_node_id, label="DerivedFile", layer="data", properties={"stem": deriv_file_stem, "dataset_id": dataset_node_id})
            )
            self.graph.add_edge(
                KGEdge(source=pipeline_node_id, target=deriv_file_node_id, relation="hasDerivedFile", properties={})
            ) # Pipeline -hasDerivedFile-> DerivedFile
            
            deriv_file_sidecar_path: Path = deriv_file_stem + ".json"
            try:
                with open(deriv_file_sidecar_path, 'r') as f:
                    sidecar_data: dict = json.load(f)
                process_exec_id: str = sidecar_data.get("ProcessExecID")
                process_exec_node_id: str = f"{pipeline_node_id}::step::{process_exec_id}"
                self.graph.add_edge(
                    KGEdge(source=process_exec_node_id, target=deriv_file_node_id, relation="generates", properties={})
                ) # ProcessExecution -generates-> DerivedFile
                
                # Get BIDSEntity nodes from sidecar
                bids_entities: dict = {key: value for key, value in parse_file_entities(str(deriv_file_sidecar_path)).items()}
                subject_id: str = bids_entities.get("subject", "")
                session_id: str = bids_entities.get("session", "")
                subj_node_id: str = f"{dataset_node_id}::subject:{subject_id}"
                sess_node_id: str = f"{subj_node_id}::session:{session_id}"
                self.graph.add_edge(
                    KGEdge(source=deriv_file_node_id, target=subj_node_id, relation="hasSubject", properties={})
                ) # DerivedFile -hasSubject-> Subject
                self.graph.add_edge(
                    KGEdge(source=deriv_file_node_id, target=sess_node_id, relation="hasSession", properties={})
                ) # DerivedFile -hasSession-> Session
                
                for entity_name, entity_value in bids_entities.items():
                    if entity_name in ["subject", "session"]:
                        continue
                    bids_entity_node_id: str = f"{deriv_file_node_id}::BIDSEntity:{entity_name}:{entity_value}"
                    self.graph.add_node(
                        KGNode(id=bids_entity_node_id, label="BIDSEntity", layer="data", properties={"name": entity_name, "value": entity_value})
                    )
                    self.graph.add_edge(
                        KGEdge(source=deriv_file_node_id, target=bids_entity_node_id, relation="hasBIDSEntity", properties={})
                    ) # DerivedFile -hasBIDSEntity-> BIDSEntity
                    
                # Find the RawFile/DerivedFile it was derived from
                input_file: str = sidecar_data.get("InputFile", "")
                if input_file:
                    input_file_path: Path = Path(input_file)
                    normalized_input_path: Path = self.normalize_file_path(input_file_path)
                    input_file_stem: str = str(normalized_input_path).split(".")[0]
                    input_file_nodes: list[KGNode] = self.search_nodes(label="RawFile", property_filters={"stem": input_file_stem})
                    if not input_file_nodes:
                        input_file_nodes = self.search_nodes(label="DerivedFile", property_filters={"stem": input_file_stem})
                    if not input_file_nodes:
                        # If the file node is not yet created, create it here
                        # Input pipeline name - {bids_root}/derivatives/{pipeline_name}/...
                        input_pipeline: str = normalized_input_path.parts[normalized_input_path.parts.index("derivatives")+1]
                        input_file_node_id: str = f"{dataset_node_id}::pipeline:{input_pipeline}::file:{input_file_stem}"
                    else:
                        input_file_node_id: str = input_file_nodes[0].id
                    self.graph.add_edge(
                        KGEdge(source=deriv_file_node_id, target=input_file_node_id, relation="derivedFrom", properties={})
                    ) # DerivedFile -derivedFrom-> RawFile/DerivedFile
                
            except FileNotFoundError:
                print(f"No sidecar file found for {deriv_file_stem} at {deriv_file_sidecar_path}.")