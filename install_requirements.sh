#!/bin/bash

venv_name=$1

pyenv shell $venv_name

pip install pydantic rich

pip install ipython ipykernel ipywidgets pymongo "fastapi[standard]"

# pip install pybids nibabel nilearn matplotlib pandas

pip freeze > requirements.txt