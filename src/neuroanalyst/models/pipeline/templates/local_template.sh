#!/bin/bash
#
# NeuPipeline Local Execution Template
#
# This template is used to generate the local execution script for a NeuPipeline.
# Variables in double curly braces will be replaced with actual values.
#

# Error handling
set -e

# Log functions
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "{{log_dir}}/pipeline.log"
}

# Execute the command
log "Starting execution: {{step_name}}"
{{command}}
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  log "Execution completed successfully: {{step_name}}"
else
  log "Execution failed with exit code $EXIT_CODE: {{step_name}}"
  exit $EXIT_CODE
fi
