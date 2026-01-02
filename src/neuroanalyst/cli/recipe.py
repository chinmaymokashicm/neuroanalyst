import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from .pydantic import PydanticWizard
from neuroanalyst.models.recipe.core import (
    LogicRecipe,
    ProcessDirRecipe,
    PipelineRecipe,
    create_logic_from_recipe,
    create_process_dir_from_recipe,
    construct_pipeline_from_recipe,
    save_recipe_to_yaml,
    create_logic_from_recipe,
    )
from neuroanalyst.utils.constants import get_current_username
from neuroanalyst.models.process.logic.core import NeuProcessLogic
from neuroanalyst.models.process.dir.core import NeuProcessDir
from neuroanalyst.models.pipeline.core import NeuPipeline
from neuroanalyst.models.process.logic.code.python.decoder import PythonDecoder

from typing import Any, Type, Optional, Union, get_args, get_origin

import typer, questionary
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()

def main():
    console.print(
        Panel(
            "Create a recipe to build an IntelliBIDS component",
            title=f"[bold blue]Recipe Wizard[/bold blue] | User: [green]{get_current_username()}[/green]",
        )
    )
    
    typer.echo("Select a component type to create:")
    component_type: str = questionary.select(
        "Component Type:",
        choices=[
            "Logic",
            "Process",
            "Pipeline",
        ],
    ).ask()
    
    if component_type == "Logic":
        recipe_model = LogicRecipe
    elif component_type == "Process":
        recipe_model = ProcessDirRecipe
    elif component_type == "Pipeline":
        recipe_model = PipelineRecipe
    else:
        console.print("[red]Invalid component type selected. Exiting.[/red]")
        return
    
    wizard = PydanticWizard(recipe_model, console)
    try:
        recipe_instance = wizard.run()
    except Exception as e:
        console.print(f"[red]Failed to create recipe instance: {e}[/red]")
        return
    console.print(f"[green]Recipe instance created successfully![/green]")
    console.print(recipe_instance.model_dump_json(indent=2))
    if isinstance(recipe_instance, LogicRecipe):
        decoder = PythonDecoder()
        logic: NeuProcessLogic = decoder.decode_from_file(recipe_instance.path)
        recipe_name: str = logic.about.name
    elif isinstance(recipe_instance, ProcessDirRecipe):
        recipe_name: str = recipe_instance.logic
    elif isinstance(recipe_instance, PipelineRecipe):
        recipe_name: str = recipe_instance.name
    else:
        raise ValueError("Unknown recipe instance type.")
    
    try:
        recipe_path: str = save_recipe_to_yaml(recipe_instance, recipe_name)
        console.print(f"[green]Recipe saved successfully![/green]")
        console.print(
            Panel(f"Recipe Details:\n{create_logic_from_recipe(recipe_path)}", title="[bold blue]Recipe Summary[/bold blue]")
        )
    except Exception as e:
        console.print(f"[red]Failed to save recipe: {e}[/red]")
    
@app.command()
def start():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Recipe creation cancelled by user.[/red]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"\n[red]An unexpected error occurred: {e}[/red]")
        raise typer.Exit(code=1)
    
if __name__ == "__main__":
    typer.run(main)