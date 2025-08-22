"""
Wrapper module for NeuProcessLogic decorators and related functionality.
"""

from .core import (
    neuprocess_decorator,
    NeuProcessDecoratorConfig,
    NeuProcessOutput,
    NeuProcessResult,
    create_neuprocess_function,
)

# Convenient alias for the decorator
neuprocess = neuprocess_decorator

__all__ = [
    "neuprocess_decorator",
    "neuprocess",
    "NeuProcessDecoratorConfig", 
    "NeuProcessOutput",
    "NeuProcessResult",
    "create_neuprocess_function",
]
