"""
Test or dry run a Process before integrating it into a full Pipeline.
"""
from src.neuroanalyst.models.process.logic.core import ALLOWED_PYBIDS_ENTITY_KEYS
from src.neuroanalyst.models.process.process.core import NeuProcess
from src.neuroanalyst.models.process.exec.core import NeuProcessExec
from src.neuroanalyst.models.pipeline.core import NeuPipeline
from src.neuroanalyst.utils.constants import get_current_username
from src.neuroanalyst.models.pipeline.constructor import ProcessConstructorConfig

from pathlib import Path
import subprocess

import typer, questionary
from rich.console import Console
from rich.panel import Panel

TARGET_MODULE_PATH: str = "neuroanalyst.models.process.logic.core"

console = Console()
app = typer.Typer()

def main():
    console.rule("[bold blue]Test Process Function")
    console.print(f"Welcome {get_current_username()}!")
    
    # Ask for process ID
    process_id: str = questionary.text("Enter the Process ID to test:").ask()
    if not process_id:
        console.print("[red]Process ID is required. Exiting.[/red]")
        return
    process: NeuProcess = NeuProcess.from_process_id(process_id)
    console.print(Panel.fit(f"[bold green]Loaded Process:[/bold green] {process.logic.about.name} (ID: {process.process_id})"))
    
    # Check if process image is built
    if not process.is_image_built:
        console.print(f"[yellow]Process image not built. Building now...[/yellow]")
        build_image: bool = questionary.confirm(
            "Do you want to build the process image now?",
            default=True
        )
        if not build_image:
            console.print("[red]Process image is required to run the process. Exiting.[/red]")
            return
        process.build_singularity_image()
        console.print(f"[green]Process image built successfully.[/green]")
        
    # Create a temporary ProcessExec for testing
    process_constructor_config: ProcessConstructorConfig = ProcessConstructorConfig.initiate_from_process_id(process_id)
    
    # Ask for extra bind paths
    for container_path, _ in process_constructor_config.extra_bind_paths.items():
        host_path: str = questionary.text(
            f"Enter the host path to bind to container path '{container_path}':"
        ).ask()
        process_constructor_config.extra_bind_paths[container_path] = host_path
    
    # Ask for extra environment variables
    for env_var, _ in process_constructor_config.extra_environment_variables.items():
        env_value: str = questionary.text(
            f"Enter the value for environment variable '{env_var}':"
        ).ask()
        process_constructor_config.extra_environment_variables[env_var] = env_value
    
    # Choose sample pipeline details (for environment variables)
    sample_pipeline_id: str = questionary.text("Enter a sample Pipeline ID for testing (default: PL-000000):", default="PL-000000").ask()
    sample_pipeline_name: str = questionary.text("Enter a sample Pipeline Name for testing (default: Test Pipeline):", default="Test Pipeline").ask()
    
    # Ask for scheduler flags
    scheduler_flags: dict = {}
    while True:
        add_flag: bool = questionary.confirm("Do you want to add a scheduler flag?", default=False).ask()
        if not add_flag:
            break
        flag_name: str = questionary.text("Enter the scheduler flag name (e.g., --time):").ask()
        flag_value: str = questionary.text(f"Enter the value for {flag_name}:").ask()
        scheduler_flags[flag_name] = flag_value
    
    # Ask for BIDS root path
    bids_root: str = questionary.path(
        "Enter the BIDS root path for testing:",
        only_directories=True
        ).ask()
    
    # Ask for BIDS scope
    bids_scope: str = questionary.select(
        "Select the BIDS scope for testing:",
        choices=NeuPipeline.get_available_scopes(bids_root)
        ).ask()
    
    # Ask for BIDS filters (key-value pairs)
    available_entities: list[str] = ALLOWED_PYBIDS_ENTITY_KEYS.copy()
    while True:
        add_filter: bool = questionary.confirm("Do you want to add a BIDS filter?", default=False).ask()
        if not add_filter:
            break
        entity_key: str = questionary.select(
            "Select the BIDS entity key for the filter:",
            choices=available_entities
            ).ask()
        entity_value: str = questionary.text(f"Enter the value for entity '{entity_key}':").ask()
        process_constructor_config.input_bids_filters[entity_key] = entity_value
        # Remove selected entity from available choices
        available_entities.remove(entity_key)
        if not available_entities:
            break
    
    process_exec: NeuProcessExec = process_constructor_config.create_single_process_exec(
        scheduler_flags=scheduler_flags,
        bids_root=bids_root,
        bids_scope=bids_scope,
        sample_pipeline_id=sample_pipeline_id,
        sample_pipeline_name=sample_pipeline_name
    )
    console.print(Panel.fit(f"[bold green]Created Test Process Execution:[/bold green] ID: {process_exec.exec_id}"))
    exec_command: str = process_exec.exec_command
    console.print(f"[blue]Execution Command:[/blue]\n{exec_command}")
    # Confirm to run the process
    run_process: bool = questionary.confirm(
        "Do you want to run the test process execution now?",
        default=True
    ).ask()
    if not run_process:
        console.print("[yellow]Test process execution cancelled by user.[/yellow]")
        return
    console.print(f"[blue]Running test process execution...[/blue]")
    try:
        subprocess.run(exec_command, shell=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running process execution: {e}[/red]")
    
@app.command()
def start():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Process testing interrupted by user.[/red]")
        raise typer.Exit(code=130)
    except EOFError:
        console.print("\n[red]No input provided. Exiting.[/red]")
        raise typer.Exit(code=130)
    
if __name__ == "__main__":
    app()