"""
Delete a process.
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
from src.neuroanalyst.models.process.exec.core import NeuProcessExec
from src.neuroanalyst.models.process.logic.core import NeuProcessLogic

from pathlib import Path
from typing import Optional

import typer, questionary
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer()

def main():
    console.print(f"Welcome {get_current_username()}!")
    console.rule("[bold red]Delete Process[/bold red]")
    all_processes: list[NeuProcessDir] = NeuProcessDir.get_all_process_dirs()
    process_choices: dict[str, str] = {
        f"{proc.logic.about.name} (ID: {proc.process_id})": proc.process_id for proc in all_processes
    }
    # Sort choices alphabetically
    process_choices = dict(sorted(process_choices.items(), key=lambda item: item[0].lower()))
    process_selection: str = questionary.select(
        "Select a Process to delete:",
        choices=list(process_choices.keys())
    ).ask()
    process_id: Optional[str] = process_choices.get(process_selection, None)
    if not process_id:
        console.print("[red]Process ID is required. Exiting.[/red]")
        return
    process: NeuProcessDir = NeuProcessDir.from_process_id(process_id)
    console.print(Panel.fit(f"[bold green]Loaded Process:[/bold green] {process.logic.about.name} (ID: {process.process_id})"))
    ask_details: bool = questionary.confirm(
        "Do you want to see process details before deletion?",
        default=True
    ).ask()
    if ask_details:
        console.print(process.logic)
        console.print(process.logic.code)
    confirm_delete: bool = questionary.confirm(
        f"Are you sure you want to DELETE process '{process.logic.about.name}' (ID: {process.process_id})? This action cannot be undone.",
        default=False
    ).ask()
    if not confirm_delete:
        console.print("[yellow]Process deletion cancelled by user.[/yellow]")
        return
    try:
        process.delete()
        # Delete process image
        paths = NeuroAnalystPaths()
        image_path: Path = paths.get_process_image_path(process.process_id)
        if image_path.exists():
            image_path.unlink()
    except Exception as e:
        console.print(f"[red]Error deleting process: {e}[/red]")
        return
    console.print(f"[green]Process '{process.logic.about.name}' (ID: {process.process_id}) deleted successfully.[/green]")
    
    # Ask to delete associated process execs as well
    confirm_delete_execs: bool = questionary.confirm(
        f"Do you also want to delete all associated ProcessExec instances for process ID '{process.process_id}'?",
        default=False
    ).ask()
    if confirm_delete_execs:
        all_execs: list[NeuProcessExec] = NeuProcessExec.get_by_process_id(process.process_id)
        for exec_instance in all_execs:
            try:
                exec_instance.delete()
            except Exception as e:
                console.print(f"[red]Error deleting ProcessExec ID '{exec_instance.exec_id}': {e}[/red]")
        console.print(f"[green]All associated ProcessExec instances for process ID '{process.process_id}' deleted successfully.[/green]")

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