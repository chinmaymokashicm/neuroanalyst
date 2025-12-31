from ...utils.constants import NeuroAnalystPaths
from ..process.logic.code.python.decoder import PythonDecoder
from ..about import About
from ..process.logic.core import NeuProcessLogic
from ..process.dir.core import NeuProcessDir, NeuProcessDirConfig
from ..process.exec.core import NeuProcessExec
from ..pipeline.core import NeuPipeline
from ..pipeline.constructor import PipelineConstructorConfig, PipelineStepConstructorConfig, ProcessConstructorConfig

import yaml
from typing import Optional, Literal
from pathlib import Path

from pydantic import Field, BaseModel, field_validator
from polyfactory.factories.pydantic_factory import ModelFactory
from ruamel.yaml import YAML

class LogicRecipe(BaseModel):
    """
    Model representing a logic recipe for creating NeuProcessLogic instances.
    """
    path: str = Field(..., description="Path to the Python code file defining the process logic.")
    function: Optional[str] = Field(None, description="Function string if path does not read to a single function definition.")
    username: Optional[str] = Field(None, description="Username of the process logic author.")
    version: Optional[str] = Field(None, description="Version string for the process logic.")
    tag: Optional[str] = Field(None, description="Tag string for the process logic.")
    author: Optional[str] = Field(None, description="Author string for the process logic.")

class ProcessDirRecipe(BaseModel):
    """
    Model representing a process directory recipe for creating NeuProcessDir instances.
    """
    class LogicDetails(BaseModel):
        name: str = Field(..., description="Name of the logic.")
        username: Optional[str] = Field(None, description="Username of the logic author.")
        
    logic: LogicDetails = Field(..., description="Dictionary containing logic name and optional username.")
    config: Optional[NeuProcessDirConfig] = Field(None, description="Configuration for the process directory.")
    
class ProcessExecInStepRecipe(BaseModel):
    process_id: str = Field(..., description="Process ID.")
    input_bids_filters: dict = Field(..., description="BIDS filters for selecting input files.", default_factory=dict)
    extra_bind_paths: dict = Field(..., description="Extra bind paths for the process execution.", default_factory=dict)
    extra_environment_variables: dict = Field(..., description="Extra environment variables for the process execution.", default_factory=dict)

class PipelineStepRecipe(BaseModel):
    name: str = Field(..., description="Name of the step.")
    description: Optional[str] = Field(None, description="Description of the step.")
    processes: list[ProcessExecInStepRecipe] = Field(..., description="List of process executions in this step.")
    
    def __iter__(self):
        return iter(self.processes)

class PipelineRecipe(BaseModel):
    username: Optional[str] = Field(None, description="Namespace within the installation.")
    author: str = Field(..., description="Author of the pipeline.")
    data: str = Field(..., description="Path to the data directory.")
    name: str = Field(..., description="Name of the pipeline.", pattern=r"^\S+$")
    description: Optional[str] = Field(None, description="Description of the pipeline.")
    auto_link: bool = Field(False, description="Whether to auto-link outputs to inputs of subsequent steps.")
    cost: int = Field(
        ...,
        description="Estimated compute cost scale for each process, used for chunk size optimization. Higher values indicate more compute-intensive processes and smaller chunk sizes. Use values between 1 and 10.",
        ge=1,
        le=10
    )
    steps: list[PipelineStepRecipe] = Field(..., description="List of steps in the pipeline.")
    starting_bids_scope: Optional[dict] = Field(None, description="BIDS scope dictionary for the starting inputs of the pipeline.")
    
    def __iter__(self):
        return iter(self.steps)

RECIPE_FACTORIES: dict[str, BaseModel] = {
    "logic": LogicRecipe,
    "process": ProcessDirRecipe,
    "pipeline": PipelineRecipe,
}

def create_mock_recipe(
    recipe_type: Literal["logic", "process", "pipeline"],
    name: str,
    username: Optional[str] = None,
    save: bool = False
    ) -> Optional[Path]:
    try:
        class Factory(ModelFactory[RECIPE_FACTORIES[recipe_type]]): ...
        mock_recipe: LogicRecipe | ProcessDirRecipe | PipelineRecipe = Factory.build()
        if save:
            return save_recipe_to_yaml(mock_recipe, name, username)
        return mock_recipe
    except KeyError:
        raise ValueError(f"Invalid recipe type: {recipe_type}")
    
