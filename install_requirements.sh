#!/bin/bash

venv_name=$1

pyenv shell $venv_name

pip install pydantic rich

pip install ipython ipykernel ipywidgets

pip install pybids

pip freeze > requirements.txt