#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, '.')

from app.models.about import About
from app.models.process.logic.core import NeuProcessLogic, ProgrammingLanguage
from app.models.process.dir.core import NeuProcessDir, NeuProcessDirConfig

# Create a simple example
about = About(name='demo', description='Demo process', version='1.0.0', author='Demo Author', tag='demo')
logic = NeuProcessLogic(about=about, language=ProgrammingLanguage.PYTHON, code='def demo(): pass')
config = NeuProcessDirConfig()
neuprocess_dir = NeuProcessDir(logic=logic, config=config)

# Create in test_output directory
output_dir = Path('./test_output/demo_with_model')
output_dir.mkdir(parents=True, exist_ok=True)
created_dir = neuprocess_dir.create_directory(output_dir)
print(f'Created demo directory at: {created_dir}')
