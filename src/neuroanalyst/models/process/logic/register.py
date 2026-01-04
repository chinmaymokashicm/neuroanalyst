"""
Register a Logic from a recipe
"""
from src.neuroanalyst.models.process.logic.core import NeuProcessLogic
from src.neuroanalyst.models.recipe.core import (
    create_logic_from_recipe
)
from src.neuroanalyst.utils.constants import get_current_username, NeuroAnalystPaths

from pathlib import Path
from typing import Optional
import yaml
from datetime import datetime

import typer, questionary
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer()

def main():
    console.rule("[bold blue]Register Process Logic from Recipe[/bold blue]")
    console.print(f"Welcome {get_current_username()}!")
    
    paths = NeuroAnalystPaths()
    logic_recipes_root: Path = paths.recipes / "process_logic"
    
    # Load available logic recipes
    available_recipes: list[Path] = list(logic_recipes_root.glob("*.yaml"))
    if not available_recipes:
        console.print(f"[red]No process logic recipes found in {logic_recipes_root}. Exiting.[/red]")
        return
    
    # Loop until a recipe is selected or cancelled
    cancel: bool = False
    selected_recipe_path: Optional[Path] = None
    while not selected_recipe_path and not cancel:
        recipe_choices: list[str] = [recipe.name for recipe in available_recipes]
        
        selected_recipe_choice: str = questionary.select(
            "Select a process logic recipe to register:",
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
            indent=2
        )
        console.print(Panel.fit(yaml_str, title="Recipe Content"))
        
        # Confirm selection
        confirm_selection: bool = questionary.confirm(
            f"Do you want to register the process logic from recipe '{selected_recipe_path.name}'?",
            default=True
        ).ask()
        if not confirm_selection:
            console.print("[yellow]Recipe selection cancelled by user.[/yellow]")
            selected_recipe_path = None
    
    # Register the selected process logic
    if not selected_recipe_path:
        return
    
    console.print(f"[blue]Registering process logic from recipe '{selected_recipe_path.name}'...[/blue]")
    new_logic: NeuProcessLogic = create_logic_from_recipe(selected_recipe_path)
    new_logic.register()
    console.print(f"[bold green]Successfully registered process logic '{new_logic.about.name}' with ID '{new_logic.logic_id}'[/bold green]")
    
@app.command()
def start():
    try:
        main()
    except KeyboardInterrupt:
        console.print("[yellow]Execution interrupted by user.[/yellow]")
        typer.Exit(code=130)
    except EOFError:
        console.print("[red]No input received. Exiting.[/red]")
        typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]")
        typer.Exit(code=1)
        
if __name__ == "__main__":
    app()