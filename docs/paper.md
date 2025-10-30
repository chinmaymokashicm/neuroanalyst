## The Logic–Process–Exec Framework
The Logic–Process–Exec framework provides a structured abstraction for defining, packaging, and executing computational analyses on neuroimaging data. Its design emphasizes clarity, modularity, and reusability, ensuring that analyses remain reproducible and adaptable across computing environments.

### Logic: Defining Computation
A Logic represents the pure computational function — the algorithmic core that defines what is to be computed. It operates only on data objects and remains agnostic to its execution environment. The logic takes BIDS-compliant inputs, performs a computation, and returns three essential outputs:

1. **Output data** — the structured results of the computation, not written to disk but retained in memory.
2. **BIDS entities** — key–value pairs describing where and how the resulting data should be organized within a BIDS dataset.
3. **Metrics** — a dictionary of derived values summarizing the computation (e.g., quantitative measures, model fit parameters).

The logic does not perform file I/O. Its outputs instead serve as blueprints for generating BIDS-compliant derivatives downstream. This strict separation between computation and data management ensures that each logic can be reused independently of infrastructure, data source, or storage configuration.

### Process: Declaring Runtime Requirements
A Process defines what the logic needs to run. It establishes the boundary between the pure computation and its environment. Each process declares:

- Required environment variables and their expected types,
- Expected mount points or accessible paths within the execution environment, and
- External dependencies such as container images or Python environments.

This declaration stage does not assign any runtime values; it simply defines the schema of requirements. Processes thus serve as reusable, portable templates that can later be bound to real configurations during execution.

Each process can be associated with a reproducible computational environment — such as a Singularity image or a Python virtual environment — providing consistency across different platforms.

### Exec: Instantiating Execution
An Exec represents a concrete instantiation of a process with specific runtime values. It binds all declared variables, parameters, and mounts to real data and configuration contexts, preparing the process for execution. Each exec corresponds to a single, traceable run that can be versioned, audited, and reproduced.

During execution, the system performs two additional operations:

1. Construct BIDS-compliant output files — transforming the in-memory output data into standardized BIDS file structures.

2. Generate detailed JSON sidecar files — capturing complete provenance, including runtime parameters, environmental context, input–output mappings, and computed metrics.

These sidecar files make each computation self-describing and fully interoperable, facilitating reproducibility and downstream aggregation of results across datasets and analyses.

### Pipelines: Chaining Executions
Multiple execs can be organized into a Pipeline, which defines their execution order and data flow. Pipelines use the BIDS entities produced by one exec to automatically locate compatible inputs for the next.

Because all inputs and outputs are BIDS-compliant, pipelines can perform entity-based querying, resolving dependencies dynamically through key–value pair matching.

This design allows pipelines to be constructed compositionally — steps can be reused, reordered, or replaced without altering their underlying logic or process definitions.

### Execution Environments and Schedulers
The execution layer of the framework is intentionally decoupled from both process and logic definitions. Execs can be dispatched through a variety of compute backends, including high-performance computing (HPC) schedulers such as LSF, SLURM, and PBS.
These schedulers manage job distribution, queuing, and resource allocation without modifying the semantics of the process or the logic. As a result, the same process definition can be executed:

- Locally, within a development environment,
- On a high-performance cluster via job submission, or
- Within a cloud-based orchestration service.

Because the abstraction layers remain unchanged across environments, reproducibility and traceability are preserved. The scheduler interface simply handles when and where an exec runs, while the framework governs what runs and how it is structured.

#### Summary
Together, the Logic–Process–Exec hierarchy establishes a clear separation of responsibilities:
- Logic — defines what to compute
- Process — declares what is required to compute it
- Exec — instantiates how and when it is executed
- Pipeline — orchestrates how computations are chained into workflows
- Scheduler — governs where and when executions occur

This architecture ensures that computational logic remains reusable, execution environments remain reproducible, and pipeline orchestration remains portable across scales — from local testing to large-scale, distributed HPC environments.

