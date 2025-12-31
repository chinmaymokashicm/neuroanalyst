from src.neuroanalyst.models.pipeline.core import NeuPipelineStepStatus, ProcessStatus, NeuPipelineStatus
from src.neuroanalyst.models.pipeline import NeuPipeline
from src.neuroanalyst.models.process.exec.core import NeuProcessExec

from datetime import datetime
import sys, os, argparse
import time

from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.console import Console
from rich import box

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

    duration_str = f" Duration - {prettify_duration(step_duration)}" if step_duration else ""
    
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

    for p in step.processes:
        process_exec: NeuProcessExec = NeuProcessExec.from_exec_id(p.exec_id, username=os.environ.get("USERNAME", None))
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
        username=os.environ.get("USERNAME", None)
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
        title=f"user: {status.username}",
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
    parser = argparse.ArgumentParser(
        description="Live pipeline progress viewer"
    )

    parser.add_argument(
        "-p",
        "--pipeline-id",
        required=True,
        help="Pipeline ID to monitor",
    )

    parser.add_argument(
        "-u",
        "--username",
        required=False,
        default=None,
        help="Username that owns the pipeline",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show all process execution details for all steps",
    )

    args = parser.parse_args()

    os.environ["USERNAME"] = args.username
    os.environ["VERBOSE"] = str(args.verbose)

    pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(
        pipeline_id=args.pipeline_id,
        username=args.username,
    )

    def fetch_status():
        return pipeline.get_pipeline_status()

    live_pipeline_view(fetch_status)