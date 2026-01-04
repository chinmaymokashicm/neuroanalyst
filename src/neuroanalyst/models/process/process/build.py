"""
Build Process Environment
"""
from src.neuroanalyst.utils.constants import get_current_username
from src.neuroanalyst.models.process.dir.core import NeuProcessDir

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
    
    all_process_dirs: list[NeuProcessDir] = NeuProcessDir.get_all_process_dirs()
    
    # Loop until a process is selected or cancelled
    cancel: bool = False
    selected_process: Optional[NeuProcessDir] = None
    while not selected_process and not cancel:
        process_choices: list[str] = [f"{proc.logic.about.name} (ID: {proc.process_id})" for proc in all_process_dirs]
        selected_process_choice: str = questionary.select(
            "Select a process to build its environment:",
            choices=["CANCEL"] + process_choices
        ).ask()
        if not selected_process_choice or selected_process_choice == "CANCEL":
            console.print("[red]Process selection is required. Exiting.[/red]")
            cancel = True
            return
        
        selected_index: int = process_choices.index(selected_process_choice)
        selected_process = all_process_dirs[selected_index]
        
        # Display selected process info
        console.print(Panel.fit(f"[bold green]Selected Process:[/bold green] {selected_process.logic.about.name} (ID: {selected_process.process_id})"))
        console.print(Panel.fit(selected_process))
        
        # Confirm selection
        confirm_selection: bool = questionary.confirm(
            f"Do you want to build the environment for process '{selected_process.logic.about.name}'?",
            default=True
        ).ask()
        if not confirm_selection:
            console.print("[yellow]Process selection cancelled by user.[/yellow]")
            selected_process = None
    
    # Check if process environment is already built
    if selected_process.is_image_built:
        console.print(f"[yellow]Process environment is already built at {selected_process.image_path}[/yellow]")
    
    if selected_process.is_venv_created:
        console.print(f"[yellow]Virtual environment is already created at {selected_process.venv_path}[/yellow]")
        
    # Select environment type to build
    env_type: str = questionary.select(
        "Select the type of environment to build:",
        choices=["Singularity Image", "Virtual Environment"]
    ).ask()
    if not env_type:
        console.print("[red]Environment type selection is required. Exiting.[/red]")
        return
    
    if env_type == "Singularity Image":
        confirm_build: bool = questionary.confirm(
            f"Do you want to build the Singularity image for process '{selected_process.logic.about.name}' now?",
            default=True
        ).ask()
        if confirm_build:
            console.print(f"[blue]Building Singularity image...[/blue]")
            try:
                selected_process.build_singularity_image()
                console.print(f"[green]Singularity image built successfully at {selected_process.image_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error building Singularity image: {e}[/red]")
        else:
            console.print("[yellow]Singularity image build cancelled by user.[/yellow]")
    elif env_type == "Virtual Environment":
        confirm_build: bool = questionary.confirm(
            f"Do you want to create the virtual environment for process '{selected_process.logic.about.name}' now?",
            default=True
        ).ask()
        if confirm_build:
            console.print(f"[blue]Creating virtual environment...[/blue]")
            try:
                selected_process.create_virtual_env()
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