"""
Build Process Environment
"""
from src.neuroanalyst.utils.constants import get_current_username
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
    
    all_logics: list[NeuProcessLogic] = NeuProcessLogic.get_all_registered_logics()
    if not all_logics:
        console.print("[red]No registered process logics found. Exiting.[/red]")
        return
    
    # Loop until a logic is selected or cancelled
    cancel: bool = False
    selected_logic: Optional[NeuProcessLogic] = None
    
    while not selected_logic and not cancel:
        selected_logic_name: str = questionary.select(
            "Select a process logic to build its environment:",
            choices=["CANCEL"] + [logic.about.name for logic in all_logics]
        ).ask()
        if not selected_logic_name or selected_logic_name == "CANCEL":
            console.print("[red]Process logic selection is required. Exiting.[/red]")
            cancel = True
            return
        
        selected_logic: NeuProcessLogic = next(logic for logic in all_logics if logic.about.name == selected_logic_name)
        
        # Display selected logic info
        console.print(Panel.fit(f"[bold green]Selected Process Logic:[/bold green] {selected_logic.about.name} (Name: {selected_logic.about.name})"))
        console.print(Panel.fit(selected_logic.code))
        
        # Confirm selection
        confirm_selection: bool = questionary.confirm(
            f"Do you want to build the environment for process logic '{selected_logic.about.name}'?",
            default=True
        ).ask()
        if not confirm_selection:
            console.print("[yellow]Process logic selection cancelled by user.[/yellow]")
            selected_logic = None
            
    # Create NeuProcessDir instance
    if not selected_logic:
        return
    
    selected_process_dir: NeuProcessDir = NeuProcessDir.from_logic(selected_logic)
    selected_process: NeuProcess = NeuProcess.from_process_dir(selected_process_dir)
    console.print(Panel.fit(f"[bold green]Process Directory Created for:[/bold green] {selected_process_dir.logic.about.name}"))
        
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
            f"Do you want to build the Singularity image for process '{selected_process_dir.logic.about.name}' now?",
            default=True
        ).ask()
        if confirm_build:
            console.print(f"[blue]Building Singularity image...[/blue]")
            try:
                selected_process_dir.build_singularity_image()
                console.print(f"[green]Singularity image built successfully at {selected_process.image_path}[/green]")
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