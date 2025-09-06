"""
NeuProcess Package

This package contains modules related to neuroimaging process creation,
configuration, and execution.

The main components are:
- NeuProcessLogic: Abstract representation of process logic
- NeuProcessDir: Directory structure for a process
- NeuProcess: Process container and image builder
- NeuProcessExec: Execution instance of a process
"""

# Import main classes for easier access
from .logic.core import NeuProcessLogic, NeuProcessKind, ProgrammingLanguage
from .dir.core import NeuProcessDir, ExecutionMode
from .process.core import NeuProcess
from .exec.core import NeuProcessExec, HPCScheduler
from .wrapper.core import neuprocess_decorator

__all__ = [
    "NeuProcessLogic",
    "NeuProcessKind",
    "ProgrammingLanguage",
    "NeuProcessDir",
    "ExecutionMode",
    "NeuProcess",
    "NeuProcessExec",
    "HPCScheduler",
    "neuprocess"
]
