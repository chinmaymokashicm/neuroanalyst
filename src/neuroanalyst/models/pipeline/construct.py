"""
Construct a Pipeline from a recipe
"""
from src.neuroanalyst.models.recipe.core import (
    construct_pipeline_from_recipe,
    get_recipe_yaml_path,
)
from src.neuroanalyst.models.pipeline.core import NeuPipeline
from src.neuroanalyst.models.process.process.core import NeuProcess
from src.neuroanalyst.utils.constants import get_current_username, NeuroAnalystPaths

from pathlib import Path
from typing import Optional
import yaml, time, traceback
from datetime import datetime

import typer, questionary
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer()

def main():
    console.rule("[bold blue]Create Pipeline from Recipe")
    console.print(f"Welcome {get_current_username()}!")
    
    paths = NeuroAnalystPaths()
    pipeline_recipes_root: Path = paths.recipes / "pipeline"
    
    # Load available pipeline recipes
    available_recipes: list[Path] = list(pipeline_recipes_root.glob("*.yaml"))
    if not available_recipes:
        console.print(f"[red]No pipeline recipes found in {pipeline_recipes_root}. Exiting.[/red]")
        return
    
    # Loop until a recipe is selected or cancelled
    cancel: bool = False
    selected_recipe_path: Optional[Path] = None
    while not selected_recipe_path and not cancel:
        recipe_choices: list[str] = [recipe.name for recipe in available_recipes]
        
        selected_recipe_choice: str = questionary.select(
            "Select a pipeline recipe to construct:",
            choices=["CANCEL"] + recipe_choices
        ).ask()
        if not selected_recipe_choice or selected_recipe_choice == "CANCEL":
            console.print("[red]Recipe selection is required. Exiting.[/red]")
            cancel = True
            return
        
        selected_index: int = recipe_choices.index(selected_recipe_choice)
        selected_recipe_path = available_recipes[selected_index]
        
        # Display selected recipe info
        console.print(Panel.fit(f"[bold green]Selected Recipe:[/bold green] {selected_recipe_path.name}"))
        with open(selected_recipe_path, 'r') as file:
            recipe_content = yaml.safe_load(file)
        yaml_str = yaml.dump(
            recipe_content,
            sort_keys=False,
            indent=4,
        )
        console.print(Panel.fit(yaml_str, title="Recipe Content", subtitle=str(selected_recipe_path)))
    
        # Confirm selection
        confirm_selection: bool = questionary.confirm(
            f"Do you want to create the pipeline from recipe '{selected_recipe_path.name}'?",
            default=True
        ).ask()
        if not confirm_selection:
            console.print("[yellow]Recipe selection cancelled by user.[/yellow]")
            selected_recipe_path = None
            
    if not selected_recipe_path:
        console.print("[red]No recipe selected. Exiting.[/red]")
        return
    
    # Create pipeline from selected recipe
    try:
        pipeline: NeuPipeline = construct_pipeline_from_recipe(selected_recipe_path)
        console.print(Panel.fit(f"[bold green]Pipeline '{pipeline.about.name}' created successfully![/bold green]\n\n[bold]Pipeline ID:[/bold] {pipeline.pipeline_id}\n[bold]Description:[/bold] {pipeline.about.description}"))
    except Exception as e:
        console.print(f"[red]Error creating pipeline from recipe: {e}[/red]")
        return
            
    all_processes: list[NeuProcess] = [NeuProcess.from_process_id(process_id) for process_id in pipeline.all_process_ids]
    # Check if the process images are built
    time_elapsed: datetime = datetime.now()
    while any(not process.is_image_built for process in all_processes):
        for process in all_processes:
            if process.is_image_built:
                console.print(f"[green]Process '{process.logic.about.name}' environment is built.[/green]")
            else:
                console.print(f"[yellow]Process '{process.logic.about.name}' environment is NOT built.[/yellow]")
                console.print(f"[blue]Do you want to build the environment for process '{process.logic.about.name}' now?[/blue]")
                build_now: bool = questionary.confirm(
                    f"Build environment for process '{process.logic.about.name}'?",
                    default=True
                ).ask()
                if build_now:
                    try:
                        process.build_singularity_image()
                        console.print(f"[green]Process '{process.logic.about.name}' environment build started at {process.image_path}[/green]")
                    except Exception as e:
                        console.print(f"[red]Error building environment for process '{process.logic.about.name}': {e}[/red]")
                else:
                    console.print(f"[yellow]Skipping build for process '{process.logic.about.name}'.[/yellow]")
                    return
        console.print("[blue]Rechecking process environments...[/blue]")
        console.print(f"[blue]Time elapsed since start: {datetime.now() - time_elapsed}[/blue]")
        all_processes = [NeuProcess.from_process_id(process_id) for process_id in pipeline.all_process_ids]
        time.sleep(5)
    
    # Check if the pipeline is ready for execution
    if pipeline.is_ready:
        console.print(f"[green]Pipeline '{pipeline.about.name}' is ready for execution.[/green]")
    else:
        console.print(f"[yellow]Pipeline '{pipeline.about.name}' is not ready for execution. Please check the configuration.[/yellow]")
        

@app.command()
def start():
    try:
        main()
    except KeyboardInterrupt:
        console.print("[yellow]Execution interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        console.print(traceback.format_exc())
        
if __name__ == "__main__":
    app()