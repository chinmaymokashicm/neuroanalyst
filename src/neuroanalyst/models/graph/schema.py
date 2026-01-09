from pydantic import BaseModel, Field
from owlready2 import get_ontology, Ontology

core_ontology = get_ontology("docs/intellibids_core.owl").load()
data_ontology = get_ontology("docs/intellibids_data.owl").load()
prov_ontology = get_ontology("docs/intellibids_prov.owl").load()

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
            raise ValueError(f"Unknown class: {label}")

        cls = self.classes[label]
        allowed_props = {
            p.name
            for p in self.data_props.values()
            if cls in p.domain or any(
                parent in p.domain for parent in cls.ancestors()
            )
        }

        for prop in properties:
            if prop not in allowed_props:
                raise ValueError(f"{prop} not allowed on {label}")

    def validate_edge(self, rel: str, src_label: str, dst_label: str):
        if rel not in self.object_props:
            raise ValueError(f"Unknown relation: {rel}")

        prop = self.object_props[rel]

        if not self._is_allowed(src_label, prop.domain):
            raise ValueError(f"{rel} not allowed from {src_label}")

        if not self._is_allowed(dst_label, prop.range):
            raise ValueError(f"{rel} not allowed to {dst_label}")

    def _is_allowed(self, label: str, classes):
        cls = self.classes[label]
        return any(c in cls.ancestors() for c in classes)
    
SCHEMA: OntologySchema = OntologySchema(
    ontologies=[core_ontology, data_ontology, prov_ontology]
)