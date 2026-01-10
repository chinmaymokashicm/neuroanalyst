from .schema import SCHEMA, OntologySchema

from typing import Optional, ClassVar, Literal

from pydantic import BaseModel, Field
import networkx as nx
from pyvis.network import Network

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

class KGGraph(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    schema: ClassVar[OntologySchema] = SCHEMA
    nodes: dict[str, KGNode] = Field(..., description="Dictionary of nodes in the knowledge graph")
    edges: list[KGEdge] = Field(..., description="List of edges in the knowledge graph")
    
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
    
    def search_nodes(self, label: str, property_filters: Optional[dict] = None) -> list[KGNode]:
        matched_nodes: list[KGNode] = []
        for node in self.nodes.values():
            if node.label != label:
                continue
            if property_filters:
                if all(node.properties.get(k) == v for k, v in property_filters.items()):
                    matched_nodes.append(node)
            else:
                matched_nodes.append(node)
        return matched_nodes
        
    def to_networkx(self) -> nx.MultiDiGraph:
        g = nx.MultiDiGraph()
        for node in self.nodes.values():
            g.add_node(node.id, label=node.label, layer=node.layer, **node.properties, color=node.color)
        for edge in self.edges:
            g.add_edge(edge.source, edge.target, key=edge.relation, **edge.properties)
        return g

    def to_pyvis(self, output: Optional[str]="bids_graph.html") -> Network:
        g = self.to_networkx()
        net = Network(height="750px", width="100%", directed=True, notebook=True)
        
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