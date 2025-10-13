#!/bin/bash

# Create directories
mkdir -p $HOME/neuroanalyst/apptainer/images
mkdir -p $HOME/neuroanalyst/process_execs
mkdir -p $HOME/neuroanalyst/apptainer/docs
mkdir -p $HOME/neuroanalyst/working_dirs
mkdir -p $HOME/neuroanalyst/pipelines
mkdir -p $HOME/neuroanalyst/reports
mkdir -p $HOME/neuroanalyst/logs
mkdir -p $HOME/neuroanalyst/datasets
mkdir -p $HOME/neuroanalyst/virtual_environments
mkdir -p $HOME/neuroanalyst/config

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
add_env_var "NEUROANALYST_PROCESS_EXECS" "export NEUROANALYST_PROCESS_EXECS=\$NEUROANALYST_HOME/process_execs"
add_env_var "NEUROANALYST_VENV" "export NEUROANALYST_VENV=\$NEUROANALYST_HOME/virtual_environments"
add_env_var "NEUROANALYST_DOCS" "export NEUROANALYST_DOCS=\$NEUROANALYST_HOME/apptainer/docs"
add_env_var "NEUROANALYST_WORKDIR" "export NEUROANALYST_WORKDIR=\$NEUROANALYST_HOME/working_dirs"
add_env_var "NEUROANALYST_PIPELINES" "export NEUROANALYST_PIPELINES=\$NEUROANALYST_HOME/pipelines"
add_env_var "NEUROANALYST_REPORTS" "export NEUROANALYST_REPORTS=\$NEUROANALYST_HOME/reports"
add_env_var "NEUROANALYST_LOGS" "export NEUROANALYST_LOGS=\$NEUROANALYST_HOME/logs"
add_env_var "NEUROANALYST_DATASETS" "export NEUROANALYST_DATASETS=\$NEUROANALYST_HOME/datasets"
add_env_var "NEUROANALYST_CONFIG" "export NEUROANALYST_CONFIG=\$NEUROANALYST_HOME/config"
add_env_var "NEUROANALYST_DB_HOST" "export NEUROANALYST_DB_HOST=localhost"
add_env_var "NEUROANALYST_DB_PORT" "export NEUROANALYST_DB_PORT=27017"
add_env_var "NEUROANALYST_DB_NAME" "export NEUROANALYST_DB_NAME=neuroanalyst"

source ~/.bashrc