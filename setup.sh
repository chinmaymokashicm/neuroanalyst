#!/bin/bash

python_version=3.12
venv_name=neuroanalyst

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "pyenv is not installed, please install it first. Also, install pyenv-virtualenv after installing pyenv."
    return
fi

# Check if pyenv-virtualenv is installed
if ! command -v pyenv-virtualenv &> /dev/null; then
    echo "pyenv-virtualenv is not installed, please install it first."
    return
fi

# Set the Python version for the current shell session
pyenv install $python_version -s

# Create and activate virtual environment
pyenv virtualenv $python_version $venv_name
pyenv shell $venv_name
pyenv local $venv_name
echo "Virtual environment name: $venv_name created"

# source $venv_name/bin/activate
echo "Virtual environment $venv_name activated"

# Install requirements
# pip install -r requirements.txt
source install_requirements.sh $venv_name