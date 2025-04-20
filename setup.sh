#!/bin/bash

# ==============================================================================
# Set up the Python environment
python_version=3.12
venv_name=venv

# Create the virtual environment using venv
if [ -d "$venv_name" ]; then
    echo "Virtual environment $venv_name already exists. Skipping creation."
else
    echo "Creating virtual environment: $venv_name..."
    python -m venv "$venv_name"
    echo "Virtual environment $venv_name created."
fi

# Activate the virtual environment
source "$venv_name/bin/activate"
echo "Virtual environment $venv_name activated."

# Install required packages
echo "Installing required packages..."
# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing packages from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping package installation."
    # Run the install_requirements.sh script if it exists
    if [ -f "install_requirements.sh" ]; then
        echo "Running install_requirements.sh..."
        bash install_requirements.sh "$venv_name"
    else
        echo "install_requirements.sh not found. Skipping."
    fi
fi
echo "Required packages installed."

# Set environment variables
source set_envs.sh