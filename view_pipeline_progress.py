from src.neuroanalyst.models.pipeline.core import NeuPipelineStepStatus, ProcessStatus, NeuPipelineStatus
from src.neuroanalyst.models.pipeline import NeuPipeline

from datetime import datetime
import sys, os
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
    total = len(step.process_execs)
    completed = count_completed(step.process_execs)
    percent = (completed / total * 100) if total else 0

    table = Table.grid(expand=True)
    table.add_column(justify="left")
    table.add_column(justify="right")

    table.add_row(
        f"[bold]{step.name}[/bold] "
        f"[{status_color(step.status)}]({step.status.value})[/]",
        f"{completed}/{total} complete"
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
    proc_table.add_column("Scheduler Job")
    proc_table.add_column("Started At")
    proc_table.add_column("Completed At")
    proc_table.add_column("Duration")

    for p in step.process_execs:
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
            p.scheduler_job_id or "-",
            started_at.strftime("%Y-%m-%d %H:%M:%S") if started_at else "-",
            completed_at.strftime("%Y-%m-%d %H:%M:%S") if completed_at else "-",
            prettify_duration(duration),
        )

    content_grid = Table.grid()
    content_grid.add_row(table)
    content_grid.add_row(bar)
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
    """
    fetch_status_fn: () -> NeuPipelineStatus
    """
    console = Console(force_terminal=True)

    with Live(console=console, refresh_per_second=4, screen=True) as live:
        while True:
            status = fetch_status_fn()
            live.update(render_pipeline(status))

            if status.status in {ProcessStatus.COMPLETE, ProcessStatus.FAILED}:
                break

            time.sleep(refresh_sec)


if __name__ == "__main__":

    pipeline_id: str = str(sys.argv[1])
    username: str = str(sys.argv[2])
    os.environ["USERNAME"] = username
    pipeline: NeuPipeline = NeuPipeline.from_pipeline_id(pipeline_id, username=username)

    def fetch_status():
        return pipeline.get_pipeline_status()

    live_pipeline_view(fetch_status)