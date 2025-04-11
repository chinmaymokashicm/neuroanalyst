# What is NeuroAnalyst?

NeuroAnalyst is a comprehensive framework designed to standardize and automate neuroimaging data processing and analysis workflows. It addresses the significant challenges researchers face with complex neuroimaging pipelines by providing a structured, containerized environment for executing reproducible analyses. By combining robust processing capabilities with advanced metadata management and AI-powered knowledge discovery, NeuroAnalyst bridges the gap between raw neuroimaging data and meaningful scientific insights.

## Key Features
- Package your niche data analysis into containerized workflows
- Generate structured and enhanced metadata, documentation, and reports
- Enable higher-order large-scale data analysis
- Accelerate knowledge discovery by fusing above-mentioned features with scientific literature using Large Language Models (LLMs)

## Why NeuroAnalyst?

The neuroimaging research community faces several critical challenges that NeuroAnalyst aims to address:

### Reproducibility Crisis
Neuroimaging analyses often suffer from poor reproducibility due to inconsistent computing environments, undocumented processing steps, and variable parameter settings. This leads to wasted research effort and undermines scientific integrity.

### Technical Barriers
Setting up and running neuroimaging pipelines requires substantial computational expertise, creating significant barriers for researchers who want to focus on scientific questions rather than technical implementation.

### Data Integration Challenges
Modern neuroscience requires integration of multiple data types and processing streams, which is challenging without standardized interfaces and metadata schemas.

### Knowledge Discovery Bottlenecks
The vast and rapidly growing neuroimaging literature makes it difficult for researchers to contextualize their findings within the broader scientific landscape.

NeuroAnalyst tackles these challenges through a structured approach to workflow management combined with rich metadata extraction and LLM-enhanced information retrieval capabilities.

## NeuroAnalyst Architecture

```
+-------------------------------+
|        NeuroAnalyst TUI       |
|   +----------+ +----------+   |
|   |  Submit  | |  Results |   |
|   |  Panel   | |   Panel  |   |
|   +----------+ +----------+   |
+-------------------------------+
            |       ^
            V       |
+-------------------------------+
|        Core API Layer         |
| +-------------------------+   |
| |  Process Management     |   |
| +-------------------------+   |
| |  Pipeline Orchestration |   |
| +-------------------------+   |
| |  Execution Engine       |   |
| +-------------------------+   |
+-------------------------------+
            |       ^
            V       |
+-------------------------------+
|    Container Infrastructure   |
|   +----------------------+    |
|   |  Apptainer Images   |    |
|   +----------------------+    |
|   |  HPC Environment    |    |
|   +----------------------+    |
+-------------------------------+
            |       ^
            V       |
+-------------------------------+
|     Insight & Knowledge       |
|        Discovery Layer        |
|   +----------------------+    |
|   |  Metadata Extraction |    |
|   +----------------------+    |
|   |  LLM Integration     |    |
|   +----------------------+    |
+-------------------------------+
```

The architecture consists of four key layers:

1. **User Interface Layer**: A Textual-based Terminal User Interface (TUI) with dual panels for job submission and results visualization[1].

2. **Core API Layer**: Manages processes, process executions, and pipelines, forming the backbone of the workflow management system.

3. **Container Infrastructure**: Leverages Apptainer containers on HPC environments to ensure consistent, reproducible execution environments[2].

4. **Insight & Knowledge Discovery Layer**: Extracts structured metadata from processing results and integrates with LLMs to contextualize findings within scientific literature.

## How NeuroAnalyst Works

NeuroAnalyst follows a modular design philosophy built around three core concepts:

### 1. Processes

A Process is a fundamental unit of computation in NeuroAnalyst. Each Process:
- Has a well-defined input/output specification
- Is packaged as a self-contained Apptainer container
- Contains all necessary dependencies and environment settings
- Includes metadata about its purpose, parameters, and expected outputs

### 2. Process Executions

A Process Execution (ProcessExec) is an instance of a Process with specific parameter values. Each ProcessExec:
- References a specific Process
- Contains concrete parameter values
- Has a unique identifier for tracking and reproducibility
- Records execution metadata (timing, resource usage, etc.)

### 3. Pipelines

A Pipeline is a directed acyclic graph (DAG) of ProcessExecs. Each Pipeline:
- Defines the execution order and dependencies between ProcessExecs
- Manages data flow between Process Executions
- Tracks overall progress and status
- Collects comprehensive metadata across the entire workflow

This hierarchical structure allows for both flexibility and reproducibility:

