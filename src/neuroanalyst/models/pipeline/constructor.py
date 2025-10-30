"""
Constructor module for building NeuPipeline instances.
"""
from ..about import About
from .core import NeuPipeline, NeuPipelineStep, HPCScheduler, ExecutionMode, NeuPipelineStatus
from .executor import ProcessStatus
from ..process.process.core import NeuProcess, STANDARD_BIND_PATHS, STANDARD_ENV_VARS
from ..process.dir.core import NeuProcessDir
from ..process.exec.core import NeuProcessExec, HPCScheduler, ExecutionMode
from ..process.logic.core import NeuProcessLogic, ALLOWED_PYBIDS_ENTITY_KEYS

from pathlib import Path
from typing import Optional
import json

from pydantic import BaseModel, Field, model_validator, field_validator
import networkx as nx
from matplotlib import pyplot as plt
from bids.layout import BIDSLayout

class ProcessConstructorConfig(BaseModel):
    """Configuration for passing a NeuProcess to a NeuPipeline constructor."""
    username: Optional[str] = Field(None, description="Username of the process owner.")
    process_id: str = Field(..., description="Unique identifier for the process.")
    extra_bind_paths: dict[str, str] = Field(default_factory=dict, description="Extra bind paths required by the process.")
    extra_environment_variables: dict[str, str] = Field(default_factory=dict, description="Extra environment variables required by the process.")
    input_bids_filters: dict[str, Optional[str | list[Optional[str | int]]]] = Field(default_factory=dict, description="BIDS filters for input data selection.")
    subject_session_pairs: Optional[list[tuple[Optional[str | list[str]], Optional[str | list[str]]]]] = Field(description="List of (subject, session) pairs for which to create process execs.", default_factory=lambda: [(None, None)])
    execution_mode: ExecutionMode = Field(default=ExecutionMode.CONTAINER, description="Execution mode for the process within the pipeline.")
    
    @property
    def process(self) -> NeuProcess:
        """Get the NeuProcess instance for the given process_id."""
        return NeuProcess.from_process_id(self.process_id, username=self.username)
    
    @property
    def output_entities(self) -> dict[str, str]:
        """Get the output BIDS entities from the process logic."""
        return self.process.logic.output_entities
    
    @property
    def process_execs(self) -> list[NeuProcessExec]:
        """Get the list of NeuProcessExec instances for this configuration."""
        process_execs: list[NeuProcessExec] = []
        for subject_session_pair in self.subject_session_pairs or [(None, None)]:
            subjects: Optional[str | list[str]] = subject_session_pair[0]
            sessions: Optional[str | list[str]] = subject_session_pair[1]
            
            bids_filters: dict[str, str] = {**self.input_bids_filters, **{"subject": subjects, "session": sessions}}
            process_exec: NeuProcessExec = NeuProcessExec.generate_from_process_id(process_id=self.process_id, username=self.username)
            
            # Set BIDS filters
            process_exec.env_var_values["BIDS_FILTERS"] = json.dumps(bids_filters)
            
            # Set execution mode
            process_exec.execution_mode = self.execution_mode
            
            # Add extra bind paths and environment variables. The standard ones are set when the pipeline is constructed.
            for path_name, path_value in self.extra_bind_paths.items():
                process_exec.set_bind_path_value(path_name, path_value)
            
            for var_name, var_value in self.extra_environment_variables.items():
                process_exec.set_env_var_value(var_name, var_value)
            
            process_execs.append(process_exec)
        return process_execs
    
    @classmethod
    def initiate_from_process_id(cls, process_id: str, username: Optional[str] = None, **kwargs) -> "ProcessConstructorConfig":
        """
        Create a ProcessConstructorConfig from a process ID by auto-detecting required extra bind paths and environment variables.
        The generated config will have empty strings for the values of extra bind paths and environment variables, which should be filled in later.
        
        Args:
            process_id (str): The unique identifier of the process.
            username (Optional[str]): The username of the process owner.
            
        Returns:
            ProcessConstructorConfig: The generated process constructor configuration.
        """
        process: NeuProcess = NeuProcess.from_process_id(process_id, username=username)
        extra_bind_paths: dict = {path: "" for path in process.get_non_standard_bind_paths()}
        extra_environment_variables: dict = {var: "" for var in process.get_non_standard_environment_variables()}
        print(f"Generating ProcessConstructorConfig for process_id: {process_id}")
        print(f"  Extra bind paths required: {extra_bind_paths}")
        print(f"  Extra environment variables required: {extra_environment_variables}")

        return cls(
            username=username,
            process_id=process_id,
            extra_bind_paths=extra_bind_paths,
            extra_environment_variables=extra_environment_variables,
            **kwargs
        )
    
    def validate_config(self) -> None:
        """Validate the configuration parameters."""
        process_id: str = self.process_id
        extra_bind_paths: dict = self.extra_bind_paths
        extra_environment_variables: dict = self.extra_environment_variables
        input_bids_filters: dict = self.input_bids_filters
        
        try:
            process: NeuProcess = NeuProcess.from_process_id(process_id, username=self.username)
        except Exception as e:
            raise ValueError(f"Invalid process_id '{process_id}'? : {e}")
        
        required_extra_bind_paths = process.get_non_standard_bind_paths()
        required_extra_env_vars = process.get_non_standard_environment_variables()
        
        if not all(param in extra_bind_paths for param in required_extra_bind_paths):
            missing = [param for param in required_extra_bind_paths if param not in extra_bind_paths]
            raise ValueError(f"Missing required extra bind paths: {missing}")
        
        # Bind path values cannot be empty or None
        if not all(extra_bind_paths[param] for param in required_extra_bind_paths):
            missing = [param for param in required_extra_bind_paths if not extra_bind_paths[param]]
            raise ValueError(f"Empty values for required extra bind paths: {missing}")

        if not all(param in extra_environment_variables for param in required_extra_env_vars):
            missing = [param for param in required_extra_env_vars if param not in extra_environment_variables]
            raise ValueError(f"Missing required extra environment variables: {missing}")
        
        if not all(key in ALLOWED_PYBIDS_ENTITY_KEYS for key in input_bids_filters.keys()):
            invalid_keys = [key for key in input_bids_filters.keys() if key not in ALLOWED_PYBIDS_ENTITY_KEYS]
            raise ValueError(f"Invalid BIDS entity keys in input_bids_filters: {invalid_keys}")
    
