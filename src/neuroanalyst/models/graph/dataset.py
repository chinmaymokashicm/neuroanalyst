from ..bids import BIDSDatasetDescription
from .core import KGGraph, KGNode, KGEdge
from ..process.process.core import NeuProcess
from ..process.logic.core import NeuProcessLogic, Metric
from ...utils.data import find_and_transform_instances

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
    
    def get_derivative_file_node_id(self, derivative_name: str, file_no_extension: str | Path) -> str:
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
    
    def get_bidseentity_node_id(self, entity_name: str, entity_value: str) -> str:
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
    
    def get_files_no_extension(self, scope: str, subject_id: Optional[str] = None, session_id: Optional[str] = None) -> set[str]:
        """
        Get set of file paths (without extensions) in the dataset for a given scope, subject, and session.
        """
        if subject_id is None and session_id is not None:
            raise ValueError("Subject ID must be provided if session ID is specified.")
        
        if scope == "raw":
            layout = self.layout
        else:
            if len(self.derivatives) == 0:
                raise ValueError("No derivatives available in this dataset.")
            derivative_datasets: list[Self] = [d for d in self.derivatives if d.dataset_description.Name == scope]
            layout = derivative_datasets[0].layout
        
        if subject_id is None:
            files = layout.get(return_type="file", scope=scope)
        elif subject_id is not None and session_id is None:
            files = layout.get(subject=subject_id, return_type="file", scope=scope)
        else:
            files = layout.get(subject=subject_id, session=session_id, return_type="file", scope=scope)
        
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
    
    def build_basic_graph(self):
        self.graph = KGGraph(nodes={}, edges=[])
        
        # Dataset node
        dataset_node_id: str = self.get_dataset_node_id()
        self.graph.add_node(KGNode(id=dataset_node_id, label="Dataset", layer="data", properties={"identifier": dataset_node_id}))
        
        # Subject and session nodes
        if not self.subjects_sessions:
            self.set_subjects_sessions()
        for subject, sessions in self.subjects_sessions.items():
            subj_node_id: str = self.get_subject_node_id(subject)
            self.graph.add_node(
                KGNode(id=subj_node_id, label="Subject", layer="data", properties={"identifier": subject, "dataset_id": dataset_node_id})
            )
            for sess in sessions:
                sess_node_id: str = self.get_session_node_id(sess)
                self.graph.add_node(
                    KGNode(id=sess_node_id, label="Session", layer="data", properties={"identifier": sess, "subject_id": subject, "dataset_id": dataset_node_id})
                )
                self.graph.add_edge(KGEdge(
                    source=subj_node_id,
                    target=sess_node_id,
                    relation="hasSession",
                    properties={
                        "subject_id": subject,
                        "session_id": sess,
                        "relationship": "hasSession"
                    }
                    )) # Subject -hasSession-> Session
            # Raw file nodes
            for raw_file_no_extension in self.get_files_no_extension(scope="raw", subject_id=subject):
                raw_file_node_id: str = self.get_raw_file_node_id(raw_file_no_extension)
                self.graph.add_node(
                    KGNode(id=raw_file_node_id, label="RawFile", layer="data", properties={"stem": raw_file_no_extension, "session_id": sess, "subject_id": subject, "dataset_id": dataset_node_id})
                )
                self.graph.add_edge(KGEdge(
                    source=dataset_node_id,
                    target=raw_file_node_id,
                    relation="hasRawFile",
                    properties={
                        "dataset_id": dataset_node_id,
                        "stem": raw_file_no_extension,
                        "relationship": "hasRawFile"
                    }
                )) # Dataset -hasRawFile-> RawFile
                self.graph.add_edge(KGEdge(
                    source=raw_file_node_id,
                    target=subj_node_id,
                    relation="hasSubject",
                    properties={
                        "subject_id": subject,
                        "stem": raw_file_no_extension,
                        "relationship": "hasSubject"
                    }
                    )) # RawFile -hasSubject-> Subject
                self.graph.add_edge(KGEdge(
                    source=raw_file_node_id,
                    target=sess_node_id,
                    relation="hasSession",
                    properties={
                        "session_id": sess,
                        "stem": raw_file_no_extension,
                        "relationship": "hasSession"
                    }
                    )) # RawFile -hasSession-> Session
                
                # DICOMHeaders node
                try:
                    dicom_data: dict = self.get_sidecar_data(raw_file_no_extension)
                except Exception as e:
                    print(f"Error processing raw file sidecar {raw_file_no_extension}.json: {e}")
                    continue
                    
                dicomheaders_node_id: str = self.get_dicomheaders_node_id(raw_file_no_extension)
                self.graph.add_node(
                    KGNode(id=dicomheaders_node_id, label="DICOMHeaders", layer="data", properties=dicom_data)
                )
                self.graph.add_edge(KGEdge(
                    source=raw_file_node_id,
                    target=dicomheaders_node_id,
                    relation="hasDICOMHeaders",
                    properties={
                        "stem": raw_file_no_extension,
                        "dataset_id": dataset_node_id,
                        "relationship": "hasDICOMHeaders"
                    }
                )) # RawFile -hasDICOMHeaders-> DICOMHeaders
                
                # Add BIDSEntity nodes from sidecar
                bids_entities: dict = {key: value for key, value in parse_file_entities(raw_file_no_extension).items() if key not in ['subject', 'session']}
                for entity_name, entity_value in bids_entities.items():
                    bids_entity_node_id: str = self.get_bidseentity_node_id(entity_name, entity_value)
                    self.graph.add_node(
                        KGNode(id=bids_entity_node_id, label="BIDSEntity", layer="data", properties={"name": entity_name, "value": entity_value})
                    )
                    self.graph.add_edge(KGEdge(
                        source=raw_file_node_id,
                        target=bids_entity_node_id,
                        relation="hasBIDSEntity",
                        properties={
                            "stem": raw_file_no_extension,
                            "name": entity_name,
                            "value": entity_value,
                            "relationship": "hasBIDSEntity"
                        }
                    )) # RawFile -hasBIDSEntity-> BIDSEntity
                
    def add_derivative_to_graph(self, derivative_name: str):
        if self.graph is None:
            raise ValueError("Knowledge graph has not been built yet.")
        
        try:
            derivative_dataset: Self = [d for d in self.derivatives if d.dataset_description.Name == derivative_name][0]
        except IndexError:
            raise ValueError(f"No derivative dataset found with name: {derivative_name}")
        
        dataset_node_id: str = self.graph.search_nodes(label="Dataset", property_filters={"identifier": f"dataset:{self.bids_root.name}"})[0].id
        pipeline_node_id: str = self.get_pipeline_node_id(derivative_name)
        
        dataset_description: BIDSDatasetDescription = derivative_dataset.dataset_description
        pipeline_id: str = dataset_description.GeneratedBy[0].model_dump().get("ID", "unknown_pipeline_id")
        
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
            properties={
                "dataset_id": dataset_node_id,
                "pipeline_id": pipeline_id,
                "relationship": "hasPipeline"
            }
        )) # Dataset -hasPipeline-> Pipeline
        
        # Get pipeline steps
        for step_idx, pipeline_step in enumerate(dataset_description.PipelineSteps):
            step_name: str = pipeline_step.get("Name", step_idx+1)
            step_node_id: str = self.get_pipeline_step_node_id(derivative_name, step_name)
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
            self.graph.add_edge(KGEdge(
                source=pipeline_node_id,
                target=step_node_id,
                relation="hasStep",
                properties={
                    "pipeline_id": pipeline_id,
                    "step_name": step_name,
                    "relationship": "hasStep"
                }
            )) # Pipeline -hasStep-> PipelineStep
            
            # Get process_ids from this step
            processes: dict[str, list[str]] = {}
            for item in pipeline_step.get("processes", []):
                process_id: str = item.get("process_id", "")
                if process_id not in processes:
                    processes[process_id] = []
                processes[process_id].append(item.get("process_exec_id", ""))
            for process_id, exec_ids in processes.items():
                process_node_id: str = self.get_process_node_id(process_id)
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
                    properties={
                        "step_name": step_name,
                        "process_id": process_id,
                        "relationship": "realizesProcess"
                    }
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
                        properties={
                            "step_name": step_name,
                            "process_id": process_id,
                            "process_exec_id": exec_id,
                            "relationship": "executes"
                        }
                    )) # Process -executes-> ProcessExecution
                
                # Logic node
                process: NeuProcess = NeuProcess.from_process_id(process_id)
                logic: NeuProcessLogic = process.logic
                logic_node_id: str = self.get_logic_node_id(logic.about.name)
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
                    properties={
                        "step_name": step_name,
                        "process_id": process_id,
                        "relationship": "usesLogic",
                    }
                )) # Process -usesLogic-> Logic
                
        # Derivative file nodes
        for deriv_file_stem in self.get_files_no_extension(scope=derivative_name):
            deriv_file_node_id: str = self.get_derivative_file_node_id(derivative_name, deriv_file_stem)
            self.graph.add_node(
                KGNode(id=deriv_file_node_id, label="DerivedFile", layer="data", properties={"stem": deriv_file_stem, "dataset_id": dataset_node_id})
            )
            self.graph.add_edge(KGEdge(
                source=pipeline_node_id,
                target=deriv_file_node_id,
                relation="hasDerivedFile",
                properties={
                    "pipeline_id": pipeline_id,
                    "step_name": step_name,
                    "relationship": "hasDerivedFile",
                    }
            )) # Pipeline -hasDerivedFile-> DerivedFile
            
            # Get BIDSEntity nodes
            bids_entities: dict = {key: value for key, value in parse_file_entities(deriv_file_stem).items()}
            subject_id: str = bids_entities.get("subject")
            session_id: str = bids_entities.get("session")
            subj_node_id: str = self.get_subject_node_id(subject_id)
            sess_node_id: str = self.get_session_node_id(session_id)
            if subject_id is not None:
                self.graph.add_edge(KGEdge(
                    source=deriv_file_node_id,
                    target=subj_node_id,
                    relation="hasSubject",
                    properties={
                        "subject_id": subject_id,
                        "stem": deriv_file_stem,
                        "relationship": "hasSubject"
                    }
                )) # DerivedFile -hasSubject-> Subject
            if session_id is not None:
                self.graph.add_edge(KGEdge(
                    source=deriv_file_node_id,
                    target=sess_node_id,
                    relation="hasSession",
                    properties={
                    "session_id": session_id,
                    "stem": deriv_file_stem,
                    "relationship": "hasSession"
                }
            )) # DerivedFile -hasSession-> Session
            
            try:
                sidecar_data: dict = self.get_sidecar_data(deriv_file_stem)
            except Exception as e:
                # print(f"Error loading derivative file sidecar {deriv_file_stem}.json: {e}")
                continue
                
            process_exec_id: str = sidecar_data.get("ProcessExecID")
            process_exec_node_id: str = self.get_process_execution_node_id(process_id, process_exec_id)
            self.graph.add_node(KGNode(
                id=process_exec_node_id,
                label="ProcessExecution",
                layer="provenance",
                properties={
                    "process_exec_id": process_exec_id,
                }
            ))
            self.graph.add_edge(KGEdge(
                source=process_exec_node_id,
                target=deriv_file_node_id,
                relation="generates",
                properties={
                    "process_exec_id": process_exec_id,
                    "stem": deriv_file_stem,
                    "relationship": "generates"
                }
                )) # ProcessExecution -generates-> DerivedFile
            
            for entity_name, entity_value in bids_entities.items():
                if entity_name in ["subject", "session"]:
                    continue
                bids_entity_node_id: str = self.get_bidseentity_node_id(entity_name, entity_value)
                self.graph.add_node(
                    KGNode(id=bids_entity_node_id, label="BIDSEntity", layer="data", properties={"name": entity_name, "value": entity_value})
                )
                self.graph.add_edge(KGEdge(
                    source=deriv_file_node_id,
                    target=bids_entity_node_id,
                    relation="hasBIDSEntity",
                    properties={
                        "name": entity_name,
                        "value": entity_value,
                        "relationship": "hasBIDSEntity"
                    }
                    )) # DerivedFile -hasBIDSEntity-> BIDSEntity
                
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
                    input_file_node_id: str = self.get_derivative_file_node_id(input_derivative_name, input_file_no_extension)
                    label = "DerivedFile"
                else:
                    input_file_node_id: str = self.get_raw_file_node_id(input_file_no_extension)
                if not input_file_node_id in self.graph.nodes:
                    print(f"Input file node {input_file_node_id} not found in graph for derived file {deriv_file_node_id}. Creating.")
                    self.graph.add_node(
                        KGNode(id=input_file_node_id, label=label, layer="data", properties={"stem": input_file_no_extension, "dataset_id": dataset_node_id})
                    )
                self.graph.add_edge(KGEdge(
                    source=deriv_file_node_id,
                    target=input_file_node_id,
                    relation="derivedFrom",
                    properties={
                        "stem": deriv_file_stem,
                        "input_stem": input_file_no_extension,
                        "relationship": "derivedFrom"
                    }
                )) # DerivedFile -derivedFrom-> RawFile/DerivedFile
                self.graph.add_edge(KGEdge(
                    source=input_file_node_id,
                    target=process_exec_node_id,
                    relation="usedBy",
                    properties={
                        "stem": deriv_file_stem,
                        "input_stem": input_file_no_extension,
                        "relationship": "usedBy"
                    }
                )) # RawFile/DerivedFile -usedBy-> ProcessExecution
                
            # Get Metric nodes from sidecar
            metrics_dict: dict = sidecar_data.get("metrics", {})
            metrics: list[Metric] = [result[1] for result in find_and_transform_instances(metrics_dict, Metric)]
            for metric in metrics:
                metric_node_id: str = f"metric:{metric.name}:{metric.value}:{metric.description}:{metric.category}:{metric.labels}"
                self.graph.add_node(
                    KGNode(id=metric_node_id, label="Metric", layer="data", properties=metric.model_dump())
                )
                self.graph.add_edge(KGEdge(
                    source=deriv_file_node_id,
                    target=metric_node_id,
                    relation="hasMetric",
                    properties={
                        "stem": deriv_file_stem,
                        "metric_name": metric.name,
                        "relationship": "hasMetric"
                    }
                )) # DerivedFile -hasMetric-> Metric