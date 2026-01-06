"""
Build Process Environment
"""
from src.neuroanalyst.utils.constants import get_current_username, NeuroAnalystPaths
from src.neuroanalyst.models.recipe.core import (
    ProcessDirRecipe,
    save_recipe_to_yaml,
    get_recipe_yaml_path,
    create_process_dir_from_recipe
)
from src.neuroanalyst.models.process.dir.core import NeuProcessDir
from src.neuroanalyst.models.process.process.core import NeuProcess
from src.neuroanalyst.models.process.logic.core import NeuProcessLogic

from pathlib import Path
from typing import Optional

import typer, questionary
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer()

def main():
    console.rule("[bold blue]Build Process Environment[/bold blue]")
    console.print(f"Welcome {get_current_username()}!")
    
    all_process_recipe_paths: list[Path] = sorted([p for p in NeuroAnalystPaths().recipes.glob("process/*.yaml") if p.is_file() and not p.name.startswith(".")])
    
    cancel: bool = False
    selected_recipe_path: Optional[Path] = None
    while not selected_recipe_path and not cancel:
        recipe_choices: list[str] = [path.stem for path in all_process_recipe_paths]
        
        selected_recipe_choice: str = questionary.autocomplete(
            "Select a process recipe to build environment for:",
            choices=["CANCEL"] + sorted(recipe_choices)
        ).ask()
        if not selected_recipe_choice or selected_recipe_choice == "CANCEL":
            console.print("[red]Recipe selection is required. Exiting.[/red]")
            cancel = True
            return
        
        selected_index: int = recipe_choices.index(selected_recipe_choice)
        selected_recipe_path = all_process_recipe_paths[selected_index]
        
        # Display selected recipe info
        console.print(Panel.fit(f"[bold green]Selected Recipe:[/bold green] {selected_recipe_path.name}"))
        recipe_content: ProcessDirRecipe = get_recipe_yaml_path(selected_recipe_path.stem, recipe_type="process")
        console.print(recipe_content)
        
        # Confirm selection
        confirm_selection: bool = questionary.confirm(
            f"Do you want to build the environment for process '{selected_recipe_path.stem}'?",
            default=True
        ).ask()
        if not confirm_selection:
            console.print("[yellow]Recipe selection cancelled by user.[/yellow]")
            selected_recipe_path = None
    
    selected_process_dir: NeuProcessDir = create_process_dir_from_recipe(selected_recipe_path)
    selected_process: NeuProcess = NeuProcess.from_process_dir(selected_process_dir)
    console.print(Panel.fit(f"[bold green]Process Directory Created for:[/bold green] {selected_process_dir.logic.about.name}"))
        
    # Select environment type to build
    env_type: str = questionary.autocomplete(
        "Select the type of environment to build:",
        choices=["Singularity Image", "Virtual Environment"]
    ).ask()
    if not env_type:
        console.print("[red]Environment type selection is required. Exiting.[/red]")
        return
    
    if env_type == "Singularity Image":
        confirm_build: bool = questionary.confirm(
            f"Do you want to build the Singularity image for process '{selected_process_dir.logic.about.name}' now?",
            default=True
        ).ask()
        if confirm_build:
            selected_process_dir.generate()
            console.print(f"[blue]Building Singularity image...[/blue]")
            try:
                selected_process_dir.build_singularity_image()
                console.print(f"[green]Singularity image build started at {selected_process.image_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error building Singularity image: {e}[/red]")
        else:
            console.print("[yellow]Singularity image build cancelled by user.[/yellow]")
    elif env_type == "Virtual Environment":
        confirm_build: bool = questionary.confirm(
            f"Do you want to create the virtual environment for process '{selected_process_dir.logic.about.name}' now?",
            default=True
        ).ask()
        if confirm_build:
            console.print(f"[blue]Creating virtual environment...[/blue]")
            try:
                selected_process_dir.create_virtual_env()
                console.print(f"[green]Virtual environment created successfully at {selected_process.venv_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error creating virtual environment: {e}[/red]")
        else:
            console.print("[yellow]Virtual environment creation cancelled by user.[/yellow]")
            
@app.command()
def start():
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