class PipelineStepConstructorConfig(BaseModel):
    """Configuration for constructing a NeuPipelineStep."""
    name: str = Field(..., description="Name of the pipeline step.")
    description: str = Field(..., description="Description of the pipeline step.")
    process_configs: list[ProcessConstructorConfig] = Field(..., description="List of process constructor configurations for this step.")
    
    @model_validator(mode="after")
    def validate_step_config(self):
        if not self.process_configs:
            raise ValueError("Pipeline step must have at least one process configuration.")
        if len({config.process_id for config in self.process_configs}) != len(self.process_configs):
            raise ValueError("Duplicate process_ids found in process configurations for the step.")
        return self

    @property
    def processes(self) -> list[NeuProcess]:
        """Get the list of NeuProcess instances for this step."""
        return [config.process for config in self.process_configs]
    
    @property
    def process_execs(self) -> list[NeuProcessExec]:
        """Get the list of NeuProcessExec instances for this step."""
        execs: list[NeuProcessExec] = []
        for config in self.process_configs:
            execs.extend(config.process_execs)  # Default to no subject/session filtering
        return execs
    
    def add_process_config(self, process_config: ProcessConstructorConfig) -> None:
        """Add a ProcessConstructorConfig to the step."""
        self.process_configs.append(process_config)
        
    def remove_process_configs(self, process_ids: str | list[str]) -> None:
        """Remove any ProcessConstructorConfig instances from the step by process_id."""
        if isinstance(process_ids, str):
            process_ids = [process_ids]
        self.process_configs = [config for config in self.process_configs if config.process_id not in process_ids]
        
    def get_process_config(self, process_id: str) -> Optional[ProcessConstructorConfig]:
        """Get a ProcessConstructorConfig by its process_id."""
        for config in self.process_configs:
            if config.process_id == process_id:
                return config
        return None

