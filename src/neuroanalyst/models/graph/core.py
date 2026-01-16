from .schema import SCHEMA, OntologySchema

from typing import Optional, ClassVar, Literal
from collections import Counter, defaultdict

from pydantic import BaseModel, Field, PrivateAttr
import networkx as nx
from pyvis.network import Network
import pandas as pd

LAYER_COLORS = {
    "data": "#4C78A8",
    "provenance": "#F58518",
    "core": "#9E9E9E",
}

SHAPE_BY_LABEL = {
    "Dataset": "box",
    "Subject": "ellipse",
    "Session": "ellipse",
    "RawFile": "database",
    "DerivedFile": "database",
    "Metric": "diamond",
    "Pipeline": "hexagon",
    "Process": "hexagon",
    "ProcessExecution": "triangle",
}

class KGNode(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    label: str = Field(..., description="Label of the node")
    layer: Literal["data", "provenance"] = Field(..., description="Layer of the knowledge graph the node belongs to")
    properties: dict = Field(description="Optional properties of the node", default_factory=dict)
    
    def __eq__(self, other):
        if not isinstance(other, KGNode):
            return NotImplemented
        return self.id == other.id
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.id, self.label, self.layer))
    
    @property
    def color(self) -> str:
        return LAYER_COLORS.get(self.layer, "#000000")
    
class KGEdge(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relation: str = Field(..., description="Relation type")
    properties: dict = Field(description="Optional properties of the edge", default_factory=dict)
    
    def __eq__(self, other):
        if not isinstance(other, KGEdge):
            return NotImplemented
        return self.source == other.source and self.target == other.target and self.relation == other.relation
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.source, self.target, self.relation))
    
    def __str__(self):
        return f"{self.source} -[{self.relation}]-> {self.target}"

