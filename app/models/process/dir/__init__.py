"""
NeuProcessDir module for wrapping NeuProcessLogic into directory structure.

This module creates a complete directory structure with scripts for parallel execution
of NeuProcessLogic functions using PyBIDS for BIDS dataset iteration.
"""

from .core import (
    NeuProcessDir,
    NeuProcessDirConfig,
    create_neuprocess_directory
)

__all__ = [
    "NeuProcessDir", 
    "NeuProcessDirConfig",
    "create_neuprocess_directory"
]
