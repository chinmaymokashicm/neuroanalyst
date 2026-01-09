from .schema import SCHEMA, OntologySchema

from typing import Optional, ClassVar, Literal

from pydantic import BaseModel, Field

class KGNode(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    label: str = Field(..., description="Label of the node")
    layer: Literal["data", "provenance"] = Field(..., description="Layer of the knowledge graph the node belongs to")
    properties: dict = Field(description="Optional properties of the node", default_factory=dict)
    
    def __eq__(self, other):
        if not isinstance(other, KGNode):
            return NotImplemented
        return self.id == other.id and self.label == other.label and self.layer == other.layer
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.id, self.label, self.layer))
    
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
    
    def add_node(self, node: KGNode):
        if node.id in self.nodes:
            return
        self.schema.validate_node(node.label, node.properties)
        self.nodes[node.id] = node
        
    def add_edge(self, edge: KGEdge):
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("Both source and target nodes must exist in the graph before adding an edge.")
        if edge in self.edges:
            return
        src: KGNode = self.nodes[edge.source]
        dst: KGNode = self.nodes[edge.target]
        self.schema.validate_edge(edge.relation, src.label, dst.label)
        self.edges.append(edge)