```
+----------------+
|    Process     |
|  Definition    |
+----------------+
        |
        | instantiate with parameters
        V
+----------------+
|  Process Exec  |
|   Instance     |
+----------------+
        |
        | combine into
        V
+----------------+
|    Pipeline    |
|                |
+----------------+
```

### Pipeline Creation Workflow

```
+-------------------+    +-------------------+    +-------------------+
| 1. Build Process  | -> | 2. Build Process  | -> | 3. Build Pipeline |
|    - Define inputs|    |    Execution      |    |    - Chain        |
|    - Define params|    |    - Set params   |    |      ProcessExecs |
|    - Define outputs    |    - Set inputs   |    |    - Define deps  |
+-------------------+    +-------------------+    +-------------------+
                                                           |
                                                           V
                                               +-------------------+
                                               | 4. Execute        |
                                               |    Pipeline       |
                                               |    - Submit to HPC|
                                               |    - Monitor      |
                                               |    - Collect data |
                                               +-------------------+
```

1. **Build Process**: Define a containerized unit of computation with specified inputs/outputs
2. **Build ProcessExec**: Create an instance of a Process with concrete parameter values
3. **Build Pipeline**: Chain multiple ProcessExecs together, defining dependencies
4. **Execute Pipeline**: Run the entire workflow on the HPC environment

## Current Demo Implementation

The current demo showcases a lightweight implementation of NeuroAnalyst using the Python Textual library for the Terminal User Interface (TUI)[1]. The interface is divided into two main panels:

### Left Panel: Job Submission

This panel currently supports:
- Creating new Process definitions via JSON input
- Instantiating ProcessExecs from Processes with parameter specifications
- Building Pipelines by chaining ProcessExecs
- Submitting user queries to the Insight API for LLM-powered knowledge discovery

**Note:** The current implementation requires direct JSON submission for all operations, as the form-based input functionality is still under development. A far superior version with intuitive forms and visual workflow builders is being actively developed.

### Right Panel: Results Visualization

This panel displays:
- Lists of all defined Processes, ProcessExecs, and Pipelines
- Detailed view of selected items, including parameter values and status
- Results metrics and analysis outputs
- Responses from the LLM-powered Insight API

### Technical Implementation Details

The demo leverages:
- **Textual TUI Framework**: For creating the terminal-based user interface with panels, input fields, and rich text display[1]
- **Apptainer Containers**: For packaging neuroimaging tools and their dependencies in a portable format suitable for HPC environments[2]
- **HPC Integration**: For executing computationally intensive neuroimaging analyses on high-performance computing resources
- **Core API**: The backend component managing the creation and execution of Processes, ProcessExecs, and Pipelines

Example JSON for creating a Process:

```json
{
  "name": "brain_extraction",
  "description": "Extract brain tissue from T1-weighted MRI",
  "container": "apptainer://neuroanalyst/bet:1.0.0",
  "inputs": [
    {"name": "t1_image", "type": "file", "description": "T1-weighted MRI image"}
  ],
  "parameters": [
    {"name": "f", "type": "float", "default": 0.5, "description": "Fractional intensity threshold"}
  ],
  "outputs": [
    {"name": "brain_mask", "type": "file", "description": "Binary brain mask"}
  ]
}
```

Example JSON for creating a ProcessExec:

```json
{
  "process_id": "brain_extraction_123",
  "parameters": {
    "f": 0.4
  },
  "inputs": {
    "t1_image": "/data/sub-01/anat/sub-01_T1w.nii.gz"
  }
}
```

## What Makes NeuroAnalyst Different?

NeuroAnalyst distinguishes itself from existing neuroimaging tools through several key innovations:

### 1. Container-First Philosophy

Unlike traditional neuroimaging pipelines that often rely on complex local installations, NeuroAnalyst embraces a container-first approach where each process is packaged as a self-contained Apptainer image[2]. This ensures:
- Complete reproducibility across computing environments
- Simplified deployment on HPC systems
- Version control of both code and dependencies
- Easy sharing of customized analysis methods

### 2. Structured Process Hierarchy

The Process → ProcessExec → Pipeline model provides a flexible yet structured approach to workflow management:
- Processes can be reused across multiple pipelines
- Parameter variations are explicitly tracked
- Dependencies are formally defined and validated
- Execution history is preserved for reproducibility

### 3. Integrated Knowledge Discovery

The integration of LLMs for interpreting and contextualizing results sets NeuroAnalyst apart:
- Automatic generation of context-aware documentation
- Literature-informed interpretation of findings
- Identification of relevant prior work
- Natural language querying of results and methods

## Future Development