class PipelineConstructorConfig(BaseModel):
    """Configuration for constructing a NeuPipeline."""
    about: About = Field(..., description="About information for the pipeline.")
    steps: list[PipelineStepConstructorConfig] = Field(..., description="List of pipeline step constructor configurations.")
    scheduler: HPCScheduler = Field(default=HPCScheduler.LOCAL, description="HPC scheduler for the pipeline execution.")
    graph: Optional[nx.DiGraph] = Field(None, description="Directed graph defining step dependencies.")
    pipeline: Optional[NeuPipeline] = Field(None, description="The constructed NeuPipeline instance.")
    
    class Config:
        arbitrary_types_allowed = True
        
    @field_validator('about', mode='before')
    def validate_about(cls, v: dict | About) -> About:
        """Ensure 'about' is an About instance."""
        if isinstance(v, dict):
            return About(**v)
        elif isinstance(v, About):
            return v
        else:
            raise TypeError("about must be an instance of About or a dict")
    
    @staticmethod
    def match_dict_entities(producer_entities: dict[str, str], consumer_entities: dict[str, Optional[str | list[str]]]) -> bool:
        """Check if producer entities satisfy consumer entities."""
        for key, value in consumer_entities.items():
            if key not in producer_entities:
                return False
            producer_value = producer_entities[key]
            if isinstance(value, list):
                if producer_value not in value:
                    return False
            else:
                if producer_value != value:
                    return False
        return True
    
    @classmethod
    def from_pipeline(cls, pipeline: NeuPipeline, construct_graph: bool = True) -> "PipelineConstructorConfig":
        """Create a PipelineConstructorConfig from a NeuPipeline instance."""
        step_configs: list[PipelineStepConstructorConfig] = []
        for step in pipeline.steps:
            process_configs: list[ProcessConstructorConfig] = []
            for process_exec in step.process_execs:
                extra_bind_paths: dict[str, str] = {path: path for path in process_exec.bind_path_values if path not in STANDARD_BIND_PATHS}
                extra_environment_variables: dict[str, str] = {var: var for var in process_exec.env_var_values if var not in STANDARD_ENV_VARS}
                input_bids_filters: dict[str, Optional[str | list[Optional[str | int]]]] = process_exec.bids_filters
                # Remove BIDS entities that are not in ALLOWED_PYBIDS_ENTITY_KEYS
                input_bids_filters = {key: value for key, value in input_bids_filters.items() if key in ALLOWED_PYBIDS_ENTITY_KEYS}
                if process_exec.process.process_id in [process_config.process_id for process_config in process_configs]:
                    continue  # Avoid duplicate process configs for the same process_id within a step
                process_config = ProcessConstructorConfig(
                    username=process_exec.username,
                    process_id=process_exec.process.process_id,
                    extra_bind_paths=extra_bind_paths,
                    extra_environment_variables=extra_environment_variables,
                    input_bids_filters=input_bids_filters
                )
                process_configs.append(process_config)
            step_config = PipelineStepConstructorConfig(
                name=step.name,
                description=step.description,
                process_configs=process_configs
            )
            step_configs.append(step_config)
        pipeline_config = cls(
            about=pipeline.about,
            description=pipeline.about.description,
            steps=step_configs
        )
        if construct_graph:
            pipeline_config.construct_graph()
        return pipeline_config
    
    def get_node_name(self, process_config: ProcessConstructorConfig) -> str:
        """Get the unique node name for a given process configuration."""
        process: NeuProcess = process_config.process
        n_execs: int = len(process_config.subject_session_pairs) if process_config.subject_session_pairs else 1
        return f"{process.logic.about.name} ({process.process_id})"

    def add_step_config(self, step_config: PipelineStepConstructorConfig) -> None:
        """Add a PipelineStepConstructorConfig to the pipeline."""
        self.steps.append(step_config)
        
    def remove_step_config(self, step_name: str) -> None:
        """Remove a PipelineStepConstructorConfig from the pipeline by step name."""
        self.steps = [config for config in self.steps if config.name != step_name]
        
    def add_process_config(self, step_idx: int, process_config: ProcessConstructorConfig) -> None:
        """Add a ProcessConstructorConfig to a specific step by index."""
        if 0 <= step_idx < len(self.steps):
            self.steps[step_idx].add_process_config(process_config)
        else:
            raise IndexError(f"Step index {step_idx} out of range.")
        
    def remove_process_config(self, step_idx: int, process_ids: str | list[str]) -> None:
        """Remove a ProcessConstructorConfig from a specific step by index and process_id."""
        if 0 <= step_idx < len(self.steps):
            self.steps[step_idx].remove_process_configs(process_ids)
        else:
            raise IndexError(f"Step index {step_idx} out of range.")
    
    def add_edge(self, producer_process_config: ProcessConstructorConfig, consumer_process_config: ProcessConstructorConfig, force: bool = False) -> None:
        """
        Add a directed edge from producer to consumer in the graph if valid.
        Validity checks:
            - Producer must be in a step before the consumer.
            - Producer's output entities must satisfy consumer's input entities.
        If `force` is True, the edge is added regardless of entity mismatch, and consumer's input entities are updated.
        
        Args:
            producer_process_config (ProcessConstructorConfig): The producer process configuration.
            consumer_process_config (ProcessConstructorConfig): The consumer process configuration.
            force (bool): Whether to force adding the edge despite entity mismatch.
            
        Raises:
            ValueError: If the edge is invalid and not forced.
        """
        if not self.graph:
            self.construct_graph()
        producer_output_entities = producer_process_config.output_entities
        consumer_input_entities = consumer_process_config.input_bids_filters
        
        if not self.match_dict_entities(producer_output_entities, consumer_input_entities):
            if not force:
                raise ValueError("Producer's output entities do not satisfy consumer's input entities.")
            print("Warning: Forcing addition of edge despite entity mismatch. Updating consumer's input entities.")
            # Update consumer's input entities to match producer's outputs
            consumer_process_config.input_bids_filters = {**producer_output_entities}
            
        self.graph.add_edge(self.get_node_name(producer_process_config), self.get_node_name(consumer_process_config))
    
    def get_config_by_name(self, node_name: str) -> tuple[Optional[ProcessConstructorConfig], int]:
        """Get the ProcessConstructorConfig and step index for a given node name."""
        for step_idx, step_config in enumerate(self.steps):
            for process_config in step_config.process_configs:
                if self.get_node_name(process_config) == node_name:
                    return process_config, step_idx
        return None, -1

    def get_root_nodes(self) -> list[str]:
        """Get the root nodes (no incoming edges) of the graph."""
        if not self.graph:
            self.construct_graph()
        return [node for node in self.graph.nodes if self.graph.in_degree(node) == 0]
    
    def get_leaf_nodes(self) -> list[str]:
        """Get the leaf nodes (no outgoing edges) of the graph."""
        if not self.graph:
            self.construct_graph()
        return [node for node in self.graph.nodes if self.graph.out_degree(node) == 0]
    
    def get_descendants(self, all_roots: bool = False, process_config: Optional[ProcessConstructorConfig] = None) -> list[str]:
        """
        Get all descendant nodes in the graph. If all_roots is True, get descendants of all root nodes.
        If all_roots is False, process_config must be provided to get descendants of that specific node.
        
        Args:
            all_roots (bool): Whether to get descendants of all root nodes.
            process_config (Optional[ProcessConstructorConfig]): Specific process configuration to get descendants for.
        
        Returns:
            list[str]: List of descendant node names.
        """
        if not self.graph:
            self.construct_graph()
        descendants: set[str] = set()
        if all_roots:
            root_nodes = self.get_root_nodes()
            for root in root_nodes:
                descendants.update(nx.descendants(self.graph, root))
        else:
            if process_config is None:
                raise ValueError("process_config must be provided when root_only is False.")
            node_name = self.get_node_name(process_config)
            descendants.update(nx.descendants(self.graph, node_name))
        return list(descendants)
    
    def construct_graph(self) -> nx.DiGraph:
        """
        Construct a directed graph defining step dependencies overwriting any existing graph.
        Key features:
            - Each process config is a node.
            - The producer process config will always be in a step before the consumer process config.
            - Producer-consumer relationships within the same step are not allowed.
            - The output entities of the producer must match the input entities of the consumer.
            
        Returns:
            nx.DiGraph: The constructed directed graph.
        """
        graph = nx.DiGraph()
        
        # Add all process configs as nodes
        for step_idx, step_config in enumerate(self.steps):
            for process_config in step_config.process_configs:
                process_config.validate_config()
                graph.add_node(node_for_adding=self.get_node_name(process_config), step_idx=step_idx)
        
        # Add edges based on producer-consumer relationships
        for i, step_config in enumerate(self.steps):
            for process_config in step_config.process_configs:
                consumer_input_entities: dict[str, Optional[str | list[str]]] = process_config.input_bids_filters
                
                # Check all previous steps for potential producers
                for j in range(i):
                    prev_step_config = self.steps[j]
                    for prev_process_config in prev_step_config.process_configs:
                        producer_output_entities = prev_process_config.process.logic.output_entities
                        
                        # Check if producer's outputs satisfy consumer's inputs
                        if self.match_dict_entities(producer_output_entities, consumer_input_entities):
                            graph.add_edge(self.get_node_name(prev_process_config), self.get_node_name(process_config))
        
        self.graph = graph
        return graph
        
    def visualize(self, show_header_box: bool = True, show_status: bool = True) -> None:
        """
        Visualize the DAG top-down with processes in the same step horizontally aligned.
        
        Args:
            show_header_box (bool): Whether to show a gray rounded rectangle behind the title area.
            show_status (bool): Whether to display the current status of the pipeline processes.
        
        """
        if not self.graph:
            print("Graph not constructed yet. Run `construct_graph()` first.")
            return

        # --- 1. Group nodes by step ---
        step_nodes: dict[int, list[str]] = {}
        for node, data in self.graph.nodes(data=True):
            step_idx = data["step_idx"]
            step_nodes.setdefault(step_idx, []).append(node)

        # --- 2. Compute positions manually ---
        pos: dict[str, tuple[float, float]] = {}
        y_gap = 3.0
        x_gap = 4.0

        for step_idx, nodes in sorted(step_nodes.items()):
            n = len(nodes)
            x_start = -(n - 1) * x_gap / 2
            for i, node in enumerate(nodes):
                x = x_start + i * x_gap
                y = -step_idx * y_gap
                pos[node] = (x, y)

        # --- 3. Setup figure + axes manually ---
        fig, ax = plt.subplots(figsize=(max(10, len(self.graph.nodes)), 6))
        node_colors = [f"C{self.graph.nodes[n]['step_idx'] % 10}" for n in self.graph.nodes]

        # --- Build custom node labels ---
        labels = {}
        for step_idx, step_config in enumerate(self.steps):
            for process_config in step_config.process_configs:
                node_name = self.get_node_name(process_config)
                n_execs = len(process_config.process_execs)
                labels[node_name] = f"{process_config.process_id} - {process_config.process.process_name} x{n_execs}"
        
        nx.draw(
            self.graph,
            pos,
            ax=ax,  # 👈 explicitly draw on this axes
            with_labels=True,
            labels=labels,
            node_color=node_colors,
            node_size=3500,
            font_size=9,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=18,
            connectionstyle="arc3,rad=0.1",
        )

        # --- 4. Annotate step containers ---
        for step_idx, nodes in sorted(step_nodes.items()):
            x_coords = [pos[n][0] for n in nodes]
            y_coords = [pos[n][1] for n in nodes]
            if not x_coords:
                continue
            x_min, x_max = min(x_coords) - 2, max(x_coords) + 2
            y_center = y_coords[0]

            ax.hlines(y_center + 1.3, x_min, x_max, linestyles="dashed", colors="gray", alpha=0.3)
            ax.hlines(y_center - 1.3, x_min, x_max, linestyles="dashed", colors="gray", alpha=0.3)
            ax.vlines(x_min, y_center - 1.3, y_center + 1.3, linestyles="dashed", colors="gray", alpha=0.3)
            ax.vlines(x_max, y_center - 1.3, y_center + 1.3, linestyles="dashed", colors="gray", alpha=0.3)

            ax.text(
                (x_min + x_max) / 2,
                y_center + 1.0,
                f"Step {step_idx + 1}: {self.steps[step_idx].name}",
                fontsize=10,
                ha="center",
                va="bottom",
                fontweight="bold"
            )
            
        # --- Status legend ---
        # --- Display pipeline status ---
        if show_status and self.pipeline:
            status_legend_y = -len(step_nodes) * y_gap - 1.5
            status_legend_x_start = -((len(ProcessStatus) - 1) * 2.5) / 2
            for i, status in enumerate(ProcessStatus):
                ax.scatter(
                    status_legend_x_start + i * 2.5,
                    status_legend_y,
                    s=300,
                    c=status.color,
                    label=status.value,
                    edgecolors="black"
                )
                ax.text(
                    status_legend_x_start + i * 2.5,
                    status_legend_y - 0.4,
                    status.value,
                    fontsize=9,
                    ha="center",
                    va="top"
                )
            ax.text(
                status_legend_x_start + (len(ProcessStatus) - 1) * 2.5 / 2,
                status_legend_y + 0.6,
                "Process Status Legend",
                fontsize=10,
                ha="center",
                va="bottom",
                fontweight="bold"
            )
        
            status: NeuPipelineStatus = self.pipeline.get_pipeline_status()
            # Get completion percentage per node
            # completion_percentages: dict[str, float] = {}
            # for step_config in self.steps:
            #     for process_config in step_config.process_configs:
            #         process_id: str = process_config.process.process_id

        # --- 5. Title and layout adjustment ---
        fig.suptitle(
            f"{self.about.name}\nAuthor: {self.about.author}",
            fontsize=14,
            fontweight="bold",
            y=0.98,
        )
        
        if show_header_box:
            # Add a gray rounded rectangle behind the title area
            from matplotlib.patches import FancyBboxPatch
            ax_header = fig.add_axes([0.0, 0.86, 1.0, 0.12], zorder=-1)
            ax_header.add_patch(
                FancyBboxPatch(
                    (0, 0),
                    1,
                    1,
                    boxstyle="round,pad=0.02",
                    linewidth=0,
                    facecolor="#f2f2f2",
                    transform=ax_header.transAxes,
                    clip_on=False,
                )
            )
            ax_header.axis("off")

        fig.subplots_adjust(top=0.80)  # 👈 now this works as expected
        ax.axis("off")
        plt.show()

        
    def set_descendant_subject_session_pairs(self, root_node: str) -> None:
        """Set subject-session pairs for all descendant process configs based on the root node."""
        if not self.graph:
            self.construct_graph()
        
        root_config, _ = self.get_config_by_name(root_node)
        if root_config is None:
            raise ValueError(f"Root node {root_node} not found in graph.")
        
        subject_session_pairs: list[tuple[Optional[str | list[str]], Optional[str | list[str]]]] = root_config.subject_session_pairs
        
        # Traverse descendants
        descendants = self.get_descendants(process_config=root_config)
        for desc_node in descendants:
            desc_config, _ = self.get_config_by_name(desc_node)
            if desc_config is None:
                print(f"Warning: Could not find config for descendant node {desc_node}. Skipping.")
                continue
            desc_config.subject_session_pairs = subject_session_pairs
    
    def to_pipeline(self, bids_root: str | Path) -> NeuPipeline:
        """Construct a NeuPipeline instance from the configuration."""
        if not self.graph:
            self.construct_graph()
            
        bids_root: Path = Path(bids_root)
        bids_layout: BIDSLayout = BIDSLayout(bids_root, derivatives=True)
        
        # Set subject-session pairs for all root nodes
        for root_node in self.get_root_nodes():
            process_config, _ = self.get_config_by_name(root_node)
            # If subject-session pairs are set, it means that the pipeline should not run on all subjects/sessions.
            if len(process_config.subject_session_pairs) == 0:
                subjects, sessions = process_config.subject_session_pairs[0]
                if isinstance(subjects, str | None):
                    subjects = [subjects]
                if isinstance(sessions, str | None):
                    sessions = [sessions]
                if any(subjects) or any(sessions):
                    continue  # Subject/session filtering is already set
                
            _, subject_session_pairs = NeuProcessExec.spawn_optimized_execs(
                process=process_config.process,
                bids_filters=process_config.input_bids_filters,
                bids_layout=bids_layout
            )
            process_config.subject_session_pairs = subject_session_pairs
            # Set subject-session pairs for all descendants
            self.set_descendant_subject_session_pairs(root_node)
        
        
        steps: list[NeuPipelineStep] = []
        for step_config in self.steps:
            process_execs: list[NeuProcessExec] = []
            for process_config in step_config.process_configs:
                process_execs.extend(process_config.process_execs)
            step = NeuPipelineStep(
                name=step_config.name,
                description=step_config.description,
                process_execs=process_execs
            )
            steps.append(step)
            
        pipeline: NeuPipeline = NeuPipeline(
            bids_root=bids_root,
            about=self.about,
            steps=steps,
            scheduler=self.scheduler,
        )
        pipeline.apply_standard_exec_params()
        
        # Re-construct the graph in the pipeline
        self.construct_graph()
        
        return pipeline