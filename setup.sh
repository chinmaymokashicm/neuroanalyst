#!/bin/bash

# ==============================================================================
# Set up the Python environment
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

# ==============================================================================
# Set up the React environment

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed, please install it first."
    return
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is not installed, please install it first."
    return
fi

# Check if npx is installed
if ! command -v npx &> /dev/null; then
    echo "npx is not installed, please install it first."
    return
fi

# Install React dependencies
mkdir -p lib/frontend
cd lib/frontend

# Run the following only if package.json does not exist
if [ ! -f "package.json" ]; then
    npx create-react-app .
fi
npm install axios react-router-dom react-table @mui/material @emotion/react @emotion/styled react-json-view react-flow-renderer

cd ../../