### Data Provenance and Reproducibility Tracking
Every execution within the framework produces detailed provenance information stored as BIDS-compliant JSON sidecar files. These sidecars describe the complete computational context of each run, including:

- Input and output BIDS entities,
- The logic and process identifiers,
- Runtime parameters and environment variables,
- System and container metadata (e.g., container hashes, software versions), and
- Derived metrics and quality-control values.

Because provenance is captured automatically and consistently, the framework ensures that every derivative file can be traced back through its full computational lineage—from the raw data inputs to the final outputs of a pipeline. This mechanism enables transparent audit trails, simplifies data sharing under FAIR principles, and allows for complete reproducibility of results across time and computing environments.

## Implementation
While the Logic–Process–Exec model defines the conceptual foundation, its design also enables an efficient and scalable implementation. Several core design patterns have already been realized, and others are straightforward to extend due to the modular and declarative nature of the framework.

### 1. Opinionated Abstraction Constructors and Pipeline Optimization
To ensure simplicity and consistency, the framework uses opinionated constructors for building abstraction layers with minimal required input. For example, in a typical pipeline, only the BIDS entities for the first logic are explicitly defined. From that point onward, each step automatically inherits its input entities from the output entities of the preceding step.

This chaining allows pipelines to be built declaratively — users define computation logic, while the framework infers the flow of data and dependencies.

Furthermore, initial dataset queries are optimized to balance workload and parallelization. The framework filters the dataset using the specified starting entities, partitions the results by subject and session, and distributes these subsets evenly across parallel execs.
Each exec operates independently on a well-scoped data subset, maximizing concurrency and minimizing resource contention. This strategy enables scalable, high-throughput execution even on large neuroimaging datasets such as UK Biobank or TCIA collections.

### 2. Provenance Graphs and Data Lineage Modeling
Because every output file in the system carries its complete provenance, the framework inherently supports the construction of data lineage graphs. In such graphs:

- Nodes represent data entities (inputs, intermediates, or outputs).
- Edges represent transformations defined by logic executions.

For example, a T1-weighted structural analysis pipeline might depend on the outputs of a preprocessing pipeline, which in turn originates from raw acquisition data. By linking their provenance chains, the system can reconstruct the full lineage of any file — enabling queryable dependency graphs across projects and pipelines.

These lineage graphs open the door to several future directions:
- **Graph-based provenance visualization**, allowing users to trace and audit how a particular result was derived.
- **Dependency-aware caching**, where previously computed intermediates can be reused if identical logic and parameters appear again.
- **Knowledge discovery through graph learning**, using machine learning or graph neural networks to identify recurring computational motifs or relationships between derived metrics and upstream processes.
- **Automated hypothesis generation**, where provenance-informed correlations between derived measures guide new analytic designs.

Thus, the provenance structure transforms the dataset from a static collection of files into a dynamic, queryable knowledge graph of computation.

### 3. Aggregated Metric Analysis
Since all execs emit JSON sidecars containing both provenance and derived metrics, the framework naturally supports aggregate statistical analysis without direct access to large image files. These sidecars can be indexed and queried to extract metrics across subjects, sessions, or entire pipelines.

The aggregated metadata tables can then be analyzed using standard statistical or machine learning methods, allowing for rapid post hoc analyses, quality control, or cohort-level reporting — all while maintaining full reproducibility and provenance traceability.

This metadata-centric approach significantly reduces I/O overhead and enables efficient downstream data mining across large-scale, multimodal neuroimaging pipelines.

##### Summary
The implementation of the Logic–Process–Exec framework combines minimal user input, automatic provenance tracking, and BIDS-based data interoperability to enable reproducible, scalable, and high-throughput neuroimaging workflows. Its extensible design allows future integration with graph databases, distributed compute schedulers, and intelligent caching or reasoning systems — turning raw computational pipelines into transparent, knowledge-generating ecosystems.

