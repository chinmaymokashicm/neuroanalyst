#!/bin/bash

venv_name=$1

source $venv_name/bin/activate

pip install pydantic rich pyperclip python-dotenv

pip install ipython ipykernel ipywidgets pymongo "fastapi[standard]"

pip install pybids nibabel nilearn matplotlib pandas

# pip install "celery[redis]" textual-dev textual[syntax] tree-sitter-languages "pydantic-ai[logfire,examples]"
pip install "celery[redis]" textual-dev textual[syntax] "pydantic-ai[logfire,examples]"

# pip uninstall tzdata protobuf
# pip install tzdata==2025.1
# pip install protobuf>=5.0,<6.0

pip install git+https://github.com/chinmaymokashicm/neurolib.git

pip install --upgrade httpx==0.27.1

pip freeze > requirements.txt

# pip install -r requirements.txt