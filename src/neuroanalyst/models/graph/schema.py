from typing import Optional, Literal

from pydantic import BaseModel, Field
import numpy as np
from owlready2 import get_ontology, Ontology
from matplotlib import pyplot as plt
import networkx as nx

ONTOLOGY_TIERS = {
    "Dataset": 0,

    "Subject": 1,
    "Pipeline": 1,

    "Session": 2,
    "PipelineStep": 2,
    "Process": 2,

    "RawFile": 3,
    "DerivedFile": 3,
    "ProcessExecution": 3,

    "BIDSEntity": 4,
    "DICOMHeaders": 4,
    "Logic": 4,
    "Metric": 4,
}

CLASS_TO_LAYER: dict[str, str] = {
    "Dataset": "data",

    "Subject": "data",
    "Pipeline": "provenance",

    "Session": "data",
    "PipelineStep": "provenance",
    "Process": "provenance",

    "RawFile": "data",
    "DerivedFile": "data",
    "ProcessExecution": "provenance",

    "BIDSEntity": "data",
    "DICOMHeaders": "data",
    "Logic": "provenance",
    "Metric": "data",
}


core_ontology = get_ontology("docs/ontology.owl").load()

class OntologySchema:
    def __init__(self, ontologies: list[Ontology]):
        self.ontologies = ontologies
        self.classes = {}
        self.data_props = {}
        self.object_props = {}
        
        for ontology in ontologies:
            for cls in ontology.classes():
                self.classes[cls.name] = cls
            for prop in ontology.data_properties():
                self.data_props[prop.name] = prop
            for prop in ontology.object_properties():
                self.object_props[prop.name] = prop
        
    def validate_node(self, label: str, properties: dict):
        if label not in self.classes:
            raise ValueError(f"Unknown class: {label}. Known classes: {list(self.classes.keys())}")

        cls = self.classes[label]
        allowed_props = {
            p.name
            for p in self.data_props.values()
            if cls in p.domain or any(
                parent in p.domain for parent in cls.ancestors()
            )
        }

        # for prop in properties:
        #     if prop not in allowed_props:
        #         raise ValueError(f"{prop} not allowed on {label}. Allowed properties: {allowed_props}")

    def validate_edge(self, rel: str, src_label: str, dst_label: str):
        if rel not in self.object_props:
            raise ValueError(f"Unknown relation: {rel}. Known relations: {list(self.object_props.keys())}")

        prop = self.object_props[rel]

        if not self._is_allowed(src_label, prop.domain):
            raise ValueError(f"{rel} not allowed from {src_label}. Allowed domains: {prop.domain}")

        if not self._is_allowed(dst_label, prop.range):
            raise ValueError(f"{rel} not allowed to {dst_label}. Allowed ranges: {prop.range}")

    def _is_allowed(self, label: str, classes):
        cls = self.classes[label]
        return any(c in cls.ancestors() for c in classes)
    
    def to_nx(self, layer: Optional[str] = None) -> nx.DiGraph:
        SKIP_NODES: set[str] = {"Entity", "File", "ProvenanceEntity", "DataEntity", "MetadataEntity"}
        G = nx.DiGraph()

        for cls_name, cls in self.classes.items():
            node_layer = CLASS_TO_LAYER.get(cls_name, "default")
            if layer is not None and node_layer != layer:
                continue
            if cls_name in SKIP_NODES:
                continue
            G.add_node(cls_name, layer=node_layer)

        for prop_name, prop in self.object_props.items():
            for domain in prop.domain:
                for range_ in prop.range:
                    src_label = domain.name
                    dst_label = range_.name
                    
                    if src_label not in G.nodes or dst_label not in G.nodes:
                        continue
                    
                    # Skip edge if already present (to avoid clutter)
                    if G.has_edge(src_label, dst_label):
                        continue
                    G.add_edge(src_label, dst_label, relation=prop_name)

        return G
    
    def layered_layout(self, G: nx.DiGraph) -> dict[str, tuple[float, float]]:
        """
        Edge-aware layered layout for ontology graphs.
        Nodes are vertically grouped by ontology tier and horizontally
        ordered to minimize edge crossings.
        """
        # --- group nodes by tier ---
        tiers: dict[int, list[str]] = {}
        for node in G.nodes:
            tier = ONTOLOGY_TIERS.get(node, 100)
            tiers.setdefault(tier, []).append(node)

        # Sort tiers top-down
        sorted_tiers = sorted(tiers.keys())

        # Initial x positions (stable)
        x_pos: dict[str, float] = {}
        for tier in sorted_tiers:
            for i, node in enumerate(sorted(tiers[tier])):
                x_pos[node] = float(i)

        # --- barycentric refinement (top-down) ---
        for tier in sorted_tiers[1:]:
            nodes = tiers[tier]

            def barycenter(n: str) -> float:
                parents = list(G.predecessors(n))
                if not parents:
                    return x_pos.get(n, 0.0)
                return sum(x_pos[p] for p in parents) / len(parents)

            nodes.sort(key=barycenter)
            for i, node in enumerate(nodes):
                x_pos[node] = float(i)

        # --- scale & assign final positions ---
        pos: dict[str, tuple[float, float]] = {}
        x_gap = 3.5
        y_gap = 2.5

        for tier in sorted_tiers:
            nodes = tiers[tier]
            width = (len(nodes) - 1) * x_gap
            x_start = -width / 2

            for i, node in enumerate(nodes):
                pos[node] = (
                    x_start + i * x_gap,
                    -tier * y_gap
                )

        return pos

    def draw_ontology(self, layer: Optional[str] = None) -> None:
        G = self.to_nx(layer=layer)

        # --- component-aware layout ---
        components = list(nx.weakly_connected_components(G))
        pos: dict[str, tuple[float, float]] = {}
        x_offset = 0.0
        component_gap = 12.0

        for comp in components:
            subG = G.subgraph(comp)
            sub_pos = self.layered_layout(subG)

            min_x = min(x for x, _ in sub_pos.values())
            max_x = max(x for x, _ in sub_pos.values())
            width = max_x - min_x

            for n, (x, y) in sub_pos.items():
                pos[n] = (x + x_offset, y)

            x_offset += width + component_gap

        fig, ax = plt.subplots(figsize=(14, 9))
        ax.set_aspect("equal")

        # --- tier guide lines ---
        tiers = sorted({ONTOLOGY_TIERS.get(n, 100) for n in G.nodes})
        for tier in tiers:
            y = -tier * 2.5
            ax.axhline(y, color="#EEEEEE", linewidth=1, zorder=0)

        # --- draw nodes by layer ---
        layer_styles = {
            "data": dict(shape="o", color="#4C72B0"),
            "provenance": dict(shape="s", color="#DD8452"),
        }

        for layer_name, style in layer_styles.items():
            nodes = [n for n in G.nodes if G.nodes[n]["layer"] == layer_name]
            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=nodes,
                node_shape=style["shape"],
                node_color=style["color"],
                node_size=1800,
                edgecolors="black",
                linewidths=0.8,
                ax=ax,
            )

        # --- node labels ---
        nx.draw_networkx_labels(
            G,
            pos,
            font_size=10,
            font_weight="bold",
            ax=ax,
        )

        # --- edges (force visible arrows) ---
        # Group edges by (source, target)
        from collections import defaultdict
        edge_groups = defaultdict(list)
        for u, v in G.edges:
            edge_groups[(u, v)].append((u, v))

        # Assign symmetric curvature values
        edge_rad = {}
        for (u, v), edges in edge_groups.items():
            n = len(edges)
            if n == 1:
                edge_rad[(u, v)] = 0.0
            else:
                rads = np.linspace(-0.3, 0.3, n)
                for e, r in zip(edges, rads):
                    edge_rad[e] = r

        for (u, v) in G.edges:
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(u, v)],
                arrows=True,
                arrowstyle="-|>",
                arrowsize=18,
                width=1.3,
                edge_color="#666666",
                connectionstyle=f"arc3,rad={edge_rad.get((u, v), 0.0)}",
                min_source_margin=18,
                min_target_margin=18,
                ax=ax,
            )


        # --- staggered edge labels with halos ---
        edge_labels = nx.get_edge_attributes(G, "relation")
        def offset_label_pos(pos, u, v, offset=0.15):
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2

            dx, dy = x2 - x1, y2 - y1
            length = (dx**2 + dy**2) ** 0.5
            if length == 0:
                return mx, my

            # perpendicular unit vector
            px, py = -dy / length, dx / length
            return mx + px * offset, my + py * offset


        for i, ((u, v), label) in enumerate(edge_labels.items()):
            lx, ly = offset_label_pos(pos, u, v, offset=0.2 + 0.1 * (i % 3))
            ax.text(
                lx,
                ly,
                label,
                fontsize=7,
                ha="center",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    fc="white",
                    ec="none",
                    alpha=0.8,
                ),
                zorder=5,
            )


        title = "Ontology Graph"
        if layer:
            title += f" ({layer.capitalize()} Layer)"
        ax.set_title(title, fontsize=14, pad=20)

        ax.axis("off")
        plt.tight_layout()
        plt.show()

        
SCHEMA: OntologySchema = OntologySchema(
    ontologies=[core_ontology]
)

def get_full_ontology_figure() -> None:
    """
    Get a matplotlib figure representing the full ontology graph.
    
    Returns:
        None: The ontology graph figure is displayed directly.
        
    Example:
        >>> get_full_ontology_figure()
    """
    SCHEMA.draw_ontology()

def get_layered_ontology_figure(layer: Literal["data", "provenance"]) -> None:
    """
    Get a matplotlib figure representing the ontology graph for a specific layer.
    Args:
        layer (Literal["data", "provenance"]): The layer to visualize.
        
    Returns:
        None: The ontology graph figure is displayed directly.
        
    Example:
        >>> get_layered_ontology_figure(layer="data")
    """
    SCHEMA.draw_ontology(layer=layer)