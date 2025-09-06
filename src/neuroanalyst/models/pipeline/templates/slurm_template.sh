#!/bin/bash
#
# NeuPipeline SLURM Template
#
# This template is used to generate the SLURM scheduler script for a NeuPipeline.
# Variables in double curly braces will be replaced with actual values.
#

# SLURM job settings
#SBATCH --job-name={{pipeline_id}}_{{step_name}}
#SBATCH --output={{log_dir}}/{{step_name}}.%j.out
#SBATCH --error={{log_dir}}/{{step_name}}.%j.err
{{#dependencies}}
#SBATCH --dependency=afterok:{{dependencies}}
{{/dependencies}}

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