### 4. Implementation

Building on the Logic–Process–Exec framework, the implementation layer translates the conceptual design into a practical, extensible, and automation-ready system for neuroimaging data analysis. Its goal is to operationalize the framework’s principles of clarity, modularity, and reusability while enabling transparent data provenance, efficient execution, and reproducible research at scale.
Figure X schematically illustrates the flow from Logic construction to pipeline execution, highlighting how processes are dynamically composed and instantiated across computation environments.

#### 4.1 Abstraction Constructors and Opinionated Pipeline Composition
The system uses abstraction constructors—predefined, minimal-input templates that enforce a consistent structure across all computation stages. Each constructor automates the creation of Logic, Process, and Exec instances while maintaining user flexibility in defining functions and execution parameters.

Pipeline creation begins when the user specifies the BIDS entities that identify the input data for the first step. From this point forward, the framework automatically infers and propagates BIDS entities across all downstream steps: the output entities generated by one Exec become the input entities of the next. This reduces manual configuration and enforces consistency across the pipeline.

An important optimization occurs through dataset partitioning. When querying the dataset, the framework uses BIDS entity filters to identify relevant data and then splits them into balanced subject–session partitions. Each partition defines an independent computational unit, generating multiple parallel Execs per step. This results in optimized resource utilization, reduced runtime, and scalable performance for large datasets. The user specifies high-level configuration, while the framework automatically handles the details of data subdivision, container initialization, and parameter propagation.

4.2 Provenance, Traceability, and Knowledge Representation
Every execution step within the pipeline generates a rich provenance record that captures both data lineage and computational context. These records encode which inputs, processes, parameters, and environments contributed to each output. The result is a provenance graph—a directed acyclic graph (DAG) whose nodes represent datasets and processes, and whose edges describe derivation relationships.

This provenance graph serves multiple purposes:
- It ensures traceability, allowing any output to be traced back to the original raw data and all intermediate transformations.
- It enables reproducibility, as every execution is fully described by its associated process, environment, and parameter set.
- It supports knowledge representation by converting provenance into a computational knowledge graph, where semantics of the analysis (e.g., “segmentation,” “registration,” “radiomics extraction”) are encoded alongside quantitative results.

Beyond static tracking, this representation enables graph-based discovery and reasoning. Provenance graphs can be mined for frequent computational patterns, analyzed for reproducibility, or used as inputs to graph neural networks (GNNs) or causal learning models to uncover relationships between data characteristics, processing choices, and resulting metrics.
This integration of computation and semantics transforms pipelines into knowledge-generating systems—each execution contributes to an evolving, queryable graph of analytic relationships.

4.3 Aggregated Data Analysis and Derived Metrics

Each Exec produces a set of BIDS-compliant sidecar files alongside its outputs. These JSON files capture detailed metadata, including:
- Provenance information (e.g., input files, process definition, runtime environment),
- Computed metrics generated during execution, and
- Derived entities corresponding to the output dataset structure.

Because this metadata is stored in a standardized, structured format, downstream analyses can operate directly on the sidecars rather than large image files. This enables rapid, scalable meta-analysis across cohorts or pipeline runs without reloading raw imaging data.

For instance, users can extract performance metrics, aggregate them into data tables, and conduct statistical or machine learning analyses to study trends across subjects or sessions. This approach supports aggregated quality control, cross-pipeline comparisons, and population-level analysis, where derived metrics become first-class analytical artifacts. The result is a metadata-centric paradigm that complements data-intensive computation with efficient, interpretable summaries.

4.4 Extensible and Scheduler-Agnostic Execution

A key advantage of the framework is its scheduler-agnostic execution model. Logic and Process definitions remain independent of any computational infrastructure, allowing the same pipeline to execute seamlessly across:

- High-performance computing (HPC) environments using LSF, SLURM, or PBS schedulers,
- Local systems for lightweight development or debugging, and
- Containerized backends such as Docker or Singularity.

