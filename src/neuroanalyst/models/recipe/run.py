"""
Create a component from a recipe
"""
from src.neuroanalyst.utils.constants import get_current_username, NeuroAnalystPaths
from src.neuroanalyst.models.recipe.core import (
    create_logic_from_recipe,
    create_process_dir_from_recipe,
    construct_pipeline_from_recipe,
    save_recipe_to_yaml,
    get_recipe_yaml_path,
    LogicRecipe,
    ProcessDirRecipe,
    ProcessExecInStepRecipe,
    PipelineStepRecipe,
    PipelineRecipe,
    RECIPE_FACTORIES
    )
from src.neuroanalyst.models.process.logic.core import NeuProcessLogic
from src.neuroanalyst.models.process.dir.core import NeuProcessDir
from src.neuroanalyst.models.pipeline.core import NeuPipeline

from pathlib import Path
from typing import Optional
import yaml

import typer, questionary
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer()

def main():
    console.rule("[bold blue]Create Component from Recipe")
    console.print(f"Welcome {get_current_username()}!")
    
    paths = NeuroAnalystPaths()
    recipes_root: Path = paths.recipes
    
    # Ask for recipe type
    recipe_type: str = questionary.select(
        "Select the type of recipe to create:",
        choices=list(RECIPE_FACTORIES.keys())
    ).ask()
    if not recipe_type:
        console.print("[red]Recipe type is required. Exiting.[/red]")
        return
    
    cancel: bool = False
    selected_recipe_path: Optional[Path] = None
    
    while not selected_recipe_path and not cancel:
        recipe_dir: Path = recipes_root / recipe_type
        available_recipes: list[Path] = sorted([p for p in recipe_dir.glob("*.yaml") if p.is_file() and not p.name.startswith(".")])
        if not available_recipes:
            console.print(f"[red]No recipes found for type '{recipe_type}'. Exiting.[/red]")
            return
        
        # Ask for recipe selection
        recipe_choices: list[str] = [recipe.stem for recipe in available_recipes]
        selected_recipe_name: str = questionary.autocomplete(
            "Select a recipe to create the component from:",
            choices=["CANCEL"] + recipe_choices
        ).ask()
        if not selected_recipe_name or selected_recipe_name == "CANCEL":
            console.print("[red]Recipe selection is required. Exiting.[/red]")
            cancel = True
            return
        
        # Display selected recipe info
        selected_index: int = recipe_choices.index(selected_recipe_name)
        selected_recipe_path = available_recipes[selected_index]
        with open(selected_recipe_path, "r") as f:
            recipe = yaml.safe_load(f)
        yaml_str = yaml.dump(
            recipe,
            sort_keys=False,
            indent=4,
        )
        console.print(Panel.fit(f"[bold green]Selected Recipe:[/bold green] {selected_recipe_name}\n\n{yaml_str}"))
        
        # Confirm selection
        confirm = questionary.confirm(
            "Do you want to proceed with this recipe?",
            default=True
        ).ask()
        if not confirm:
            selected_recipe_path = None
    
    if not selected_recipe_path:
        console.print("[red]No recipe selected. Exiting.[/red]")
        return

    console.print(f"[blue]Loading recipe from:[/blue] {selected_recipe_path}")
    
    # Create component from recipe
    if recipe_type == "logic":
        logic: NeuProcessLogic = create_logic_from_recipe(selected_recipe_path)
        register: bool = questionary.confirm(
            f"Do you want to register the logic '{logic.about.name}' now?",
            default=True
        ).ask()
        if register:
            logic.register(overwrite=True)
            console.print(f"[green]Logic '{logic.about.name}' registered successfully.[/green]")
            console.print(logic)
    elif recipe_type == "process":
        process_dir: NeuProcessDir = create_process_dir_from_recipe(selected_recipe_path)
        generate: bool = questionary.confirm(
            f"Do you want to generate the process directory for '{process_dir.logic}' now?",
            default=True
        ).ask()
        if generate:
            process_dir.generate()
            console.print(f"[green]Process directory for '{process_dir.logic}' created at {process_dir.working_dir}.[/green]")
            console.print(process_dir)
    elif recipe_type == "pipeline":
        pipeline: NeuPipeline = construct_pipeline_from_recipe(selected_recipe_path)
        create: bool = questionary.confirm(
            f"Do you want to create the pipeline '{pipeline.pipeline_id}' now?",
            default=True
        ).ask()
        if create:
            pipeline.create_pipeline_dir()
            console.print(f"[green]Pipeline '{pipeline.pipeline_id}' created successfully.[/green]")
            console.print(pipeline)
    else:
        console.print(f"[red]Unsupported recipe type '{recipe_type}'. Exiting.[/red]")
        return
    
@app.command()
def run():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Operation cancelled by user.[/red]")
        raise typer.Exit(code=130)
    except EOFError:
        console.print("\n[red]No input provided. Exiting.[/red]")
        raise typer.Exit(code=130)

if __name__ == "__main__":
    app()