While the current demo showcases the core functionality of NeuroAnalyst, several enhancements are planned:

1. **Enhanced UI**: A more sophisticated user interface with form-based input, interactive pipeline visualization, and integrated results exploration.

2. **Expanded Container Library**: More pre-packaged neuroimaging processes covering commonly used analyses across multiple modalities.

3. **Advanced Pipeline Features**: Support for conditional execution, parameter sweeps, and dynamic workflow adaptation based on intermediate results.

4. **Improved Knowledge Discovery**: Enhanced LLM integration with specialized neuroimaging knowledge and reasoning capabilities.

5. **Collaborative Features**: Sharing and reusing processes and pipelines across research teams with proper versioning and attribution.

## Conclusion

NeuroAnalyst represents a significant step forward in neuroimaging workflow management by combining containerized processing, structured metadata, and AI-powered knowledge discovery. The current TUI demo provides a glimpse of the system's capabilities, with substantial improvements planned for future versions.

By addressing the technical challenges of neuroimaging research while enhancing knowledge discovery, NeuroAnalyst aims to accelerate scientific progress and improve reproducibility in the field. We welcome feedback from the scientific community as we continue to develop and refine this tool to meet the needs of neuroimaging researchers.

Citations:
[1] https://pythongui.org/how-to-build-a-todo-tui-application-with-textual/
[2] https://chtc.cs.wisc.edu/uw-research-computing/apptainer-hpc
[3] https://learn.microsoft.com/en-us/azure/devops/pipelines/create-first-pipeline?view=azure-devops
[4] https://pmc.ncbi.nlm.nih.gov/articles/PMC2818590/
[5] https://cylc.github.io/cylc-doc/nightly_8.4/html/user-guide/running-workflows/tasks-jobs-ui.html
[6] https://pubmed.ncbi.nlm.nih.gov/38776505/
[7] https://neurosnap.ai/blog/post/full-neurosnap-api-tutorial-the-quick-easy-api-for-bioinformatics/66b00dacec3f2aa9b4be703a
[8] https://hu-neuro-pipeline.readthedocs.io/en/stable/quickstart_r.html
[9] https://hcc.unl.edu/docs/applications/user_software/using_apptainer/
[10] https://docs.drone.io/yaml/exec/
[11] https://www.youtube.com/watch?v=lGWtMYty6xQ
[12] https://neurojson.org
[13] https://pmc.ncbi.nlm.nih.gov/articles/PMC10880440/
[14] https://github.com/AllenInstitute/aisynphys
[15] https://neuroanalyzer.org
[16] https://www.academia.edu/27468569/Master_Thesis_Bootstrapping_Information_Criterion_for_Stochastic_Models_of_Point_Processes_and_The_ni_Python_Toolbox
[17] https://textual.textualize.io/tutorial/
[18] https://www.youtube.com/watch?v=CFVdh7UbNYk
[19] https://textual.textualize.io
[20] https://apptainer.org/docs/user/main/introduction.html
[21] https://www.jenkins.io/doc/book/pipeline/
[22] https://abret.org/index.php/download_file/1059/
[23] https://www.reddit.com/r/HPC/comments/yzopnr/slurmvision_a_tui_for_monitoring_inspecting_and/
[24] https://realpython.com/python-textual/
[25] https://www.hifis.net/workshop-materials/general-container/episodes/06-apptainer-in-hpc/
[26] https://stackoverflow.com/questions/63398590/exec-as-a-pipeline-component
[27] https://www.youtube.com/watch?v=afTgM2vYumo
[28] https://www.youtube.com/watch?v=aiWOTYiIzyE
[29] https://lt.linkedin.com/in/faustam
[30] https://lt.linkedin.com/in/rugil%C4%97-blauzd%C5%BEi%C5%ABnait%C4%97-187221274
[31] https://www.aset.org/career-ladder/
[32] https://pmc.ncbi.nlm.nih.gov/articles/PMC8055434/
[33] https://www.fixstars.com/en/cases
[34] https://github.com/orgs/AllenInstitute/repositories
[35] https://www.mathworks.com/matlabcentral/fileexchange/156039-nansen-neuro-analysis-software-ensemble
[36] https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2013.00026/epub
[37] https://neuroangio.org/pipeline-device/pipeline-embolization-of-cerebral-aneurysms/
[38] https://neuroangio.org/pipeline-device/pipeline-classic/
[39] https://direct.mit.edu/netn/article/6/4/960/109066/It-s-about-time-Linking-dynamical-systems-with
[40] https://www.nature.com/articles/s41593-024-01741-0