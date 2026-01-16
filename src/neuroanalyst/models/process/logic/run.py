"""
Test or dry run a function or a Logic before registering and without integrating it into a full Process or Pipeline.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[5] / "src"
sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
console = Console()
console.print(f"[dim]Using PYTHONPATH root: {PROJECT_ROOT}[/dim]")

import src.neuroanalyst.models.process.logic.core as core_module
from src.neuroanalyst.models.process.wrapper.core import _write_output_data
from src.neuroanalyst.models.process.logic.code.python.decoder import PythonFunctionExtractor
from src.neuroanalyst.utils.constants import get_current_username

from unittest.mock import patch
import os, importlib, sys, ast, inspect, traceback
from contextlib import contextmanager
import tempfile

import typer, questionary
from rich.panel import Panel

TARGET_MODULE_PATH: str = "neuroanalyst.models.process.logic.core"

@contextmanager
def emulate_container_mounts(mounts: dict[Path, Path]):
    """
    Emulate container bind mounts by rewriting Path operations.

    mounts:
        {
            Path("/data"): Path("/host/data"),
            Path("/scratch"): Path("/tmp/scratch")
        }
    """
    mounts = {
        Path(container).resolve(): Path(host).resolve()
        for container, host in mounts.items()
    }

    def resolve(self: Path) -> Path:
        self = self.resolve()
        for container_root, host_root in mounts.items():
            try:
                rel = self.relative_to(container_root)
                return host_root / rel
            except ValueError:
                continue
        return self

    # Save originals
    originals = {
        "exists": Path.exists,
        "is_file": Path.is_file,
        "is_dir": Path.is_dir,
        "mkdir": Path.mkdir,
        "open": Path.open,
        "iterdir": Path.iterdir,
    }

    # Patch methods
    Path.exists  = lambda self: originals["exists"](resolve(self))
    Path.is_file = lambda self: originals["is_file"](resolve(self))
    Path.is_dir  = lambda self: originals["is_dir"](resolve(self))
    Path.mkdir   = lambda self, *a, **k: originals["mkdir"](resolve(self), *a, **k)
    Path.open    = lambda self, *a, **k: originals["open"](resolve(self), *a, **k)
    Path.iterdir = lambda self: originals["iterdir"](resolve(self))

    try:
        yield
    finally:
        for name, fn in originals.items():
            setattr(Path, name, fn)

app = typer.Typer()

_real_mkdir = Path.mkdir

def redirected_mkdir(self, temp_dir: str | Path, *args, **kwargs):
    if str(self).startswith("/data"):
        redirected = Path(temp_dir) / self.relative_to("/data")
        return _real_mkdir(redirected, *args, **kwargs)
    return _real_mkdir(self, *args, **kwargs)

def load_function(module_path: str | Path, function_name: str) -> callable:
    """
    Dynamically load a function from a path.
    """
    module_path = Path(module_path).resolve() # Ensure absolute path
    module_name = module_path.stem
    
    spec: importlib.machinery.ModuleSpec = importlib.util.spec_from_file_location(module_name, str(module_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from path: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    function = getattr(module, function_name)
    return function

def get_env_vars(function: callable) -> list[str]:
    """
    Extract environment variable names used in the function.
    """
    source = inspect.getsource(function)
    tree = ast.parse(source, type_comments=True)
    extractor = PythonFunctionExtractor()
    extractor.visit(tree)
    if extractor.functions:
        return list(extractor.functions[0].get("env_vars", []))
    return []

def collect_mounts() -> dict[Path, Path]:
    mounts = {}

    console.print("\n[bold]Configure container mounts[/bold]")
    console.print("Example: /data -> /home/user/mydata")

    while True:
        container_path = questionary.text(
            "Container path (e.g. /data, /scratch). Leave empty to finish:"
        ).ask()

        if not container_path:
            break

        host_path = questionary.path(
            f"Host path to bind to {container_path}:"
        ).ask()

        mounts[Path(container_path)] = Path(host_path)

    return mounts

def main():
    console.rule("[bold blue]Test Logic Function")
    console.print(f"Welcome {get_current_username()}!")
    
    module_path: str = questionary.text("Enter the path to the Python module containing the function:").ask()
    function_name: str = questionary.text("Enter the function name to test:").ask()
    
    if not module_path:
        console.print("[red]Module path is required.[/red]")
        return
    
    try:
        function: callable = load_function(module_path, function_name)
    except Exception as e:
        console.print(f"[red]Error loading function: {e}[/red]")
        return
    
    env_vars: list[str] = get_env_vars(function)
    console.print(Panel.fit(f"[bold green]Function '{function_name}' loaded successfully![/bold green]\n\n[bold]Environment Variables Required:[/bold] {env_vars}"))
    
    # Ask values for environment variables
    mock_env: dict = {}
    for var in env_vars:
        value: str = questionary.text(f"Enter value for environment variable '{var}':").ask()
        if value is not None:
            mock_env[var] = value
    
    samples_path: Path = Path(__file__).resolve().parents[2] / "src" / "neuroanalyst" / "models" / "process" / "logic" / "code" / "python" / "samples" / "autorecon1.py"
    
    input_filepath: str = questionary.path(
        message="Enter the path to the input file for the function:",
        # default=str(samples_path / "sub-01_T1w.nii.gz")
    ).ask()
    
    data_root: str = questionary.path(
        message="Enter the host path to use as /data:"
    ).ask()

    with patch.dict(sys.modules, {TARGET_MODULE_PATH: core_module}):
        with patch.dict(os.environ, mock_env):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Emulate container mounts
                mounts = {Path("/data"): Path(data_root)}
                with emulate_container_mounts(mounts):
                    # Redirect mkdir calls to temp dir
                    with patch.object(Path, "mkdir", new=redirected_mkdir):
                        try:
                            output = function(input_filepath)
                            if output is None:
                                console.print("[yellow]Function returned None. No output to display.[/yellow]")
                                return
                            output_data, metrics, output_entities, forced_outputs = output
                            
                            console.print(Panel.fit(f"[bold green]Function executed successfully![/bold green]\n\n[bold]Metrics:[/bold] {metrics}\n\n[bold]Output Entities:[/bold] {output_entities}\n\n[bold]Forced Outputs:[/bold] {forced_outputs}"))
                            
                            # Optionally write output data to temp dir
                            save_output: bool = questionary.confirm(
                                "Do you want to save the output data to a temporary directory?",
                                default=True
                            ).ask()
                            if save_output:
                                output_path: str = _write_output_data(
                                    output_data,
                                    temp_dir,
                                    "output_data"
                                )
                                console.print(f"[green]Output data saved to: {output_path}[/green]")
                        except Exception as e:
                            console.print(f"[red]Error during function execution: {e}[/red]")
                            console.print(traceback.format_exc())
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