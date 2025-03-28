#!/bin/bash

venv_name=$1

pyenv shell $venv_name

pip install pydantic rich

pip install ipython ipykernel ipywidgets pymongo "fastapi[standard]"

# pip install pybids nibabel nilearn matplotlib pandas

pip install "celery[redis]" textual-dev textual[syntax] "pydantic-ai[logfire,examples]"
pip install --upgrade httpx==0.27.1

pip freeze > requirements.txt