At runtime, the Exec layer serves as the interface between the pipeline and the execution environment. It manages job submission, tracks progress, and records provenance without altering the underlying computation logic. This clear separation of concerns ensures portability, scalability, and consistency across diverse hardware and software configurations.

4.5 Potential Extensions and Future Directions

The modular architecture naturally supports future extensions that enhance intelligence, adaptability, and user interactivity:
1. Automated pipeline composition: Provenance graphs can be analyzed to automatically suggest or generate new pipeline configurations based on prior successful patterns or literature-aligned logic chains.
2. Adaptive workflow tuning: Historical performance data can be used to dynamically optimize job scheduling, resource allocation, and parameter initialization for subsequent runs.
3. Interactive provenance visualization: Users can explore lineage graphs to trace data transformations, compare alternative branches, or inspect intermediate results.
4. Integration with RAG-based knowledge retrieval: Provenance graphs and sidecar metadata can be cross-referenced with neuroimaging literature databases to contextualize findings and facilitate hypothesis generation.

4.6 Summary
Together, these implementation strategies extend the Logic–Process–Exec framework into a functional and intelligent system for neuroimaging analysis. The framework’s structured abstraction ensures modularity and clarity, while its implementation promotes automation, provenance, and interpretability.
The resulting system transforms pipelines from simple task sequences into knowledge networks, where computation, data, and reasoning are tightly integrated to accelerate discovery in neuro-oncology research.

### Transition to Evaluation / Results
To evaluate the effectiveness of the proposed framework, we implemented it within the NeuroAnalyst platform and applied it to representative neuroimaging workflows. These included single-modality pipelines, such as T1-weighted morphometric analysis, and multimodal workflows integrating diffusion and perfusion MRI data. The evaluation focused on three dimensions:
1. Reproducibility, assessed through the consistency of derived metrics and provenance tracking across repeated executions;
2. Scalability, measured by performance under distributed HPC scheduling with variable data partitioning strategies; and
3. Knowledge extraction, demonstrated through aggregation of sidecar metadata into interpretable summaries and graph-based lineage exploration.

Together, these experiments illustrate how the Logic–Process–Exec abstraction enables transparent, modular, and knowledge-centric computation that bridges methodological rigor with computational scalability.

### 5. Evaluation
We evaluated the NeuroAnalyst framework across three representative use cases that span structural, diffusion, and functional MRI modalities. Each case demonstrates how NeuroAnalyst builds, executes, and tracks branching directed acyclic graph (DAG) pipelines across heterogeneous processing environments — including both containerized (Docker/Singularity) and virtual environment (venv) executions — while maintaining complete provenance and reproducibility.

#### 5.1 Experimental Setup

All experiments were conducted using de-identified brain MRI data from multi-center repositories, including UK Biobank and PROACTIVE. The datasets were preprocessed into BIDS format prior to analysis.
For all runs, NeuroAnalyst was configured to:

- Execute processes using Docker containers or Python venvs interchangeably.
- Submit jobs via institutional schedulers (LSF, SLURM, or PBS) for scalability.
- Track provenance using an internal MongoDB-backed lineage store, capturing execution metadata, parameter configurations, and derived entities as graph nodes and edges.

Pipeline progress, execution time, and lineage metrics were monitored via the framework’s textual UI and graph-based provenance explorer.

#### 5.2 Case Study 1: Structural MRI Parcellation and Morphometry

**Objective:**
Quantify cortical thickness and volumetric morphometry across 500 subjects using T1-weighted scans.

**Pipeline Design:**
A three-branch DAG was created:

1. Preprocessing (Branch A): Intensity normalization → bias field correction → skull stripping.
2. Segmentation (Branch B): FreeSurfer recon-all + deep learning-based tissue segmentation (DeepLabv3).
3. Atlas Registration (Branch C): Nonlinear registration to Desikan-Killiany and Schaefer-400 atlases.

