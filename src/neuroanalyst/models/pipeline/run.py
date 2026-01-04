"""
Run a Pipeline
"""
from src.neuroanalyst.utils.constants import get_current_username, NeuroAnalystPaths
from src.neuroanalyst.models.pipeline.core import NeuPipeline

import json
from pathlib import Path
from typing import Optional

import typer, questionary
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer()

def main():
    console.rule("[bold blue]Run Pipeline[/bold blue]")
    console.print(f"Welcome {get_current_username()}!")
    
    console.print("Recommended: Run this script in a terminal that supports background execution (e.g., tmux, screen) to keep it running while you work on other tasks.")
    
    # Show available pipelines
    paths = NeuroAnalystPaths()
    all_pipelines: list[NeuPipeline] = NeuPipeline.get_all_pipelines()
    if not all_pipelines:
        console.print(f"[red]No pipelines found in {paths.pipelines}. Exiting.[/red]")
        return
    pipeline_choices: list[str] = [f"{pl.about.name} (ID: {pl.pipeline_id})" for pl in all_pipelines]
    selected_pipeline: Optional[NeuPipeline] = None
    cancel: bool = False
    while not selected_pipeline and not cancel:
        selected_pipeline_choice: str = questionary.select(
            "Select a pipeline to run:",
            choices=["CANCEL"] + pipeline_choices
        ).ask()
        if not selected_pipeline_choice or selected_pipeline_choice == "CANCEL":
            console.print("[red]Pipeline selection is required. Exiting.[/red]")
            cancel = True
            return
        
        selected_index: int = pipeline_choices.index(selected_pipeline_choice)
        selected_pipeline = all_pipelines[selected_index]
        
        # Display selected pipeline info
        console.print(f"[bold green]Selected Pipeline:[/bold green] {selected_pipeline.about.name} (ID: {selected_pipeline.pipeline_id})")
        console.print(selected_pipeline)
        
        # Confirm selection
        confirm_selection: bool = questionary.confirm(
            f"Do you want to run the pipeline '{selected_pipeline.about.name}'?",
            default=True
        ).ask()
        if not confirm_selection:
            console.print("[yellow]Pipeline selection cancelled by user.[/yellow]")
            selected_pipeline = None
            
    # Run the selected pipeline
    if not selected_pipeline:
        return
    # Ask for window size (number of parallel processes at the same time)
    window_size: int = int(questionary.text(
        "Enter the window size (number of parallel processes to run at the same time):",
        default="1",
        validate=lambda text: text.isdigit() and int(text) in range(1, 31) or "Please enter a positive integer."
    ).ask())
    console.print(f"[blue]Running pipeline '{selected_pipeline.about.name}'...[/blue]")
    try:
        selected_pipeline.execute_via_python(window_size=window_size)
        console.print(f"[green]Pipeline '{selected_pipeline.about.name}' started execution. Minimize this window to continue working.[/green]")
    except Exception as e:
        console.print(f"[red]Error running pipeline '{selected_pipeline.about.name}': {e}[/red]")
        
@app.command()
def start():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Pipeline run interrupted by user.[/red]")
    except EOFError:
        console.print("\n[red]Pipeline run interrupted by user (EOF).[/red]")
    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/red]")
        
if __name__ == "__main__":
    app()