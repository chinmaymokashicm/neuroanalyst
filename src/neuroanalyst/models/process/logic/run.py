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
from src.neuroanalyst.models.process.logic.code.python.decoder import PythonFunctionExtractor
from src.neuroanalyst.utils.constants import get_current_username

from unittest.mock import patch
import os, importlib, sys, ast, inspect
from contextlib import contextmanager
import tempfile

import typer, questionary
from rich.panel import Panel

TARGET_MODULE_PATH: str = "neuroanalyst.models.process.logic.core"

@contextmanager
def emulate_container_data_mount(data_root: Path):
    """
    Emulate a container /data mount by mapping /data paths
    to a host directory.
    """
    data_root = Path(data_root).resolve()

    # Save originals
    _orig_exists = Path.exists
    _orig_is_file = Path.is_file
    _orig_is_dir = Path.is_dir
    _orig_mkdir = Path.mkdir
    _orig_open = Path.open
    _orig_iterdir = Path.iterdir

    def resolve(self: Path) -> Path:
        if str(self).startswith("/data"):
            return data_root / self.relative_to("/data")
        return self

    def patched_exists(self):
        return _orig_exists(resolve(self))

    def patched_is_file(self):
        return _orig_is_file(resolve(self))

    def patched_is_dir(self):
        return _orig_is_dir(resolve(self))

    def patched_mkdir(self, *args, **kwargs):
        return _orig_mkdir(resolve(self), *args, **kwargs)

    def patched_open(self, *args, **kwargs):
        return _orig_open(resolve(self), *args, **kwargs)

    def patched_iterdir(self):
        return _orig_iterdir(resolve(self))

    try:
        Path.exists = patched_exists
        Path.is_file = patched_is_file
        Path.is_dir = patched_is_dir
        Path.mkdir = patched_mkdir
        Path.open = patched_open
        Path.iterdir = patched_iterdir
        yield
    finally:
        Path.exists = _orig_exists
        Path.is_file = _orig_is_file
        Path.is_dir = _orig_is_dir
        Path.mkdir = _orig_mkdir
        Path.open = _orig_open
        Path.iterdir = _orig_iterdir

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
            with emulate_container_data_mount(Path(data_root)):
                console.print("[bold blue]Running the function...[/bold blue]")
                result = function(input_filepath)
                try:
                    console.print(f"[dim]Listdir in '/data': {os.listdir('/data')}[/dim]")
                    result = function(input_filepath)
                    console.print(Panel.fit(f"[bold green]Function executed successfully![/bold green]\n\n[bold]Result:[/bold] {result}"))
                except Exception as e:
                    console.print(f"[red]Error executing function: {e}[/red]")
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