Each branch produced intermediate artifacts reused across dependent nodes (e.g., registration reused bias-corrected data from Branch A). Execution nodes were distributed across the SLURM cluster with container-based reproducibility.

Results:

- Mean processing time per subject: 38.6 minutes (parallelized over 50 nodes).
- Cross-pipeline reuse reduced redundant computation by 27%.
- Provenance graph traversal confirmed complete lineage for all 1,500 intermediate files.
- Downstream queries (e.g., “Which atlas was used for subject 101233 in version 2.1 of the pipeline?”) were resolved in <40 ms.

*Hypothesis Discovery Example:*
Using NeuroAnalyst’s integrated graph learner, correlations between segmentation-derived cortical thickness and age were automatically flagged, suggesting a non-linear decline pattern within temporal lobe regions, consistent with prior neurodegeneration findings.

#### 5.3 Case Study 2: Diffusion MRI Microstructure and Tractography Integration

**Objective:**
Evaluate multi-model tractography reproducibility using DWI pipelines across two acquisition protocols.

**Pipeline Design:**
A branching workflow with shared pre-processing:

1. Preprocessing: Eddy current correction → motion correction → gradient table harmonization.
2. Branch A: Tensor-based model fitting (DTI).
3. Branch B: Constrained spherical deconvolution (CSD) model for probabilistic tractography.
4. Branch C: Structural–diffusion registration to align T1w and DWI spaces.

NeuroAnalyst’s provenance graph linked each fiber bundle to its model origin, acquisition site, and pre-processing parameters.

Results:

- DTI–CSD overlap coefficient: 0.73 ± 0.04 across major tracts.
- Site-level variability reduced by 14% through harmonization.
- Automated anomaly detection (based on lineage graph embeddings) identified four subjects with parameter deviations.
- Provenance queries confirmed model dependencies and hardware consistency for reproducibility auditing.

**Knowledge Discovery:**
Using the graph learner, NeuroAnalyst identified a pattern where CSD-based fractional anisotropy exhibited higher age sensitivity in posterior tracts, prompting hypotheses about microstructural aging differences not captured by standard tensor models.

#### 5.4 Case Study 3: Resting-State fMRI Connectivity and Cross-Modal Integration

**Objective:**
Construct multimodal connectivity models combining rs-fMRI and DWI features to explore tumor–network interactions in glioma patients.

**Pipeline Design:**
A composite DAG pipeline combining outputs from prior pipelines:

- Functional Branch: Motion correction → ICA-based denoising → parcellation → static and dynamic connectivity matrices.
- Structural Branch: White-matter tractography-derived connectivity matrices.
- Integration Node: Graph fusion (multimodal network embedding) → statistical modeling.

Executions were launched on an HPC cluster (LSF) with functional data processed in venvs (Python/Nipype stack) and diffusion nodes executed in Docker containers. All provenance was unified under a single execution graph.

Results:

- 42 subjects processed across 2 modalities; 1,342 derived nodes tracked.
- Integrated graph embeddings identified consistent network disruption patterns in the default-mode network in midline gliomas.
- Automated hypothesis generator proposed possible coupling between tract disruption and BOLD temporal variance, prompting a follow-up analysis.

System Performance Metrics:

|Metric | Value|
|-------|------|
|Average DAG depth | 12|
|Mean execution time (per subject)	| 58.4 min|
|Container success rate	| 99.2%|
|Venv success rate	| 97.8%|
|Provenance query latency	| <50 ms|
|Graph node count (all runs)	| 12,480|

#### 5.5 Summary

Across all use cases, NeuroAnalyst successfully demonstrated:
- Scalable execution via native scheduler integration.
- Unified provenance and data lineage tracking across heterogeneous compute environments.
- Automated hypothesis generation through graph-based learning on execution metadata.

These experiments validate the framework’s ability not only to orchestrate complex neuroimaging pipelines but also to turn provenance into knowledge — using lineage graphs as a substrate for hypothesis discovery.