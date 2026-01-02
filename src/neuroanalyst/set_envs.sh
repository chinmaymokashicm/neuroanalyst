#!/bin/bash

# Create directories
mkdir -p $HOME/neuroanalyst

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

source ~/.bashrc