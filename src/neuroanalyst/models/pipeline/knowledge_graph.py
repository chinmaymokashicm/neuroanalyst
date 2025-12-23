"""
Module to generate Knowledge Graphs from BIDS datasets and analysis pipelines.

Steps-
    - Load BIDS dataset and extract metadata
    - Create NetworkX graph based on Axonome ontology
    - Refine graph by adding inferred relationships using ontology reasoning
    - Transfer the graph to Neo4j for persistent storage and querying
"""

from ..ontology.core import axonome_ontology
from ..process.logic.core import Metric
from .core import NeuPipeline
from ..process import NeuProcess, NeuProcessExec, NeuProcessLogic

from pathlib import Path
import os
from warnings import warn
import csv
import json
import uuid
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

from rich.progress import track
import pandas as pd
from neo4j import GraphDatabase
from bids.layout import BIDSLayout, BIDSFile, parse_file_entities
from pydantic import BaseModel, Field, DirectoryPath, FilePath, ConfigDict
import networkx as nx
from matplotlib import pyplot as plt

from owlready2 import get_ontology, Ontology

class SubjectCharacteristic(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    subject_id: str = Field(..., description="Subject identifier")
    label: str = Field(..., description="Characteristic label")
    value: any = Field(..., description="Characteristic value")

def is_metric_dict(d: Dict[str, Any]) -> bool:
    """Check if the dict matches a Metric pattern."""
    return (
        isinstance(d, dict)
        and "value" in d
        and "description" in d
        # `unit` may be None or missing
    )

def extract_metrics_from_sidecar(
    data: dict[str, any],
    prefix: str = ""
) -> list[Metric]:
    """
    Recursively extract Metric objects from a nested dictionary.

    Args:
        data: nested dict of metrics
        prefix: hierarchical key name, e.g. "qc_metrics.mask_ratio"

    Returns:
        List of Metric objects.
    """
    metrics: list[Metric] = []

    for key, value in data.items():
        # Construct hierarchical name
        node_name = f"{prefix}.{key}" if prefix else key

        # Case 1: This dict is directly a Metric
        if is_metric_dict(value):
            metrics.append(
                Metric(
                    name=node_name,
                    value=value.get("value"),
                    unit=value.get("unit"),
                    description=value.get("description", "")
                )
            )
            continue

        # Case 2: This is a nested dict => recurse
        if isinstance(value, dict):
            metrics.extend(extract_metrics_from_sidecar(value, prefix=node_name))
            continue

        # Case 3: Value is not a metric, ignore (it's metadata like strings or lists)
        # Example: "brain_dimensions": [256,256,256] would not be treated unless wrapped like below:
        # {"value": [...], "unit": "...", "description": "..."}
        continue

    return metrics

def extract_subject_characteristics(tsv_path: str) -> list[SubjectCharacteristic]:
    """
    Extract subject characteristics from a participants.tsv file.

    Args:
        tsv_path: Path to participants.tsv file.
    Returns:
        List of SubjectCharacteristic objects.
    """
    df_participants: pd.DataFrame = pd.read_csv(tsv_path, sep="\t")
    characteristics: list[SubjectCharacteristic] = []
    for _, row in df_participants.iterrows():
        subject_id = row.get("participant_id")
        # Special handling to remove 'sub-' prefix if present
        if subject_id.startswith("sub-"):
            subject_id = subject_id.replace("sub-", "")
        for col in df_participants.columns:
            if col == "participant_id":
                continue
            characteristics.append(
                SubjectCharacteristic(
                    subject_id=subject_id,
                    label=col,
                    value=row.get(col)
                )
            )
    return characteristics

class OntologySchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    ontology: Ontology = Field(..., description="Owlready2 Ontology object")
    classes: List[Any] = Field(..., description="List of ontology classes")
    obj_props: List[Any] = Field(..., description="List of ontology object properties")
    data_props: List[Any] = Field(..., description="List of ontology data properties")
    
    @classmethod
    def from_ontology(cls, ontology: Ontology) -> "OntologySchema":
        classes = list(ontology.classes())
        obj_props = list(ontology.object_properties())
        data_props = list(ontology.data_properties())
        return cls(
            ontology=ontology,
            classes=classes,
            obj_props=obj_props,
            data_props=data_props
        )

    @property
    def node_labels(self) -> list[str]:
        return [cls.name for cls in self.classes]

    @property
    def relationships(self) -> dict[str, dict[str, list[str]]]:
        rels = {}

        for prop in self.obj_props:
            # raw domain/range
            raw_domain = prop.domain
            raw_range = prop.range

            # expand domain/range to include all subclasses
            expanded_domain = set()
            for c in raw_domain:
                expanded_domain |= {cls.name for cls in self.get_all_subclasses(c)}

            expanded_range = set()
            for c in raw_range:
                expanded_range |= {cls.name for cls in self.get_all_subclasses(c)}
            
            rels[prop.name] = {
                "domain": sorted(expanded_domain),
                "range": sorted(expanded_range),
            }

        return rels

    @property    
    def attributes(self) -> dict[str, dict[str, list[str]]]:
        attrs = {}

        for prop in self.data_props:
            raw_domain = prop.domain
            raw_range = prop.range

            expanded_domain = set()
            for c in raw_domain:
                expanded_domain |= {cls.name for cls in self.get_all_subclasses(c)}

            # ranges are Python types, no need for subclass expansion
            expanded_range = {r.__name__ for r in raw_range}

            attrs[prop.name] = {
                "domain": sorted(expanded_domain),
                "range": sorted(expanded_range),
            }

        return attrs

    @staticmethod
    def get_all_subclasses(cls):
        """Return cls + all its recursive subclasses."""
        subs = set([cls])
        for c in cls.subclasses():
            subs |= OntologySchema.get_all_subclasses(c)
        return subs

    
    def build_templates(self) -> tuple[dict[str, "NodeTemplate"], dict[str, "RelationshipTemplate"]]:
        """
        Build node and relationship templates based on the ontology schema.
        
        Returns:
            Tuple containing dictionaries of node and relationship templates.
        """
        def is_valid_for_domain(cls, domain_classes):
            """Check if a class is valid for a domain (direct or through inheritance)."""
            if cls in domain_classes:
                return True
            # Check if cls is a subclass of any domain class
            for domain_cls in domain_classes:
                try:
                    if issubclass(cls, domain_cls):
                        return True
                except TypeError:
                    # Handle cases where cls might not be a proper class
                    continue
            return False
        
        node_templates = {
            cls.name: NodeTemplate(
                class_name=cls.name,
                attributes={
                    prop.name: prop.range[0].__name__ if prop.range else "str"
                    for prop in self.data_props
                    if is_valid_for_domain(cls, prop.domain)
                }
            )
            for cls in self.classes
        }
        
        # Build relationship templates with inheritance handling
        relationship_templates = {}
        
        for prop in self.obj_props:
            if not prop.domain or not prop.range:
                continue
                
            # For each property, find all valid domain and range classes (including subclasses)
            valid_domain_classes = []
            valid_range_classes = []
            
            # Find all classes that can be in the domain (including subclasses)
            for cls in self.classes:
                if is_valid_for_domain(cls, prop.domain):
                    valid_domain_classes.append(cls)
            
            # Find all classes that can be in the range (including subclasses)  
            for cls in self.classes:
                if is_valid_for_domain(cls, prop.range):
                    valid_range_classes.append(cls)
            
            # Create relationship templates for all valid combinations
            for domain_cls in valid_domain_classes:
                for range_cls in valid_range_classes:
                    template_key = f"{prop.name}__{domain_cls.name}__{range_cls.name}"
                    relationship_templates[template_key] = RelationshipTemplate(
                        name=prop.name,
                        domain=node_templates[domain_cls.name],
                        range=node_templates[range_cls.name]
                    )
        
        return node_templates, relationship_templates
    
    def get_relationships(self, from_cls_name: str, to_cls_name: Optional[str] = None) -> dict[str, dict[str, list[str]]]:
        """Get relationships for a given class name, optionally filtered by target class name."""
        rels = self.relationships
        valid_rels = {}
        for rel_name, rel_info in rels.items():
            if from_cls_name in rel_info["domain"]:
                if to_cls_name is None or to_cls_name in rel_info["range"]:
                    valid_rels[rel_name] = rel_info
        return valid_rels
        
class NodeTemplate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    class_name: str = Field(..., description="Ontology class name for the node")
    attributes: dict[str, any] = Field(default_factory=dict, description="Attributes for the node")
    
    def to_dict(self) -> dict:
        node_dict = {"class": self.class_name}
        node_dict.update(self.attributes)
        return node_dict
    
class RelationshipTemplate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = Field(..., description="Name of the relationship")
    domain: NodeTemplate = Field(..., description="Domain node template")
    range: NodeTemplate = Field(..., description="Range node template")

class KnowledgeGraphBuilder(BaseModel):
    bids_root: DirectoryPath = Field(..., description="Root directory of the BIDS dataset")
    layout: BIDSLayout = Field(..., description="BIDS Layout object for dataset organization")
    ontology_schema: OntologySchema = Field(default_factory=lambda: OntologySchema.from_ontology(axonome_ontology), description="Ontology schema for knowledge graph")
    graph: nx.DiGraph = Field(default_factory=nx.DiGraph, description="NetworkX directed graph representing the knowledge graph")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @property
    def valid_node_labels(self) -> list[str]:
        """Return valid node labels based on the ontology schema."""
        return self.ontology_schema.node_labels
    
    @classmethod
    def from_dataset(cls, bids_root: Union[str, Path]) -> "KnowledgeGraphBuilder":
        """Create a KnowledgeGraphBuilder instance from a BIDS dataset root."""
        layout = BIDSLayout(str(bids_root), validate=False, derivatives=True)
        ontology_schema = OntologySchema.from_ontology(axonome_ontology)
        return cls(
            bids_root=Path(bids_root),
            layout=layout,
            ontology_schema=ontology_schema,
        )
        
    @classmethod
    def from_graph(cls, graph: nx.DiGraph) -> "KnowledgeGraphBuilder":
        """Create a KnowledgeGraphBuilder instance from an existing graph."""
        # Extract BIDS root from the Dataset node
        dataset_node: nx.classes.node = graph.nodes.get("Dataset")
        bids_root: str = dataset_node.get("filepath")
        layout = BIDSLayout(str(bids_root), validate=False, derivatives=True)
        ontology_schema = OntologySchema.from_ontology(axonome_ontology)
        return cls(
            bids_root=Path(bids_root),
            layout=layout,
            ontology_schema=ontology_schema,
            graph=graph
        )

    def generate_subject_node_id(self, subject_id: str) -> str:
        """Generate a unique node identifier for a Subject."""
        return f"subject::{subject_id}"
    
    def generate_session_node_id(self, subject_id: str, session_id: str) -> str:
        """Generate a unique node identifier for a Session."""
        return f"subject::{subject_id}::session::{session_id}"
    
    def generate_dataset_node_id(self) -> str:
        """Generate a unique node identifier for the Dataset."""
        return f"dataset::{self.bids_root.name}"
    
    def generate_file_node_id(self, filepath: str) -> str:
        """Generate a unique node identifier for a File."""
        filename: str = os.path.basename(filepath)
        dirpath: str = os.path.dirname(filepath)
        # Replace BIDS root path with /data to standardize IDs
        dirpath = dirpath.replace(str(self.bids_root), "/data")
        filename_without_ext: str = filename.split('.')[0]
        return os.path.join(dirpath, filename_without_ext)

    def generate_metric_node_id(self, file_id: str, metric: Metric) -> str:
        """Generate a unique node identifier for a Metric."""
        return f"metric::{file_id}::{metric.description if metric.description else 'NoDescription'}::{str(metric.value)}::{metric.unit if metric.unit else 'NoUnit'}"
    
    def generate_bids_entity_node_id(self, entity_name: str, entity_value: str) -> str:
        """Generate a unique node identifier for a BIDSEntity."""
        return f"{entity_name}::{entity_value}"
    
    def generate_dicom_headers_node_id(self, file_id: str) -> str:
        """Generate a unique node identifier for DICOMHeaders."""
        return f"DICOMHeaders::{file_id}"

    def generate_subject_characteristic_node_id(self, subject_characteristic: SubjectCharacteristic) -> str:
        """Generate a unique node identifier for a SubjectCharacteristic."""
        return f"SubjectCharacteristic::{subject_characteristic.label}::{subject_characteristic.value}"

    # def generate_session_characteristic_node_id(self, session_characteristic: SessionCharacteristic) -> str:
    #     """Generate a unique node identifier for a SessionCharacteristic."""
    #     return f"SessionCharacteristic::{session_characteristic.label}::{session_characteristic.value}"

    def get_valid_attributes_for_node(self, node_label: str) -> dict[str, list[str]]:
        """Get valid attributes for a given node label."""
        attrs = self.ontology_schema.attributes
        valid_attrs = {
            attr_name: attr_info
            for attr_name, attr_info in attrs.items()
            if node_label in attr_info["domain"]
        }
        return valid_attrs
    
    def get_sidecar_path(self, file_id: str) -> Optional[str]:
        """Get the sidecar JSON file path for a given BIDS file ID (filepath without the extension)."""
        # Replace /data with actual BIDS root if needed
        sidecar_path = file_id.replace("/data", str(self.bids_root)) + ".json"
        return sidecar_path

    def create_node(self, cls_name: str, identifier: str, **attributes) -> dict:
        """Create a node dictionary for the knowledge graph."""
        attributes = {k: v for k, v in attributes.items() if v is not None}
        if cls_name not in self.valid_node_labels:
            raise ValueError(f"Invalid class name '{cls_name}' for node. Valid labels: {self.valid_node_labels}")
        if 'identifier' not in attributes:
            attributes['identifier'] = identifier
        
        if identifier in self.graph.nodes:
            # warn(f"Node with identifier '{identifier}' already exists. Skipping creation.")
            return self.graph.nodes[identifier]    
        self.graph.add_node(identifier, class_name=cls_name, **attributes)
        return self.graph.nodes[identifier]
    
    def create_subject_node(self, subject_id: str) -> None:
        subject_node_id = self.generate_subject_node_id(subject_id)
        self.create_node(
            cls_name="Subject",
            identifier=subject_node_id,
            name=subject_id
        )
        
    def create_session_node(self, subject_id: str, session_id: str) -> None:
        session_node_id = self.generate_session_node_id(subject_id, session_id)
        self.create_node(
            cls_name="Session",
            identifier=session_node_id,
            name=session_id
        )

    def create_relationship(self, from_id: str, rel_name: str, to_id: str, **attributes) -> None:
        """Create a relationship (edge) in the knowledge graph."""
        from_node = self.graph.nodes.get(from_id)
        to_node = self.graph.nodes.get(to_id)
        if from_node is None or to_node is None:
            raise ValueError(f"One or both nodes not found in graph: from_id={from_id} - {from_node is not None}, to_id={to_id} - {to_node is not None}")
        valid_rels = self.ontology_schema.get_relationships(from_node['class_name'], to_node['class_name'])
        if rel_name not in valid_rels:
            raise ValueError(f"Invalid relationship '{rel_name}' between nodes of classes '{from_node['class_name']}' and '{to_node['class_name']}'. Valid relationships: {list(valid_rels.keys())}")
        attributes = {k: v for k, v in attributes.items() if v is not None}
        
        # Get relationship type from ontology
        rel_type = valid_rels[rel_name].rel_type if 'rel_type' in valid_rels[rel_name] else None
        if rel_type:
            attributes["rel_type"] = rel_type
        
        if self.graph.has_edge(from_id, to_id):
            # warn(f"Edge '{rel_name}' from '{from_id}' to '{to_id}' already exists. Skipping creation.")
            return
        self.graph.add_edge(from_id, to_id, relationship=rel_name, **attributes)
        
    def build_graph_within_scope(self, scope: str) -> list[dict]:
        """
        Build the knowledge graph for a specific pipeline scope.
        Builds relationships between File nodes and their children such as Metrics, DICOMHeaders, BIDSEntity and FileProvenance.
        Builds relationships between File and File nodes themselves only if they are in the same scope.
        
        Returns a list of created File nodes.
        """
        cls_name: str = "DerivedFile" if scope != "raw" else "RawFile"
        files_in_scope: list[str] = []
        for file in self.layout.get(scope=scope, return_type="filename"):
            if file.endswith(('.json', '.bval', '.bvec')):
                continue
            files_in_scope.append(file)
        created_file_nodes: list[dict] = []
        
        for bids_file in files_in_scope:
            file_id = self.generate_file_node_id(bids_file)
            file_node = self.create_node(
                cls_name=cls_name,
                identifier=file_id,
                filepath=bids_file,
                description=f"BIDS file: {bids_file}"
            )
            
            # Create BIDSEntity nodes and link to File
            entities = parse_file_entities(bids_file)
            for entity_name, entity_value in entities.items():
                entity_node_id = self.generate_bids_entity_node_id(entity_name, entity_value)
                if entity_name in ["extension", "session"]:
                    continue  # Skip these entities for now
                if entity_name == "subject":
                    subject_node_id = self.generate_subject_node_id(entity_value)
                    self.create_relationship(
                        from_id=file_id,
                        rel_name="hasSubject",
                        to_id=subject_node_id
                    )
                    
                    if "session" in entities:
                        session_value = entities["session"]
                        session_node_id = self.generate_session_node_id(entity_value, session_value)
                        self.create_relationship(
                            from_id=subject_node_id,
                            rel_name="hasSession",
                            to_id=session_node_id
                        )
                else:    
                    self.create_node(
                        cls_name="BIDSEntity",
                        identifier=entity_node_id,
                        name=entity_name,
                        value=entity_value
                    )
                    self.create_relationship(
                        from_id=file_id,
                        rel_name="hasBIDSEntity",
                        to_id=entity_node_id
                    )
            
            created_file_nodes.append(file_node)
            
            # Get sidecar JSON file
            sidecar_json_path = self.get_sidecar_path(file_id)

            # If RawFile, include DICOMHeaders if available
            if cls_name == "RawFile":
                dicom_header_node_id = self.generate_dicom_headers_node_id(file_id)
                
                sidecar_data = {}
                if os.path.exists(sidecar_json_path):
                    with open(sidecar_json_path, 'r') as f:
                        sidecar_data = json.load(f)
                
                self.create_node(
                    cls_name="DICOMHeaders",
                    identifier=dicom_header_node_id,
                    source_file=file_id,
                    headers=sidecar_data
                )
                self.create_relationship(
                    from_id=file_id,
                    rel_name="hasDICOMHeaders",
                    to_id=dicom_header_node_id
                )
                
            elif cls_name == "DerivedFile":
                # For DerivedFile, include Metrics and Provenance if available in sidecar
                metrics_data = {}
                provenance_data = {}
                if os.path.exists(sidecar_json_path):
                    with open(sidecar_json_path, 'r') as f:
                        sidecar_data = json.load(f)
                    metrics_data = sidecar_data.get("metrics", {})
                    provenance_data = {data for data in sidecar_data if data != "metrics"}
                metrics_list = extract_metrics_from_sidecar(metrics_data)
                
                for metric in metrics_list:
                    metric_node_id = self.generate_metric_node_id(file_id, metric)
                    self.create_node(
                        cls_name="Metric",
                        identifier=metric_node_id,
                        value=metric.value,
                        unit=metric.unit,
                        description=metric.description
                    )
                    self.create_relationship(
                        from_id=file_id,
                        rel_name="hasMetric",
                        to_id=metric_node_id
                    )
                # Create Provenance node
                self.create_node(
                    cls_name="FileProvenance",
                    identifier=f"Provenance::{file_id}",
                    source_file=file_id,
                    details=provenance_data
                )
                self.create_relationship(
                    from_id=file_id,
                    rel_name="hasFileProvenance",
                    to_id=f"Provenance::{file_id}"
                )
            
        return created_file_nodes

    def build_subjects_and_sessions(self, dataset_node_id: str) -> None:
        # Create Subject and Session nodes
        subjects: list[str] = self.layout.get_subjects()
        for subject_id in subjects:
            subject_node_id = self.generate_subject_node_id(subject_id)
            self.create_subject_node(subject_id)
            self.create_relationship(
                from_id=dataset_node_id,
                rel_name="hasSubject",
                to_id=subject_node_id
            )
            
            sessions: list[str] = self.layout.get_sessions(subject=subject_id)
            for session in sessions:
                session_node_id = self.generate_session_node_id(subject_id, session)
                self.create_session_node(subject_id, session)
                self.create_relationship(
                    from_id=subject_node_id,
                    rel_name="hasSession",
                    to_id=session_node_id
                )

        # Extract subject characteristics from participants.tsv if available
        subject_characteristics_path = self.layout.get_file("participants.tsv", scope="raw").path
        if subject_characteristics_path:
            subject_characteristics: list[SubjectCharacteristic] = extract_subject_characteristics(subject_characteristics_path)
            
            for char in subject_characteristics:

                char_node_id = self.generate_subject_characteristic_node_id(char)
                self.create_node(
                    cls_name="SubjectCharacteristic",
                    identifier=char_node_id,
                    subject_id=char.subject_id,
                    label=char.label,
                    value=char.value
                )
                subject_node_id = self.generate_subject_node_id(char.subject_id)
                if subject_node_id not in self.graph.nodes:
                    # warn(f"Subject node '{subject_node_id}' not found for characteristic '{char.label}'. This is likely because the subject has no data files in the dataset. Creating the subject node now.")
                    self.create_subject_node(char.subject_id)

                self.create_relationship(
                    from_id=subject_node_id,
                    rel_name="hasSubjectCharacteristic",
                    to_id=char_node_id
                )
                
                # * Load session characteristics similarly if needed
    
    def build_graph(self, load_previous: bool = False) -> None:
        """Build the knowledge graph from the BIDS dataset and pipeline."""
        
        # Create Dataset node
        dataset_node_id: str = self.bids_root.name
        self.create_node(
            cls_name="Dataset",
            identifier=dataset_node_id,
            filepath=str(self.bids_root),
            description=f"BIDS dataset at {self.bids_root}"
        )
        
        self.build_subjects_and_sessions(dataset_node_id)
        
        # Separate files by scope
        available_scopes: set[str] = {"raw"}
        derivative_pipeline_names: set[str] = set()
        for ds in self.layout.derivatives:
            derivative_pipeline_names.add(ds.replace("derivatives/", ""))
        available_scopes.update(derivative_pipeline_names) # This should include all derivative pipelines present with the raw data
        
        for scope in available_scopes:
            # Identify the pipelines that correspond to this scope - if 'raw', then no pipeline; else the pipeline name is the scope
            if scope != "raw":
                pipeline_id: str = self.layout.get_dataset_description(scope=scope)["GeneratedBy"][0]["ID"]
                username: str = self.layout.get_dataset_description(scope=scope)["GeneratedBy"][0]["UserName"]
                pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id, username)
                self.create_node(
                    cls_name="Pipeline",
                    identifier=pipeline.pipeline_id,
                    name=pipeline.about.name,
                    description=pipeline.about.description,
                )
                self.create_relationship(
                    from_id=dataset_node_id,
                    rel_name="hasPipeline",
                    to_id=pipeline.pipeline_id
                )
                for step in pipeline.steps:
                    self.create_node(
                        cls_name="PipelineStep",
                        identifier=f"{pipeline.pipeline_id}::{step.name}",
                        name=step.name,
                        description=step.description,
                    )
                    self.create_relationship(
                        from_id=pipeline.pipeline_id,
                        rel_name="hasStep",
                        to_id=f"{pipeline.pipeline_id}::{step.name}"
                    )
                    
                    process_execs: list[NeuProcessExec] = step.process_execs
                    unique_processes: list[NeuProcess] = list({pe.process.process_id: pe.process for pe in process_execs}.values())
                    
                    for process in unique_processes:
                        self.create_node(
                            cls_name="Process",
                            identifier=process.process_id,
                            name=process.process_dir.logic.about.name,
                            description=process.process_dir.logic.about.description,
                        )
                        self.create_relationship(
                            from_id=f"{pipeline.pipeline_id}::{step.name}",
                            rel_name="hasProcess",
                            to_id=process.process_id
                        )
                        
                        logic: NeuProcessLogic = process.logic
                        self.create_node(
                            cls_name="Logic",
                            identifier=logic.about.name,
                            code_snippet=logic.code,
                            language=logic.language,
                            description=logic.about.description,
                        )
                        self.create_relationship(
                            from_id=process.process_id,
                            rel_name="hasLogic",
                            to_id=logic.about.name
                        )
                        
                        process_execs_for_process = [pe for pe in process_execs if pe.process.process_id == process.process_id]
                        for pe in process_execs_for_process:
                            self.create_node(
                                cls_name="ProcessExecution",
                                identifier=pe.exec_id,
                            )
                            self.create_relationship(
                                from_id=process.process_id,
                                rel_name="generatesExecution",
                                to_id=pe.exec_id
                            )
            
            file_nodes = self.build_graph_within_scope(scope)
            for file_node in file_nodes:
                self.create_relationship(
                    from_id=dataset_node_id if scope == "raw" else pipeline.pipeline_id,
                    rel_name="hasFile",
                    to_id=file_node['identifier']
                )
                
        # Finally, make conections between files derived from each other across scopes
        for scope in [scope for scope in available_scopes if scope != "raw"]:
            for bids_file in self.layout.get(scope=scope, return_type="filename"):
                file_id = self.generate_file_node_id(bids_file)
                sidecar_info: dict = {}
                sidecar_path = self.get_sidecar_path(file_id)
                if not os.path.exists(sidecar_path):
                    continue
                with open(sidecar_path, 'r') as f:
                    sidecar_info = json.load(f)
                previous_file: str = sidecar_info.get("InputFile")
                if previous_file:
                    previous_file_id = self.generate_file_node_id(previous_file)
                    if previous_file_id not in self.graph.nodes:
                        warn(f"Input file node '{previous_file_id}' not found in graph for derived file '{file_id}'. Skipping relationship creation.")
                        continue
                    self.create_relationship(
                        from_id=file_id,
                        rel_name="derivedFrom",
                        to_id=previous_file_id
                    )

    def get_edges(self, node=None) -> tuple[list, Optional[list]]:
        """Get all edges in the knowledge graph or edges connected to a specific node."""
        if node:
            return list(self.graph.edges(node, data=True)), list(self.graph.in_edges(node, data=True))
        return list(self.graph.edges(data=True)), []
    
    def summarize_graph(self) -> pd.DataFrame:
        """Summarize the knowledge graph as a DataFrame of nodes and their attributes."""
        records = []
        for node_id, data in self.graph.nodes(data=True):
            record = {"node_id": node_id, "class_name": data.get("class_name", "Unknown")}
            record.update({k: v for k, v in data.items() if k != "class_name"})
            records.append(record)
        return pd.DataFrame(records)        
                        
    def visualize_graph(self, figsize=(12, 8)) -> None:
        """Visualize the knowledge graph using Matplotlib."""
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(self.graph)
        node_labels = {node: data['class_name'] for node, data in self.graph.nodes(data=True)}
        edge_labels = {(u, v): data['relationship'] for u, v, data in self.graph.edges(data=True)}
        
        nx.draw(self.graph, pos, with_labels=True, labels=node_labels, node_size=2000, node_color='lightblue', font_size=10)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_color='red')
        plt.title("Knowledge Graph Visualization")
        plt.show()

    def save_graph(self, filepath: Optional[str] = None) -> None:
        """Save the knowledge graph to a GraphML file."""
        if filepath is None:
            filepath = os.path.join(self.bids_root, "knowledge_graph.graphml")
        nx.write_graphml(self.graph, filepath)
        print(f"Knowledge graph saved to {filepath}.")
        
    def save_neo4j_dump(self, dirpath: Optional[str] = None) -> None:
        """Convert the knowledge graph to a CSV dump suitable for Neo4j import."""
        if dirpath is None:
            dirpath = os.path.join(self.bids_root, "neo4j_dump")
        os.makedirs(dirpath, exist_ok=True)

        # Save nodes
        nodes_file = os.path.join(dirpath, "nodes.csv")
        with open(nodes_file, 'w') as f:
            f.write("identifier:ID,class_name:string,*\n")
            for node_id, data in self.graph.nodes(data=True):
                props = [str(data.get(k, "")) for k in data if k != "class_name"]
                f.write(f"{node_id},{data.get('class_name','Unknown')},{','.join(props)}\n")
        print(f"Nodes saved to {nodes_file}.")

        # Save relationships
        rels_file = os.path.join(dirpath, "relationships.csv")
        with open(rels_file, 'w') as f:
            f.write(":START_ID,:END_ID,relationship:string,*\n")
            for u, v, data in self.graph.edges(data=True):
                props = [str(data.get(k, "")) for k in data if k != "relationship"]
                f.write(f"{u},{v},{data.get('relationship','RELATED_TO')},{','.join(props)}\n")
        print(f"Relationships saved to {rels_file}.")
    
    def export_to_neo4j(self, uri: str, user: str, password: str) -> None:
        """
        Export the knowledge graph to Neo4j, ensuring:
        No duplicate nodes (MERGE)
        No duplicate relationships (MERGE)
        Neo4j identifier = NetworkX node_id
        """
        driver = GraphDatabase.driver(uri, auth=(user, password))

        # -----------------------------
        # Support session to target DB
        # -----------------------------
        def get_session():
            return driver.session()

        # -----------------------------
        # Serialize Python → Neo4j JSON-safe
        # -----------------------------
        def serialize(value):
            if value is None:
                return None
            if isinstance(value, (str, int, float, bool)):
                return value
            if isinstance(value, (list, dict)):
                try:
                    return json.dumps(value)
                except Exception:
                    return str(value)
            return str(value)

        # -----------------------------
        # 1. EXPORT NODES
        # -----------------------------
        with get_session() as session:
            for node_id, data in self.graph.nodes(data=True):

                label = data.get("class_name", "Unknown")

                # enforce stable identifier
                props = {"identifier": node_id}

                for k, v in data.items():
                    if k == "class_name":
                        continue
                    ser = serialize(v)
                    if ser is not None:
                        props[k] = ser

                prop_set = ", ".join([f"n.{k} = ${k}" for k in props])

                cypher = f"""
                    MERGE (n:{label} {{identifier: $identifier}})
                    SET {prop_set}
                """

                session.run(cypher, **props)

        # -----------------------------
        # 2. EXPORT RELATIONSHIPS
        # -----------------------------
        with get_session() as session:
            for u, v, data in self.graph.edges(data=True):
                rel_type = data.get("rel_type", data.get("relationship", "RELATED_TO"))

                edge_props = {k: serialize(val)
                            for k, val in data.items()
                            if k not in ["relationship", "rel_type"]}

                params = {"from_id": u, "to_id": v, **edge_props}

                if edge_props:
                    edge_set = ", ".join([f"r.{k} = ${k}" for k in edge_props])
                    cypher = f"""
                        MATCH (a {{identifier: $from_id}})
                        MATCH (b {{identifier: $to_id}})
                        MERGE (a)-[r:{rel_type}]->(b)
                        SET {edge_set}
                    """
                else:
                    cypher = f"""
                        MATCH (a {{identifier: $from_id}})
                        MATCH (b {{identifier: $to_id}})
                        MERGE (a)-[r:{rel_type}]->(b)
                    """

                session.run(cypher, **params)

        driver.close()
