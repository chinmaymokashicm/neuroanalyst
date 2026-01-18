"""
View pipeline progress and results.
"""
from src.neuroanalyst.models.pipeline.core import NeuPipelineStepStatus, ProcessStatus, NeuPipelineStatus
from src.neuroanalyst.models.pipeline import NeuPipeline
from src.neuroanalyst.models.process.exec.core import NeuProcessExec

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

def count_completed(processes):
    return sum(p.status == ProcessStatus.COMPLETE for p in processes)

def status_color(status: ProcessStatus) -> str:
    return {
        ProcessStatus.NOT_STARTED: "grey50",
        ProcessStatus.RUNNING: "cyan",
        ProcessStatus.COMPLETE: "green",
        ProcessStatus.FAILED: "red",
    }.get(status, "white")

def prettify_duration(duration: datetime) -> str:
    """
    Convert a duration (timedelta) into a human-readable string.
    
    Args:
        duration (datetime): Duration to prettify.
        
    Returns:
        str: Human-readable duration string.
    """
    if duration is None:
        return "-"
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return ' '.join(parts)


def render_step(step: NeuPipelineStepStatus) -> Panel:
    show_all = os.environ.get("VERBOSE", "false").lower() == "true"
    show_details = show_all or step.status in {
        ProcessStatus.RUNNING,
        ProcessStatus.FAILED,
    }
    
    total = len(step.processes)
    completed = count_completed(step.processes)
    percent = (completed / total * 100) if total else 0
    step_started_at: datetime = datetime.fromisoformat(step.started_at.replace('Z', '+00:00')) if step.started_at else None
    step_completed_at: datetime = datetime.fromisoformat(step.completed_at.replace('Z', '+00:00')) if step.completed_at else None
    step_duration = (step_completed_at - step_started_at) if step_started_at and step_completed_at else None

    table = Table.grid(expand=True)
    table.add_column(justify="left")
    table.add_column(justify="right")

    duration_str = f" | Duration: [bold]{prettify_duration(step_duration)}[/bold]" if step_duration else ""
    
    table.add_row(
        f"[bold]{step.name}[/bold] "
        f"[{status_color(step.status)}]({step.status.value})[/]",
        f"{completed}/{total} complete{duration_str}"
    )

    bar = Progress(
        BarColumn(bar_width=None),
        TextColumn("{task.percentage:>5.1f}%"),
        expand=True,
    )
    task = bar.add_task("", total=total, completed=completed)

    # Filter processes to display
    processes_to_show = step.processes
    hidden_count = 0
    
    MAX_DISPLAY = 20
    if total >= MAX_DISPLAY and not show_all:
        # Sort all processes by this order: FAILED, RUNNING, COMPLETE, NOT_STARTED
        status_priority = {
            ProcessStatus.FAILED: 0,
            ProcessStatus.RUNNING: 1,
            ProcessStatus.COMPLETE: 2,
            ProcessStatus.NOT_STARTED: 3,
        }
        sorted_processes = sorted(
            step.processes,
            key=lambda p: status_priority.get(p.status, 4)  # Default to lowest priority
        )
        
        processes_to_show = sorted_processes[:MAX_DISPLAY]
        hidden_count = total - MAX_DISPLAY

    proc_table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold",
    )
    proc_table.add_column("Exec ID")
    proc_table.add_column("Status")
    proc_table.add_column("BIDS Filters")
    proc_table.add_column("Scheduler Job")
    proc_table.add_column("Started At")
    proc_table.add_column("Completed At")
    proc_table.add_column("Duration")

    for p in processes_to_show:
        process_exec: NeuProcessExec = NeuProcessExec.from_exec_id(p.exec_id)
        bids_filters: dict = process_exec.bids_filters
        started_at: datetime = datetime.fromisoformat(p.started_at.replace('Z', '+00:00')) if p.started_at else None
        completed_at: datetime = datetime.fromisoformat(p.completed_at.replace('Z', '+00:00')) if p.completed_at else None
        duration = (completed_at - started_at) if started_at and completed_at else None
        
        icon = {
            ProcessStatus.COMPLETE: "✔",
            ProcessStatus.RUNNING: "▶",
            ProcessStatus.FAILED: "✖",
            ProcessStatus.NOT_STARTED: "•",
        }.get(p.status, "?")

        proc_table.add_row(
            p.exec_id,
            f"[{status_color(p.status)}]{icon} {p.status.value}[/]",
            ", ".join(f"{k}={v}" for k, v in bids_filters.items()) if bids_filters else "-",
            p.scheduler_job_id or "-",
            started_at.strftime("%Y-%m-%d %H:%M:%S") if started_at else "-",
            completed_at.strftime("%Y-%m-%d %H:%M:%S") if completed_at else "-",
            prettify_duration(duration),
        )

    # Add notice about hidden processes
    if hidden_count > 0:
        proc_table.add_row(
            f"[dim]... {hidden_count} more process(es) hidden[/dim]",
            "", "", "", "", "", ""
        )

    content_grid = Table.grid()
    content_grid.add_row(table)
    content_grid.add_row(bar)
    
    if show_details:
        content_grid.add_row(proc_table)

    return Panel(
        content_grid,
        border_style=status_color(step.status),
    )


