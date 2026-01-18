"""
Delete a pipeline and its associated process execs from the system.
"""
from src.neuroanalyst.models.pipeline.core import NeuPipelineStepStatus, ProcessStatus, NeuPipelineStatus
from src.neuroanalyst.models.pipeline import NeuPipeline
from src.neuroanalyst.models.process.exec.core import NeuProcessExec
from src.neuroanalyst.utils.constants import get_current_username, NeuroAnalystPaths

from datetime import datetime
import sys, os, argparse, time
from typing import Optional

from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
from rich import box
import typer, questionary

console = Console()
app = typer.Typer()

def main():
    console.print(f"Welcome {get_current_username()}!")
    console.rule("[bold red]Delete Pipeline[/bold red]")
    all_pipelines: list[NeuPipeline] = NeuPipeline.get_all_pipelines()
    pipeline_choices: dict[str, str] = {
        f"{pl.about.name} (ID: {pl.pipeline_id})": pl.pipeline_id for pl in all_pipelines
    }
    # Sort choices alphabetically
    pipeline_choices = dict(sorted(pipeline_choices.items(), key=lambda item: item[0].lower()))
    pipeline_selection: str = questionary.select(
        "Select a Pipeline to delete:",
        choices=list(pipeline_choices.keys())
    ).ask()
    pipeline_id: Optional[str] = pipeline_choices.get(pipeline_selection, None)
    if not pipeline_id:
        console.print("[red]Pipeline ID is required. Exiting.[/red]")
        return
    console.print(f"[bold green]Loaded Pipeline:[/bold green] {pipeline_selection}")
    # Display pipeline details
    pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id)
    console.print(Panel.fit(f"[bold blue]Pipeline Details:[/bold blue]\n{pipeline}"))

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