def save_recipe_to_yaml(recipe: BaseModel, recipe_name: str, username: Optional[str] = None) -> str:
    """
    Save a recipe Pydantic model to a YAML file.
    
    Args:
        recipe (BaseModel): The recipe Pydantic model instance.
        recipe_name (str): Name of the recipe.
        username (Optional[str]): Username of the recipe author.
        
    Returns:
        str: The file path of the saved recipe YAML file.
    """
    if not isinstance(recipe, BaseModel):
        raise ValueError("Recipe must be a Pydantic BaseModel instance.")
    paths = NeuroAnalystPaths(username=username)
    if isinstance(recipe, LogicRecipe):
        output_path: str = paths.get_recipes_dir("logic") / f"{recipe_name}.yaml"
    elif isinstance(recipe, ProcessDirRecipe):
        output_path: str = paths.get_recipes_dir("process") / f"{recipe_name}.yaml"
    elif isinstance(recipe, PipelineRecipe):
        output_path: str = paths.get_recipes_dir("pipeline") / f"{recipe_name}.yaml"
    else:
        raise ValueError("Unsupported recipe type.")
    
    ruayaml = YAML()
    ruayaml.indent(mapping=2, sequence=4, offset=2)
    with open(output_path, "w") as f:
        try:
            ruayaml.dump(recipe.model_dump(), f)
        except Exception:
            yaml.dump(recipe.model_dump(), f)
        
    return output_path
        
def get_recipe_yaml_path(recipe_name: str, recipe_type: str, username: Optional[str] = None) -> Path:
    """
    Get the file path of a recipe YAML file based on its name and type.
    Args:
        recipe_name (str): Name of the recipe.
        recipe_type (str): Type of the recipe ("logic", "process", or "pipeline").
        username (Optional[str]): Username of the recipe author.
        
    Returns:
        Path: The file path of the recipe YAML file.
    """
    paths = NeuroAnalystPaths(username=username)
    if recipe_type == "logic":
        recipe_path: Path = paths.get_recipes_dir("logic") / f"{recipe_name}.yaml"
    elif recipe_type == "process":
        recipe_path: Path = paths.get_recipes_dir("process") / f"{recipe_name}.yaml"
    elif recipe_type == "pipeline":
        recipe_path: Path = paths.get_recipes_dir("pipeline") / f"{recipe_name}.yaml"
    else:
        raise ValueError("recipe_type must be one of 'logic', 'process', or 'pipeline'.")
    if not recipe_path.exists():
        raise FileNotFoundError(f"Recipe file does not exist: {recipe_path}")
    return recipe_path

def create_logic_from_recipe(recipe_path: str | Path) -> NeuProcessLogic:
    """
    Load a NeuProcessLogic instance from a recipe YAML file.
    Required keys in the recipe file:
        - path: Path to the Python code file defining the process logic.
    Optional keys:
        - function: function string if path does not read to a single function definition.
        - username: Username of the process logic author.
        - version: Version string for the process logic.
        - tag: Tag string for the process logic.
        - author: Author string for the process logic.

    Args:
        recipe_path (str | Path): Path to the recipe YAML file.
        
    Returns:
        NeuProcessLogic: An instance of NeuProcessLogic loaded from the recipe file.
    """
    recipe_path = Path(recipe_path)
    if not recipe_path.exists():
        raise FileNotFoundError(f"Recipe file does not exist: {recipe_path}")
    with recipe_path.open("r") as f:
        recipe: dict = yaml.safe_load(f)
    
    logic_recipe: LogicRecipe = LogicRecipe.model_validate(recipe)
    decoder: PythonDecoder = PythonDecoder()
    if not Path(logic_recipe.path).exists():
        raise FileNotFoundError(f"Logic code file does not exist: {logic_recipe.path}")
    with open(logic_recipe.path, "r") as code_file:
        code_str: str = code_file.read()
    try:
        logic: NeuProcessLogic = decoder.decode_from_string(code_str)
    except Exception as e:
        if not logic_recipe.function:
            raise ValueError(f"Error decoding logic from code file: {e}. No function string provided in recipe.")
        try:
            logic: NeuProcessLogic = decoder.decode_from_string(code_str, function_name=logic_recipe.function)
        except Exception as e2:
            raise ValueError(f"Error decoding logic from code file with function '{logic_recipe.function}': {e2}")
    # Update metadata if provided
    logic.username = logic_recipe.username or logic.username
    logic.about.version = logic_recipe.version or logic.about.version
    logic.about.tag = logic_recipe.tag or logic.about.tag
    logic.about.author = logic_recipe.author or logic.about.author

    return logic

