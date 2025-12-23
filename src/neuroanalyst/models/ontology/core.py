from typing import Literal
import os

from owlready2 import (
    get_ontology,
    Thing,
    DataProperty,
    ObjectProperty,
    AnnotationProperty,
    Restriction,
    onto_path,
    Ontology
    )


AXONOME_ONTOLOGY_URI: str = "http://axonome.org/ontology/axonome.owl"
AXONOME_ONTOLOGY_PATH: str = "docs/axonome_ontology.owl"

# Create or load the ontology
if os.path.exists(AXONOME_ONTOLOGY_PATH):
    axonome_ontology: Ontology = get_ontology(AXONOME_ONTOLOGY_PATH).load()
else:
    axonome_ontology = get_ontology(AXONOME_ONTOLOGY_URI)

provo_ontology: Ontology = get_ontology("docs/provo_owlapi.owl").load()
prov_entity_cls = provo_ontology.search_one(iri="http://www.w3.org/ns/prov#Entity")
prov_plan_cls = provo_ontology.search_one(iri="http://www.w3.org/ns/prov#Plan")
prov_activity_cls = provo_ontology.search_one(iri="http://www.w3.org/ns/prov#Activity")

with axonome_ontology:
    """
    Annotation properties
    """
    class versionInfo(AnnotationProperty):
        pass
    
    class createdBy(AnnotationProperty):
        pass

    class createdOn(AnnotationProperty):
        pass

    class description(AnnotationProperty):
        pass

    """
    Data Layer
    """
    class DataThing(Thing):
        """Base class for data entities"""
        entity_type: Literal["Data", "Provenance"]  # To distinguish data vs provenance
        pass
    
    class Dataset(DataThing):
        """Represents a BIDS Dataset"""
        entity_type: Literal["Data"] = "Data"
        pass
    
    # Files are provenance entities

    class RawFile(prov_entity_cls, DataThing):
        """Represents a raw BIDS file"""
        entity_type: Literal["Provenance"] = "Provenance"
        pass
    
    class DerivedFile(prov_entity_cls, DataThing):
        """Represents a derived BIDS file"""
        entity_type: Literal["Provenance"] = "Provenance"
        pass
    
    class BIDSEntity(DataThing):
        """Represents a BIDS entity (e.g., modality, acquisition)"""
        entity_type: Literal["Data"] = "Data"
        pass
    
    class Subject(DataThing):
        """Represents a subject in the dataset"""
        entity_type: Literal["Data"] = "Data"
        pass

    class Session(DataThing):
        """Represents a session in the dataset"""
        entity_type: Literal["Data"] = "Data"
        pass

    class Metric(DataThing):
        """Represents a quantitative metric derived from data"""
        entity_type: Literal["Data"] = "Data"
        value: DataProperty
        unit: DataProperty
        description: DataProperty
        pass

    class DICOMHeaders(prov_entity_cls):
        """Represents DICOM header metadata"""
        entity_type: Literal["Provenance"] = "Provenance"
        pass
    
    class SubjectCharacteristic(DataThing):
        """Represents characteristic of a subject (e.g., age, sex)"""
        entity_type: Literal["Data"] = "Data"
        pass
    
    class SessionCharacteristic(DataThing):
        """Represents characteristic of a session (e.g., scanner parameters)"""
        entity_type: Literal["Data"] = "Data"
        pass

    """
    Provenance Layer
    """
    class Pipeline(prov_plan_cls):
        """Represents a processing pipeline (plan)"""
        entity_type: Literal["Provenance"] = "Provenance"
        pass
    
    class PipelineStep(prov_activity_cls):
        """Represents a step within a processing pipeline (activity)"""
        entity_type: Literal["Provenance"] = "Provenance"
        pass

    class Process(prov_plan_cls):
        """Represents a process (plan)"""
        entity_type: Literal["Provenance"] = "Provenance"
        pass

    class ProcessExecution(prov_activity_cls):
        """Represents the execution of a processing step"""
        entity_type: Literal["Provenance"] = "Provenance"
        pass
    
    class Logic(prov_entity_cls):
        """Represents the logic/code of a process"""
        entity_type: Literal["Provenance"] = "Provenance"
        pass
    
    class FileProvenance(prov_entity_cls):
        """Represents the provenance of a file"""
        entity_type: Literal["Provenance"] = "Provenance"
        pass
    
    """
    Object Properties (Relationships)
    """
    # Data relationships
    
    class hasRawFile(ObjectProperty):
        """Links a Dataset to its RawFile(s)"""
        domain = [Dataset]
        range = [RawFile]
        rel_type = "data"
    
    class hasDerivedFile(ObjectProperty):
        """Links a Pipeline to its DerivedFile(s)"""
        domain = [Pipeline]
        range = [DerivedFile]
        rel_type = "data"
    
    class hasBIDSEntity(ObjectProperty):
        """Links a RawFile or DerivedFile to its BIDS Entities"""
        domain = [RawFile, DerivedFile]
        range = [BIDSEntity]
        rel_type = "data"
        
    class hasSubject(ObjectProperty):
        """Links a RawFile, DerivedFile, or Dataset to its Subject"""
        domain = [RawFile, DerivedFile, Dataset]
        range = [Subject]
        rel_type = "data"
        
    class hasSession(ObjectProperty):
        """Links a Subject to its Session"""
        domain = [Subject]
        range = [Session]
        rel_type = "data"
    
    class hasSubjectCharacteristic(ObjectProperty):
        """Links a Subject to its Characteristics"""
        domain = [Subject]
        range = [SubjectCharacteristic]
        rel_type = "data"

    class hasSessionCharacteristic(ObjectProperty):
        """Links a Session to its Characteristics"""
        domain = [Session]
        range = [SessionCharacteristic]
        rel_type = "data"

    class derivedFrom(ObjectProperty):
        """Links a DerivedFile to its source File(s). Used for provenance tracking."""
        domain = [DerivedFile]
        range = [RawFile, DerivedFile]
        rel_type = "data"
        
    class hasMetric(ObjectProperty):
        """Links a DerivedFile to its derived Metric(s)"""
        domain = [DerivedFile]
        range = [Metric]
        rel_type = "data"
        
    class hasDICOMHeaders(ObjectProperty):
        """Links a RawFile to its DICOMHeaders"""
        domain = [RawFile]
        range = [DICOMHeaders]
        rel_type = "data"
        
    class hasFileProvenance(ObjectProperty):
        """Links a DerivedFile to its FileProvenance"""
        domain = [DerivedFile]
        range = [FileProvenance]
        rel_type = "data"
    
    # Provenance relationships
    class hasPipeline(ObjectProperty):
        """Links a Dataset to its Pipeline"""
        domain = [Dataset]
        range = [Pipeline]
        rel_type = "provenance"
    
    class hasStep(ObjectProperty):
        """Links a Pipeline to its PipelineStep"""
        domain = [Pipeline]
        range = [PipelineStep]
        rel_type = "provenance"
        
    class hasProcess(ObjectProperty):
        """Links a PipelineStep to its Process"""
        domain = [PipelineStep]
        range = [Process]
        rel_type = "provenance"
        
    class hasLogic(ObjectProperty):
        """Links a Process to its Logic"""
        domain = [Process]
        range = [Logic]
        rel_type = "provenance"

    class generatesExecution(ObjectProperty):
        """Links a Process with its ProcessExecution"""
        domain = [Process]
        range = [ProcessExecution]
        rel_type = "provenance"

    """
    Data Properties (Attributes)
    """
    class identifier(DataProperty):
        """Unique identifier"""
        domain = [DataThing]
        range = [str]
        
    class filepath(DataProperty):
        """File path"""
        domain = [RawFile, DerivedFile]
        range = [str]
        
    class timestamp(DataProperty):
        """Timestamp"""
        domain = [prov_activity_cls, FileProvenance]
        range = [str]
        
    class parameters(DataProperty):
        """Parameters used in core objects"""
        domain = [Pipeline, PipelineStep, ProcessExecution, Process, Logic]
        range = [str]
        
    class value(DataProperty):
        """Value of a metric"""
        domain = [Metric]
        range = [float]
        
    class name(DataProperty):
        """Name of a metric"""
        domain = [Metric]
        range = [str]

    class unit(DataProperty):
        """Unit of a metric"""
        domain = [Metric]
        range = [str]
        
    class description(DataProperty):
        """Description of a metric"""
        domain = [Metric]
        range = [str]

    class createdAt(DataProperty):
        """Creation timestamp"""
        domain = [DataThing, prov_entity_cls]
        range = [str]
        
    class status(DataProperty):
        """Status of a process execution"""
        domain = [ProcessExecution, PipelineStep, Pipeline]
        range = [str]

axonome_ontology.metadata = {
    "title": "Axonome (v1) minimal ontology",
    "version": "1.0.0",
    "description": "Minimal ontology to represent datasets, subjects, files, metrics and provenance (pipelines/process executions).",
}
axonome_ontology.versionInfo = "v1"
axonome_ontology.createdBy = "Chinmay Mokashi"
axonome_ontology.description = "Seed ontology for Axonome knowledge graphs (minimal, extensible)."

if __name__ == "__main__":
    print("Saving Axonome ontology to 'docs/axonome_ontology.owl'...")
    axonome_ontology.save(file="docs/axonome_ontology.owl", format="rdfxml")