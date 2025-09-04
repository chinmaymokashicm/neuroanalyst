"""
NeuProcess Module

This module defines the NeuProcess class, which is responsible for:
1. Creating and managing neuroimaging process metadata
2. Building Singularity/Apptainer images from NeuProcessDir instances
3. Creating virtual environments for script-based execution
"""

from .core import NeuProcess

__all__ = ['NeuProcess']