class KGGraph(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    schema: ClassVar[OntologySchema] = SCHEMA
    nodes: dict[str, KGNode] = Field(..., description="Dictionary of nodes in the knowledge graph")
    edges: list[KGEdge] = Field(..., description="List of edges in the knowledge graph")
    _nodes_by_label: dict[str, set[KGNode]] = PrivateAttr(default_factory=lambda: defaultdict(set))
    _nodes_by_layer: dict[str, set[KGNode]] = PrivateAttr(default_factory=lambda: defaultdict(set))
    _edges_by_source: dict[str, set[KGEdge]] = PrivateAttr(default_factory=lambda: defaultdict(set))
    _edges_by_target: dict[str, set[KGEdge]] = PrivateAttr(default_factory=lambda: defaultdict(set))
    
    @property
    def node_count(self) -> int:
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        return len(self.edges)
    
    @property
    def stats(self) -> dict:
        node_counts_by_label: Counter = Counter(
            node.label for node in self.nodes.values()
        )
        edge_counts_by_relation: Counter = Counter(
            edge.relation for edge in self.edges
        )
        return {
            "nodes": {
                "all": len(self.nodes),
                "by_label": dict(node_counts_by_label)
            },
            "edges": {
                "all": len(self.edges),
                "by_relation": dict(edge_counts_by_relation)
            }
        }
        
    @property
    def stats_summary(self) -> str:
        stats = self.stats
        summary_lines = [
            f"Total Nodes: {stats['nodes']['all']}",
            f"Total Edges: {stats['edges']['all']}",
            "Node Counts by Label:",
        ]
        for label, count in stats["nodes"]["by_label"].items():
            summary_lines.append(f"  - {label}: {count}")
        summary_lines.append("Edge Counts by Relation:")
        for relation, count in stats["edges"]["by_relation"].items():
            summary_lines.append(f"  - {relation}: {count}")
        return "\n".join(summary_lines)
    
    @staticmethod
    def props_to_html(props: dict) -> str:
        if not props:
            return "No properties"
        return "<br>".join(f"<b>{k}</b>: {v}" for k, v in props.items())
    
    @staticmethod
    def props_to_markdown(props: dict) -> str:
        if not props:
            return "No properties"
        return "\n".join(f"**{k}**: {v}" for k, v in props.items())
    
    @staticmethod
    def props_to_pretty(props: dict, trim: Optional[int] = 1000) -> str:
        if not props:
            return "No properties"
        props_str = ", ".join(f"{k}: {v}" for k, v in props.items())
        if trim and len(props_str) > trim:
            props_str = props_str[:trim] + "..."
        return props_str
    
    def add_node(self, node: KGNode):
        if node.id in self.nodes:
            return
        self.schema.validate_node(node.label, node.properties)
        self.nodes[node.id] = node
        self._nodes_by_label[node.label].add(node)
        self._nodes_by_layer[node.layer].add(node)
        
    def add_edge(self, edge: KGEdge):
        if edge.source not in self.nodes:
            raise ValueError(f"Source node {edge.source} not found in graph")
        if edge.target not in self.nodes:
            raise ValueError(f"Target node {edge.target} not found in graph")
        if edge in self.edges:
            return
        src: KGNode = self.nodes[edge.source]
        dst: KGNode = self.nodes[edge.target]
        self.schema.validate_edge(edge.relation, src.label, dst.label)
        self.edges.append(edge)
        self._edges_by_source[edge.source].add(edge)
        self._edges_by_target[edge.target].add(edge)
    
    def remove_edge(self, edge: KGEdge):
        """
        Remove an edge from the graph. Removes references from source and target mappings as well.
        
        Args:
            edge (KGEdge): The edge to remove.
        Returns:
            None
        """
        if edge not in self.edges:
            return
        self.edges.remove(edge)
        self._edges_by_source[edge.source].remove(edge)
        self._edges_by_target[edge.target].remove(edge)
    
    def remove_node(self, node_id: str):
        """
        Remove a node from the graph along with all connected edges.
        
        Args:
            node_id (str): The ID of the node to remove.
        Returns:
            None
        """
        if node_id not in self.nodes:
            return
        node: KGNode = self.nodes[node_id]
        layer: str = node.layer
        label: str = node.label
        
        # Remove connected edges
        edges: list[KGEdge] = self.get_node_edges(node_id)
        for edge in edges:
            self.remove_edge(edge)
        
        self._nodes_by_label[label].remove(node)
        self._nodes_by_layer[layer].remove(node)
        del self.nodes[node_id]
        
    def search_nodes(self, label: str, layer: Optional[str] = None, property_filters: Optional[dict] = None) -> list[KGNode]:
        """
        Search for nodes by label and optional property filters.
        
        Args:
            label (str): The label of the nodes to search for.
            layer (Optional[str]): The layer of the nodes to search for. If None, search across all layers.
            property_filters (Optional[dict]): A dictionary of property filters to apply.
        Returns:
            list[KGNode]: List of nodes matching the criteria.
        """
        if layer:
            candidates = [
                node for node in self._nodes_by_layer.get(layer, set())
                if node.label == label
            ]
        else:
            candidates = list(self._nodes_by_label.get(label, set()))
        if property_filters:
            def matches_properties(node: KGNode) -> bool:
                for key, value in property_filters.items():
                    if node.properties.get(key) != value:
                        return False
                return True
            candidates = [
                node for node in candidates
                if matches_properties(node)
            ]
        return candidates
    
    def get_node_edges(self, node_id: str, position: Optional[Literal["source", "target"]] = None) -> set[KGEdge]:
        """
        Retrieve edges connected to a specific node.
        
        Args:
            node_id (str): The ID of the node.
            position (Optional[Literal["source", "target"]]): If "source", return edges where the node is the source.
                If "target", return edges where the node is the target.
                If None, return all edges connected to the node.
        Returns:
            set[KGEdge]: Set of edges connected to the node.
        """
        if node_id not in self.nodes:
            return set()
        if position == "source":
            return self._edges_by_source.get(node_id, set())
        elif position == "target":
            return self._edges_by_target.get(node_id, set())
        else:
            return self._edges_by_source.get(node_id, set()).union(
                self._edges_by_target.get(node_id, set())
            )
        
    def get_nearby_neighbors(
        self,
        node_id: str,
        hops: int = 1,
        direction: Literal["both", "outgoing", "incoming"] = "both",
        node_labels: Optional[set[str]] = None,
        node_layers: Optional[set[str]] = None,
        edge_relations: Optional[set[str]] = None,
        exclude_node_labels: Optional[set[str]] = None,
        ) -> set[KGNode]:
        """
        Retrieve neighboring nodes within a certain number of hops.
        
        Args:
            node_id (str): The ID of the starting node.
            hops (int): Number of hops to search for neighbors.
            direction (Literal["both", "outgoing", "incoming"]): Direction of edges to consider.
            node_labels (Optional[set[str]]): If provided, only include neighbors with these labels.
            node_layers (Optional[set[str]]): If provided, only include neighbors in these layers.
            edge_relations (Optional[set[str]]): If provided, only traverse edges with these relations.
            exclude_node_labels (Optional[set[str]]): If provided, exclude neighbors with these labels.
            
        Returns:
            set[KGNode]: Set of neighboring nodes within the specified hops.
        """
        if node_id not in self.nodes or hops < 1:
            return set()
        visited: set[str] = set()
        current_level: set[str] = {node_id}
        for _ in range(hops):
            next_level: set[str] = set()
            for nid in current_level:
                position: Optional[Literal["source", "target"]] = None
                if direction == "outgoing":
                    position = "source"
                elif direction == "incoming":
                    position = "target"
                for edge in self.get_node_edges(nid, position=position):
                    if edge_relations and edge.relation not in edge_relations:
                        continue
                    neighbor_id = edge.target if edge.source == nid else edge.source
                    if neighbor_id not in visited:
                        next_level.add(neighbor_id)
            visited.update(current_level)
            current_level = next_level
        result_nodes: set[KGNode] = set()
        all_ids = visited.union(current_level)
        all_ids.discard(node_id)
        for nid in all_ids:
            node = self.nodes[nid]
            if node_labels and node.label not in node_labels:
                continue
            if node_layers and node.layer not in node_layers:
                continue
            if exclude_node_labels and node.label in exclude_node_labels:
                continue
            result_nodes.add(node)
        return result_nodes
    
    def traverse_from_to(self, source_id: str, target_id: str, pretty_print: bool = True) -> list[list[KGEdge]]:
        """
        Find the shortest path from source node to target node.
        
        Args:
            source_id (str): The ID of the source node.
            target_id (str): The ID of the target node.
            pretty_print (bool): If True, print the paths in a readable format.
        Returns:
            list[list[KGEdge]]: List of paths, each path is a list of KGEdge objects.
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            return []
        
        g_nx = self.to_networkx().to_undirected()
        shortest_path = nx.shortest_path(G=g_nx, source=source_id, target=target_id)
        paths: list[list[KGEdge]] = []
        
        edges_in_path: list[KGEdge] = []
        for i in range(len(shortest_path) - 1):
            src = shortest_path[i]
            dst = shortest_path[i + 1]
            edge_candidates = [
                edge for edge in self.get_node_edges(src)
                if (edge.source == src and edge.target == dst) or (edge.source == dst and edge.target == src)
            ]
            if edge_candidates:
                edges_in_path.append(edge_candidates[0])
                
        paths.append(edges_in_path)
        if pretty_print:
            for path in paths:
                path_str = " -> ".join(
                    f"{edge.source} -[{edge.relation}]-> {edge.target}"
                    for edge in path
                )
                print(path_str)
        return paths
        
    
    def to_dataframe(self) -> pd.DataFrame:
        data = []
        for edge in self.edges:
            source_node = self.nodes[edge.source]
            target_node = self.nodes[edge.target]
            row = {
                "source_id": edge.source,
                "source_label": source_node.label,
                "source_layer": source_node.layer,
                "target_id": edge.target,
                "target_label": target_node.label,
                "target_layer": target_node.layer,
                "relation": edge.relation,
            }
            data.append(row)
        return pd.DataFrame(data)
    
    def to_networkx(self) -> nx.MultiDiGraph:
        g = nx.MultiDiGraph()
        for node in self.nodes.values():
            g.add_node(node.id, label=node.label, layer=node.layer, **node.properties, color=node.color)
        for edge in self.edges:
            g.add_edge(edge.source, edge.target, key=edge.relation, **edge.properties)
        return g

    def to_pyvis(self, output: Optional[str]="bids_graph.html", heading: Optional[str]="") -> Network:
        g = self.to_networkx()
        net = Network(height="750px", width="100%", directed=True, notebook=True, heading=heading)
        
        # === Add nodes ===
        
        for node_id, data in g.nodes(data=True):
            node_props = {
                k: v for k, v in data.items()
                if k not in {"color"}
            }
            net.add_node(
                node_id,
                label=data.get("label", str(node_id)),
                color=data.get("color", "#000000"),
                shape=SHAPE_BY_LABEL.get(data.get("label", ""), "dot"),
                title=self.props_to_pretty(node_props)
            )
        
        # === Add edges ===
        for source, target, key, data in g.edges(keys=True, data=True):
            net.add_edge(
                source,
                target,
                label=key,
                arrows="to",
                font={"align": "middle"},
                smooth={"type": "cubicBezier"},
                title=self.props_to_pretty(data)
            )
            
        # === Layout tuning ===
        net.force_atlas_2based(
            gravity=-50,
            central_gravity=0.01,
            spring_length=100,
            spring_strength=0.08,
            damping=0.4,
            overlap=0
        )
        
        # === UI Controls ===
        net.show_buttons(filter_=['physics', 'interaction'])
        
        net.show(output)
        
        return net