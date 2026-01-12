from .dataset import BIDSDataset
from ..process.logic.core import Metric
from .core import KGGraph, KGEdge, KGNode

from enum import Enum
from typing import Optional, NamedTuple, Self

from pydantic import BaseModel, Field
from bids.layout import BIDSLayout, parse_file_entities

def normalize_enum_key(s: str) -> str:
    return s.upper().replace("-", "_").replace(" ", "_")

class Slices(NamedTuple):
    scope: type[Enum]
    layer: type[Enum]
    process: type[Enum]
    subject: type[Enum]
    session: type[Enum]
    
    @staticmethod
    def to_enum(name: str, items: set[str]) -> Optional[type[Enum]]:
        if not items:
            return None
        mapping = {normalize_enum_key(item): item for item in items if item}
        return Enum(name, mapping)

class SliceMode(str, Enum):
    UNION = "union"
    INTERSECTION = "intersection"

class SlicedBIDSDataset(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    dataset: BIDSDataset = Field(..., description="BIDSDataset object representing the dataset")
    graph: KGGraph = Field(..., description="KGGraph object representing the self.graph", default_factory=lambda: KGGraph(nodes={}, edges=[]))
        
    def _validate_and_normalize_slices(
        self,
        slices: dict[str, set[str] | list[str] | str]
    ) -> dict[str, set[str]]:
        """
        Validate and normalize the input slices.
        Slices should be a dict mapping slice names to sets/lists/strings of allowed values.
        
        Slices Enum:
        - scope: allowed values are 'raw' and derivative names
        - layer: allowed values are 'data' and 'provenance'
        - process: allowed values are process IDs from pipelines
        - subject: allowed values are subject IDs in the dataset
        - session: allowed values are session IDs in the dataset
        
        Args:
            slices (dict): Input slices to validate and normalize.
        Returns:
            dict: Normalized slices with sets of allowed values.
        """
        # Build enum map from dataset.slices
        slice_attributes = self.generate_slice_attributes()
        enum_map: dict[str, Optional[type[Enum]]] = {
            "scope": slice_attributes.scope,
            "layer": slice_attributes.layer,
            "process": slice_attributes.process,
            "subject": slice_attributes.subject,
            "session": slice_attributes.session
        }

        normalized: dict[str, set[str]] = {}

        for slice_name, values in slices.items():
            # Normalize input to list
            if isinstance(values, (set, list)):
                values = list(values)
            else:
                values = [values]

            if slice_name not in enum_map:
                raise ValueError(f"Unknown slice: {slice_name}")

            enum_cls = enum_map[slice_name]
            if enum_cls is None:
                raise ValueError(f"No enum defined for slice: {slice_name}")

            allowed = {e.value for e in enum_cls}

            invalid = set(values) - allowed
            if invalid:
                raise ValueError(
                    f"Invalid values for slice '{slice_name}': {invalid}. "
                    f"Allowed: {allowed}"
                )

            normalized[slice_name] = set(values)

        return normalized
    
    def generate_slice_attributes(self) -> Slices:
        """
        Analyze the dataset to determine available slice values.
        
        Returns:
            Slices: Slices object with enums for each slice dimension.
        """
        derivative_names: set[str] = {derivative.dataset_description.Name for derivative in self.dataset.derivatives} # Does not allow just 'derivatives' for specificity
        scopes: set[str] = {"raw"}
        scopes.update(derivative_names)
        layers: set[str] = {"data", "provenance"}
        processes: set[str] = set()
        for derivative in self.dataset.derivatives:
            pipeline_steps = derivative.dataset_description.PipelineSteps[0]
            if "processes" not in pipeline_steps:
                continue
            for item in pipeline_steps["processes"]:
                process_id: str = item.get("process_id")
                if process_id is None:
                    continue
                processes.add(process_id)
        if self.dataset.subjects_sessions is None:
            self.dataset.set_subjects_sessions()
        subjects: set[str] = set(self.dataset.subjects_sessions.keys())
        sessions: set[str] = {session for session_list in self.dataset.subjects_sessions.values() for session in session_list}
        
        return Slices(
            scope=Slices.to_enum("Scope", scopes),
            layer=Slices.to_enum("Layer", layers),
            process=Slices.to_enum("Process", processes),
            subject=Slices.to_enum("Subject", subjects),
            session=Slices.to_enum("Session", sessions)
        )
        
    def create_graph(self, slices: dict[str, set[str] | list[str] | str]) -> KGGraph:
        """
        Create a BIDSDatasetself.graph by applying the specified slices to the dataset.
        Algorithm:
            1. Based on scope, subjects, sessions, extract all files from the BIDS dataset.
            2. Remove file extensions and create a set of unique file identifiers.
            3. Search for RawFile and DerivedFile nodes in the KGGraph matching the file identifiers (based on scope).
            4. Find associated nodes and edges to each RawFile/DerivedFile node based on the layer slice and the defined ontology.
                DerivedFile:
                    Nodes: 
                        - Pipeline
                        - PipelineStep
                        - Process
                        - ProcessExecution
                        - Logic
                        - Metric
                RawFile:
                    Nodes:
                        - DICOMHeaders
                Both:
                    Nodes:
                        - Subject
                        - Session
                        - BIDSEntity
            5. Iteratively add nodes and edges to the self.graph following the ontology relationships.
        """
        if self.dataset.graph is None:
            raise ValueError("Graph not built")
        
        normalized_slices = self._validate_and_normalize_slices(slices)
        
        scope = normalized_slices.get("scope", set())
        layer = normalized_slices.get("layer", set())
        process = normalized_slices.get("process", set())
        subject = normalized_slices.get("subject", set())
        session = normalized_slices.get("session", set())
        
        # If any slice is empty, fill it with all possible values
        slice_attributes = self.generate_slice_attributes()
        if not scope:
            scope = {e.value for e in slice_attributes.scope} if slice_attributes.scope else set()
        if not layer:
            layer = {e.value for e in slice_attributes.layer} if slice_attributes.layer else set()
        if not process:
            process = {e.value for e in slice_attributes.process} if slice_attributes.process else set()
        if not subject:
            subject = {e.value for e in slice_attributes.subject} if slice_attributes.subject else set()
        if not session:
            session = {e.value for e in slice_attributes.session} if slice_attributes.session else set()
        
        
        # Add Dataset node
        dataset_node: KGNode = self.dataset.create_dataset_node()
        self.graph.add_node(dataset_node)
        
        # ==== 1. Extract files based on scope, subject, session ====
        if "raw" in scope:
            layout: BIDSLayout = self.dataset.layout
            file_kwargs = {"scope": "raw", "return_type": "file"}
            if subject:
                file_kwargs["subject"] = list(subject)
            if session:
                file_kwargs["session"] = list(session)
            files: list[str] = layout.get(**file_kwargs)
            # files: set[str] = self.dataset.get_files_no_extension(derivative_name="raw", subjects=subject, sessions=session)
            for file_path in files:
                file_path_no_extension: str = self.dataset.remove_file_extension(file_path)
                # Extract BIDS entities
                bids_entities: dict = {key: value for key, value in parse_file_entities(file_path_no_extension).items()}
                if "subject" not in bids_entities:
                    raise ValueError(f"Missing subject entity in file: {file_path_no_extension}")
                subject_id = bids_entities["subject"]
                # Create Subject node
                self.graph.add_node(self.dataset.create_subject_node(subject_id))
                session_id: Optional[str] = None
                if "session" in bids_entities:
                    session_id = bids_entities["session"]
                    # Create Session node
                    self.graph.add_node(self.dataset.create_session_node(session_id))
                # Create RawFile node
                raw_file_node: KGNode = self.dataset.create_raw_file_node(file_path_no_extension, subject_id, session_id)
                raw_file_node_id: str = raw_file_node.id
                self.graph.add_node(raw_file_node)
                # RawFile -hasBIDSEntity-> BIDSEntity (0 or more edges)
                for entity_name, entity_value in bids_entities.items():
                    if entity_name in {"subject", "session"}:
                        continue
                    self.graph.add_node(self.dataset.create_BIDSEntity_node(entity_name, entity_value))
                    self.graph.add_edge(self.dataset.create_rawFile_hasBIDSEntity_edge(file_path_no_extension, entity_name, entity_value))
                # Dataset -hasRawFile-> RawFile (one edge)
                self.graph.add_edge(self.dataset.create_hasRawFile_edge(file_path_no_extension))
                # Relevant edges to RawFile -
                # RawFile -hasSubject-> Subject (one edge)
                self.graph.add_edge(self.dataset.create_rawFile_hasSubject_edge(file_path_no_extension, subject_id))
                # RawFile -hasSession-> Session (0 or 1 edge)
                if session_id is not None:
                    self.graph.add_edge(self.dataset.create_rawFile_hasSession_edge(file_path_no_extension, session_id))
                # RawFile -hasDICOMHeaders-> DICOMHeaders (0 or 1 edge)
                try:
                    dicom_data: dict = self.dataset.get_sidecar_data(file_path_no_extension)
                    self.graph.add_node(self.dataset.create_dicomheaders_node(file_path_no_extension, dicom_data))
                    self.graph.add_edge(self.dataset.create_hasDICOMHeaders_edge(file_path_no_extension))
                except Exception as e:
                    print(f"Failed to add DICOMHeaders for {file_path_no_extension}: {e}")
                # RawFile -usedBy-> ProcessExecution (0 or more edges)
                for hasStep_edge in self.dataset.graph.get_node_edges(raw_file_node_id, position="source"):
                    if hasStep_edge.relation != "usedBy":
                        continue
                    process_execution_node: KGNode = self.dataset.graph.nodes[hasStep_edge.target]
                    process_id: str = process_execution_node.properties.get("process_id")
                    process_exec_id: str = process_execution_node.properties.get("process_exec_id")
                    if process_id is None or process_exec_id is None:
                        print(f"Skipping ProcessExecution node with missing properties: {process_execution_node.id}: {process_execution_node.properties}")
                        continue
                    self.graph.add_node(process_execution_node)
                    self.graph.add_edge(self.dataset.create_usedBy_edge(raw_file_node_id, process_id, process_exec_id))
                # DerivedFile -derivedFrom-> RawFile (0 or more edges)
                for hasStep_edge in self.dataset.graph.get_node_edges(raw_file_node_id, position="target"):
                    if hasStep_edge.relation != "derivedFrom":
                        continue
                    derived_file_node: KGNode = self.dataset.graph.nodes[hasStep_edge.source]
                    derived_file_no_extension: str = derived_file_node.properties.get("stem")
                    derivative_name: str = derived_file_node.properties.get("derivative_name")
                    if derived_file_no_extension is None:
                        print(f"Skipping DerivedFile node with missing stem: {derived_file_node.id}: {derived_file_node.properties}")
                        continue
                    self.graph.add_node(derived_file_node)
                    self.graph.add_edge(self.dataset.create_derivedFrom_edge(derivative_name, derived_file_no_extension, raw_file_node_id))
                    
        for derivative_name in scope - {"raw"}:
            layout: BIDSLayout = [d for d in self.dataset.derivatives if d.dataset_description.Name == derivative_name][0].layout
            file_kwargs = {"scope": derivative_name, "return_type": "file"}
            if subject:
                file_kwargs["subject"] = list(subject)
            if session:
                file_kwargs["session"] = list(session)
            files: list[str] = layout.get(**file_kwargs)
            for file_path in files:
                file_path_no_extension: str = self.dataset.remove_file_extension(file_path)
                # Extract BIDS entities
                bids_entities: dict = {key: value for key, value in parse_file_entities(file_path_no_extension).items()}
                if "subject" not in bids_entities:
                    raise ValueError(f"Missing subject entity in file: {file_path_no_extension}")
                subject_id = bids_entities["subject"]
                # Create Subject node
                self.graph.add_node(self.dataset.create_subject_node(subject_id))
                session_id: Optional[str] = None
                if "session" in bids_entities:
                    session_id = bids_entities["session"]
                    # Create Session node
                    self.graph.add_node(self.dataset.create_session_node(session_id))
                # Create DerivedFile node
                derived_file_node: KGNode = self.dataset.create_derived_file_node(derivative_name, file_path_no_extension)
                self.graph.add_node(derived_file_node)
                # DerivedFile -hasBIDSEntity-> BIDSEntity (0 or more edges)
                for entity_name, entity_value in bids_entities.items():
                    if entity_name in {"subject", "session"}:
                        continue
                    self.graph.add_node(self.dataset.create_BIDSEntity_node(entity_name, entity_value))
                    self.graph.add_edge(self.dataset.create_derivedFile_hasBIDSEntity_edge(derivative_name, file_path_no_extension, entity_name, entity_value))
                # DerivedFile -hasSubject-> Subject (one edge)
                self.graph.add_edge(self.dataset.create_derivedFile_hasSubject_edge(derivative_name, file_path_no_extension, subject_id))
                # DerivedFile -hasSession-> Session (0 or 1 edge)
                if session_id is not None:
                    self.graph.add_edge(self.dataset.create_derivedFile_hasSession_edge(derivative_name, file_path_no_extension, session_id))
                # Create Metric nodes and edges
                for hasMetric_edge in self.dataset.graph.get_node_edges(derived_file_node.id, position="source"):
                    if hasMetric_edge.relation != "hasMetric":
                        continue
                    metric_node: KGNode = self.dataset.graph.nodes[hasMetric_edge.target]
                    self.graph.add_node(metric_node)
                    self.graph.add_edge(self.dataset.create_hasMetric_edge(derived_file_node.id, Metric(**metric_node.properties)))
                # Pipeline -hasDerivedFile-> DerivedFile (one edge)
                try:
                    hasDerivedFile_edge: KGEdge = [edge for edge in self.dataset.graph.get_node_edges(derived_file_node.id, position="target") if edge.relation == "hasDerivedFile"][0]
                except IndexError:
                    print(f"No hasDerivedFile edge found for DerivedFile node: {derived_file_node.id}")
                    continue
                pipeline_node: KGNode = self.dataset.graph.nodes[hasDerivedFile_edge.source]
                pipeline_id: str = pipeline_node.properties.get("pipeline_id")
                if pipeline_id is None:
                    print(f"Skipping Pipeline node with missing pipeline_id: {pipeline_node.id}: {pipeline_node.properties}")
                    continue
                self.graph.add_node(pipeline_node)
                self.graph.add_edge(self.dataset.create_hasDerivedFile_edge(derivative_name, file_path_no_extension))
                # Dataset -hasPipeline-> Pipeline (one edge)
                self.graph.add_edge(self.dataset.create_hasPipeline_edge(derivative_name))
                # Find the relevant ProcessExecution, Process, Logic
                sidecar_data: dict = self.dataset.get_sidecar_data(file_path_no_extension)
                process_exec_id: Optional[str] = sidecar_data.get("ProcessExecID")
                process_id: Optional[str] = sidecar_data.get("ProcessID")
                if any(v is None for v in [process_exec_id, process_id]):
                    print(f"Skipping process nodes for DerivedFile with missing ProcessExecID or ProcessID in sidecar: {file_path_no_extension}")
                    continue
                process_execution_node: KGNode = self.dataset.create_process_execution_node(process_id, process_exec_id)
                self.graph.add_node(process_execution_node)
                process_node: KGNode = self.dataset.create_process_node(process_id)
                self.graph.add_node(process_node)
                # Process -executes-> ProcessExecution (one edge)
                self.graph.add_edge(self.dataset.create_executes_edge(process_id, process_exec_id))
                # Process -usesLogic-> Logic (one edge)
                # Create Logic node
                try:
                    usedLogic_edge: KGEdge = [edge for edge in self.dataset.graph.get_node_edges(process_node.id, position="source") if edge.relation == "usesLogic"][0]
                except IndexError:
                    print(f"No usesLogic edge found for Process node: {process_id}")
                    continue
                logic_node: KGNode = self.dataset.graph.nodes[usedLogic_edge.target]
                self.graph.add_node(logic_node)
                self.graph.add_edge(self.dataset.create_usesLogic_edge(process_id, logic_node.properties.get("name")))
                # Find relevant PipelineStep node
                try:
                    realizesProcess_edge: KGEdge = [edge for edge in self.dataset.graph.get_node_edges(process_node.id, position="target") if edge.relation == "realizesProcess"][0]
                except IndexError:
                    print(f"No realizesProcess edge found for Process node: {process_id}")
                    continue
                pipeline_step_node: KGNode = self.dataset.graph.nodes[realizesProcess_edge.source]
                self.graph.add_node(pipeline_step_node)
                # Pipeline -hasStep-> PipelineStep (one edge)
                self.graph.add_edge(self.dataset.create_hasStep_edge(derivative_name, pipeline_step_node.properties.get("name")))
                # PipelineStep -realizesProcess-> Process (one edge)
                self.graph.add_edge(self.dataset.create_realizesProcess_edge(pipeline_node.properties.get("name"), pipeline_step_node.properties.get("name"), process_id))
                # ProcessExecution -generates-> DerivedFile (one edge)
                self.graph.add_edge(self.dataset.create_generates_edge(derivative_name, process_id, process_exec_id, file_path_no_extension))
                
                # DerivedFile (other) -usedBy-> ProcessExecution (0 or more edges)
                for usedBy_edge in self.dataset.graph.get_node_edges(process_execution_node.id, position="target"):
                    if usedBy_edge.relation != "usedBy":
                        continue
                    other_derived_file_node: KGNode = self.dataset.graph.nodes[usedBy_edge.source]
                    other_derived_file_no_extension: str = other_derived_file_node.properties.get("stem")
                    if other_derived_file_no_extension is None:
                        print(f"Skipping DerivedFile node with missing stem: {other_derived_file_node.id}: {other_derived_file_node.properties}")
                        continue
                    self.graph.add_node(other_derived_file_node)
                    self.graph.add_edge(self.dataset.create_usedBy_edge(other_derived_file_node.id, process_id, process_exec_id))
                    
                # DerivedFile -hasMetric-> Metric (0 or more edges)
                for hasMetric_edge in self.dataset.graph.get_node_edges(derived_file_node.id, position="source"):
                    if hasMetric_edge.relation != "hasMetric":
                        continue
                    metric_node: KGNode = self.dataset.graph.nodes[hasMetric_edge.target]
                    metric: Metric = Metric(**metric_node.properties)
                    self.graph.add_node(metric_node)
                    self.graph.add_edge(self.dataset.create_hasMetric_edge(derived_file_node.id, metric))
                    
                            
        return self.graph
    
    @classmethod
    def from_dataset(cls, dataset: BIDSDataset, slices: dict[str, set[str] | list[str] | str]) -> Self:
        """
        Create a BIDSDatasetSubgraph from a BIDSDataset by analyzing available slices.
        """
        instance = cls(dataset=dataset)
        return instance.create_graph(slices)