def create_process_dir_from_recipe(recipe_path: str | Path) -> NeuProcessDir:
    """
    Create a NeuProcessDir instance from a recipe YAML file.

    Args:
        recipe_path (str | Path): Path to the recipe YAML file.
    Returns:
        NeuProcessDir: An instance of NeuProcessDir created from the recipe file.
    """
    if not Path(recipe_path).exists():
        raise FileNotFoundError(f"Recipe file does not exist: {recipe_path}")
    with open(recipe_path, "r") as f:
        recipe: dict = yaml.safe_load(f)
        
    process_dir_recipe: ProcessDirRecipe = ProcessDirRecipe.model_validate(recipe)
    logic_name: str = process_dir_recipe.logic.name
    logic_username: Optional[str] = process_dir_recipe.logic.username
    logic: NeuProcessLogic = NeuProcessLogic.from_func_name(logic_name, logic_username)
    if not logic:
        raise ValueError(f"Could not find NeuProcessLogic with name '{logic_name}' and username '{logic_username}'")
    config: Optional[NeuProcessDirConfig] = process_dir_recipe.config
    process_dir: NeuProcessDir = NeuProcessDir.from_logic(
        logic=logic,
        config=config
    )
    return process_dir

def construct_pipeline_from_recipe(recipe_path: str | Path) -> NeuPipeline:
    """
    Create a NeuPipeline instance from a recipe YAML file.

    Args:
        recipe_path (str | Path): Path to the recipe YAML file.
    Returns:
        NeuPipeline: An instance of NeuPipeline created from the recipe file.
    """
    if not Path(recipe_path).exists():
        raise FileNotFoundError(f"Recipe file does not exist: {recipe_path}")
    with open(recipe_path, "r") as f:
        recipe: dict = yaml.safe_load(f)
        
    pipeline_recipe: PipelineRecipe = PipelineRecipe.model_validate(recipe)
    pipeline_step_configs: list[PipelineStepConstructorConfig] = []
    
    # Auto-linking - except for the first step, use previous step's output_entities as current step's input_bids_filters if enabled
    current_input_bids_filters: Optional[dict] = None
    for step_recipe in pipeline_recipe.steps:
        process_configs: list[ProcessConstructorConfig] = []
        for process_exec_recipe in step_recipe.processes:
            process_config = ProcessConstructorConfig(
                username=pipeline_recipe.username,
                process_id=process_exec_recipe.process_id,
                input_bids_filters=current_input_bids_filters or process_exec_recipe.input_bids_filters,
                extra_bind_paths=process_exec_recipe.extra_bind_paths,
                extra_environment_variables=process_exec_recipe.extra_environment_variables
            )
            process_config.validate_config()
            process_configs.append(process_config)
            
        # Update current_input_bids_filters for auto-linking if enabled
        if pipeline_recipe.auto_link:
            current_input_bids_filters = process_config.process.output_entities
            
        step_config = PipelineStepConstructorConfig(
            name=step_recipe.name,
            description=step_recipe.description,
            process_configs=process_configs
        )
        pipeline_step_configs.append(step_config)
        
    pipeline_config = PipelineConstructorConfig(
        about={
            "name": pipeline_recipe.name,
            "description": pipeline_recipe.description,
            "username": pipeline_recipe.username,
            "author": pipeline_recipe.author
        },
        steps=pipeline_step_configs,
        scheduler="lsf"
    )
    pipeline: NeuPipeline = pipeline_config.to_pipeline(
        bids_root=pipeline_recipe.data,
        probable_compute_cost=pipeline_recipe.cost,
        starting_bids_scope=pipeline_recipe.starting_bids_scope
    )
    return pipeline