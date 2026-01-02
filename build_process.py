"""
Build an image or a virtual environment of a created process directory.
"""
from src.neuroanalyst.models.process.process.core import NeuProcess

import sys

process_id: str = sys.argv[1]

process: NeuProcess = NeuProcess.from_process_id(
    process_id=process_id
)

process.build_singularity_image()