def render_pipeline(status: NeuPipelineStatus) -> Panel:
    overall_pct = status.get_completion_percentage()
    
    pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(
        pipeline_id=status.pipeline_id,
    )
    pipeline_name: str = pipeline.about.name

    header = Table.grid(expand=True)
    header.add_column(justify="left")
    header.add_column(justify="right")

    header.add_row(
        f"[bold]Pipeline {status.pipeline_id} {pipeline_name} [/bold] "
        f"[{status_color(status.status)}]({status.status.value})[/]",
        f"Scheduler: {status.scheduler}"
    )
    header.add_row(
        f"Updated: {status.last_updated}",
        f"{overall_pct:.1f}% complete"
    )

    steps = Table.grid(expand=True)
    for step in status.steps:
        steps.add_row(render_step(step))

    main_grid = Table.grid()
    main_grid.add_row(header)
    main_grid.add_row(steps)

    return Panel(
        main_grid,
        border_style=status_color(status.status),
    )


def live_pipeline_view(fetch_status_fn, refresh_sec: float = 2.0):
    console = Console(force_terminal=True)

    final_status: NeuPipelineStatus | None = None

    with Live(console=console, refresh_per_second=4, screen=True) as live:
        while True:
            status = fetch_status_fn()
            final_status = status
            live.update(render_pipeline(status))

            if status.status in {
                ProcessStatus.COMPLETE,
                ProcessStatus.FAILED,
            }:
                break

            time.sleep(refresh_sec)

    # IMPORTANT: after Live exits, explicitly render final state
    if final_status is not None:
        console.print(render_pipeline(final_status))
    
    console.print(
    Panel.fit(
        f"[bold green]Pipeline completed successfully[/bold green]"
        if final_status.status == ProcessStatus.COMPLETE
        else "[bold red]Pipeline failed[/bold red]",
        border_style=status_color(final_status.status),
        )
    )
    
if __name__ == "__main__":
    # Get all pipelines and their names and their statuses
    all_pipelines: list[NeuPipeline] = NeuPipeline.get_all_pipelines()
    pipeline_choices: dict[str, str] = {
        f"{pl.about.name} (ID: {pl.pipeline_id}) (Status: {pl.get_pipeline_status().status.value}) (Created at: {datetime.fromisoformat(pl.get_pipeline_status().created_at)})": pl.pipeline_id for pl in all_pipelines
    }
    # Sort choices alphabetically
    pipeline_choices = dict(sorted(pipeline_choices.items(), key=lambda item: item[0].lower()))
    
    selected_pipeline: str = questionary.select(
        "Select a Pipeline to view:",
        choices=list(pipeline_choices.keys())
    ).ask()
    pipeline_id: Optional[str] = pipeline_choices.get(selected_pipeline, None)
    if not pipeline_id:
        console.print("[red]Pipeline ID is required. Exiting.[/red]")
        sys.exit(1)
        
    # Ask if user wants verbose mode
    verbose_mode: bool = questionary.confirm(
        "Do you want to enable verbose mode (show all processes)?",
        default=False
    ).ask()
    if verbose_mode:
        os.environ["VERBOSE"] = "true"
    else:
        os.environ["VERBOSE"] = "false"
    
    pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id)
    
    def fetch_status():
        return pipeline.get_pipeline_status()
    
    live_pipeline_view(fetch_status)