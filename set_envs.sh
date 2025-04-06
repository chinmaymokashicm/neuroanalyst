#!/bin/bash

# Create directories
mkdir -p $HOME/neuroanalyst/apptainer/images 
mkdir -p $HOME/neuroanalyst/apptainer/docs
mkdir -p $HOME/neuroanalyst/working_dirs
mkdir -p $HOME/neuroanalyst/reports

# Define the environment variables
ENV_VARS="
export NEUROANALYST_HOME=\$HOME/neuroanalyst
export NEUROANALYST_IMAGES=\$NEUROANALYST_HOME/apptainer/images
export NEUROANALYST_DOCS=\$NEUROANALYST_HOME/apptainer/docs
export NEUROANALYST_WORKDIR=\$NEUROANALYST_HOME/working_dirs
export NEUROANALYST_REPORTS=\$NEUROANALYST_HOME/reports
export NEUROANALYST_LOGS=\$NEUROANALYST_HOME/logs
"

# Function to check and add environment variable
add_env_var() {
    local var_name=$1
    local var_value=$2
    if ! grep -q "$var_name" ~/.bashrc; then
        echo "$var_value" >> ~/.bashrc
        echo "$var_name added to ~/.bashrc"
    else
        echo "$var_name already set in ~/.bashrc"
    fi
}

# Add each environment variable if not already set
add_env_var "NEUROANALYST_HOME" "export NEUROANALYST_HOME=\$HOME/neuroanalyst"
add_env_var "NEUROANALYST_IMAGES" "export NEUROANALYST_IMAGES=\$NEUROANALYST_HOME/apptainer/images"
add_env_var "NEUROANALYST_DOCS" "export NEUROANALYST_DOCS=\$NEUROANALYST_HOME/apptainer/docs"
add_env_var "NEUROANALYST_WORKDIR" "export NEUROANALYST_WORKDIR=\$NEUROANALYST_HOME/working_dirs"
add_env_var "NEUROANALYST_REPORTS" "export NEUROANALYST_REPORTS=\$NEUROANALYST_HOME/reports"
add_env_var "NEUROANALYST_LOGS" "export NEUROANALYST_LOGS=\$NEUROANALYST_HOME/logs"

source ~/.bashrc