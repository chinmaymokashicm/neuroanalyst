#!/bin/bash
# ===== PIPELINE SCRIPT =====
# This script executes a pipeline of NeuProcess executions.
# It uses pre-generated execution commands stored in the model.json file,
# eliminating the need to reconstruct complex commands with bind paths and env vars.
# The script uses scheduler information from model.json to determine the appropriate
# scheduler commands and job status checking methods for each process.

# ===== ENVIRONMENT SETUP =====
# Load environment variables if they exist
[ -f "${HOME}/.neuroanalyst/env.sh" ] && source "${HOME}/.neuroanalyst/env.sh"

# ===== PIPELINE VARIABLES =====
PIPELINE_ID="PL_ID_PLACEHOLDER"
PIPELINE_DIR="PL_DIR_PLACEHOLDER"
MODEL_FILE="${PIPELINE_DIR}/model.json"
STATUS_FILE="${PIPELINE_DIR}/status.json"

# ===== LOG DIRECTORY SETUP =====
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ -n "${NEUROANALYST_LOGS}" ]; then
  LOG_BASE="${NEUROANALYST_LOGS}"
else
  LOG_BASE="${HOME}/.neuroanalyst/logs"
fi
LOG_DIR="${LOG_BASE}/pipelines/${PIPELINE_ID}/${TIMESTAMP}"
mkdir -p "${LOG_DIR}"

# ===== UTILITY FUNCTIONS =====

# Function to log messages with timestamp
log() {
  local message="$1"
  local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
  echo "[${timestamp}] ${message}" | tee -a "${LOG_DIR}/pipeline.log"
}

# Function to extract error messages from log files
extract_error() {
  local log_file="$1"
  local lines=10
  
  if [ -f "$log_file" ]; then
    # Return the last few lines that might contain error information
    tail -n $lines "$log_file"
  else
    echo "Log file not found: $log_file"
  fi
}

# ===== STATUS MANAGEMENT FUNCTIONS =====

# Initialize status file if it doesn't exist
initialize_status_file() {
  if [ ! -f "$STATUS_FILE" ]; then
    log "Creating status file: $STATUS_FILE"
    cat > "$STATUS_FILE" << EOF
{
  "pipeline_id": "${PIPELINE_ID}",
  "status": "initialized",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "last_updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "steps": []
}
EOF
  fi
}

# Update status of a specific process
update_process_status() {
  local step_idx="$1"
  local proc_idx="$2"
  local status="$3"
  local job_id="$4"
  local error_msg="$5"
  
  if command -v jq &> /dev/null; then
    # Prepare job_id and error_msg fields
    local job_id_str=""
    local error_msg_str=""
    local scheduler_str=""
    
    if [ -n "$job_id" ]; then
      job_id_str=", \"scheduler_job_id\": \"$job_id\""
      
      # If job ID is provided, also get scheduler type from model.json
      if [ -f "$MODEL_FILE" ]; then
        local scheduler=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].scheduler" "$MODEL_FILE" 2>/dev/null)
        if [ -n "$scheduler" ] && [ "$scheduler" != "null" ]; then
          scheduler_str=", \"scheduler\": \"$scheduler\""
        fi
      fi
    fi
    
    if [ -n "$error_msg" ]; then
      # Escape quotes in error message
      error_msg=$(echo "$error_msg" | sed 's/"/\\"/g')
      error_msg_str=", \"error\": \"$error_msg\""
    fi
    
    # Update the status
    jq ".steps[$step_idx].process_execs[$proc_idx].status = \"$status\" | 
        .steps[$step_idx].process_execs[$proc_idx].last_updated = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"
        $job_id_str $scheduler_str $error_msg_str" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
    mv "${STATUS_FILE}.tmp" "$STATUS_FILE"
    
    # Check if all processes in this step are complete or failed
    local all_complete=true
    local any_failed=false
    local num_processes=$(jq ".steps[$step_idx].process_execs | length" "$STATUS_FILE")
    
    for ((i=0; i<num_processes; i++)); do
      local proc_status=$(jq -r ".steps[$step_idx].process_execs[$i].status" "$STATUS_FILE")
      if [ "$proc_status" != "COMPLETE" ] && [ "$proc_status" != "FAILED" ]; then
        all_complete=false
      fi
      if [ "$proc_status" = "FAILED" ]; then
        any_failed=true
      fi
    done
    
    # Update step status if all processes are complete or any failed
    if $all_complete; then
      if $any_failed; then
        jq ".steps[$step_idx].status = \"FAILED\" | 
            .steps[$step_idx].last_updated = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
      else
        jq ".steps[$step_idx].status = \"COMPLETE\" | 
            .steps[$step_idx].last_updated = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
      fi
      mv "${STATUS_FILE}.tmp" "$STATUS_FILE"
    fi
  else
    log "WARNING: jq not found, cannot update status"
  fi
}

# Get status of a specific process
check_process_status() {
  local step_idx="$1"
  local proc_idx="$2"
  
  if command -v jq &> /dev/null; then
    local status=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].status" "$STATUS_FILE" 2>/dev/null)
    if [ "$status" = "null" ] || [ -z "$status" ]; then
      echo "NOT_STARTED"
    else
      echo "$status"
    fi
  else
    log "WARNING: jq not found, cannot check status"
    echo "UNKNOWN"
  fi
}

# ===== SCHEDULER FUNCTIONS =====

# Function to execute a command
execute_process() {
  local cmd="$1"
  local step_idx="$2"
  local proc_idx="$3"
  local step_name="$4"
  local proc_name="$5"
  
  # Check if this process is already completed
  local status=$(check_process_status "$step_idx" "$proc_idx")
  if [ "$status" = "COMPLETE" ]; then
    log "Process $proc_name in step $step_name already completed, skipping"
    echo "COMPLETED"
    return 0
  fi
  
  # Define log files
  local stdout_file="${LOG_DIR}/step${step_idx}_proc${proc_idx}_${proc_name}.out"
  local stderr_file="${LOG_DIR}/step${step_idx}_proc${proc_idx}_${proc_name}.err"
  
  # Get scheduler type from model.json if available
  local model_scheduler=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].scheduler" "$MODEL_FILE" 2>/dev/null)
  if [ -z "$model_scheduler" ] || [ "$model_scheduler" = "null" ]; then
    model_scheduler=""
  fi
  
  # Convert to uppercase for consistency
  model_scheduler=$(echo "$model_scheduler" | tr '[:lower:]' '[:upper:]')
  
  # Check if this is a local (direct) command or a scheduler command
  if [[ "$cmd" == "source "* || "$cmd" == "./"* || "$cmd" == "bash "* || "$cmd" == "sh "* ]] || [[ "$model_scheduler" == "LOCAL" ]]; then
    # This is a local command
    log "Running local process $proc_name in step $step_name"
    
    # Update status to running
    update_process_status "$step_idx" "$proc_idx" "RUNNING"
    
    # Execute command directly
    if eval "$cmd" > "$stdout_file" 2> "$stderr_file"; then
      update_process_status "$step_idx" "$proc_idx" "COMPLETE"
      log "Process $proc_name in step $step_name completed successfully"
      echo "COMPLETED"
      return 0
    else
      local exit_code=$?
      local error_msg=$(extract_error "$stderr_file")
      update_process_status "$step_idx" "$proc_idx" "FAILED" "" "$error_msg"
      log "ERROR: Process $proc_name in step $step_name failed with exit code $exit_code"
      echo "FAILED"
      return $exit_code
    fi
  else
    # This is a scheduler command (bsub, sbatch, qsub)
    local scheduler_type=""
    local job_cmd=""
    
    # Determine scheduler type from model.json or command
    if [ -n "$model_scheduler" ]; then
      scheduler_type="$model_scheduler"
    elif [[ "$cmd" == bsub* ]]; then
      scheduler_type="LSF"
    elif [[ "$cmd" == sbatch* ]]; then
      scheduler_type="SLURM"
    elif [[ "$cmd" == qsub* ]]; then
      scheduler_type="PBS"
    else
      log "ERROR: Unknown scheduler command and no scheduler specified in model.json: $cmd"
      echo "FAILED"
      return 1
    fi
    
    # Prepare job command based on scheduler
    if [[ "$scheduler_type" == "LSF" ]]; then
      # Add job name and output redirection to bsub command
      job_cmd="$cmd -J \"${PIPELINE_ID}_${step_name}_${proc_name}\" -o \"$stdout_file\" -e \"$stderr_file\""
    elif [[ "$scheduler_type" == "SLURM" ]]; then
      # Add job name and output redirection to sbatch command
      job_cmd="$cmd -J \"${PIPELINE_ID}_${step_name}_${proc_name}\" -o \"$stdout_file\" -e \"$stderr_file\""
    elif [[ "$scheduler_type" == "PBS" ]]; then
      # For PBS, we need to create a script wrapper
      local script_file="${LOG_DIR}/step${step_idx}_proc${proc_idx}_${proc_name}.pbs"
      echo "#!/bin/bash" > "$script_file"
      echo "#PBS -N ${PIPELINE_ID}_${step_name}_${proc_name}" >> "$script_file"
      echo "#PBS -o $stdout_file" >> "$script_file"
      echo "#PBS -e $stderr_file" >> "$script_file"
      # Extract the actual command after qsub and its options
      local actual_cmd=$(echo "$cmd" | sed 's/^qsub\s*\([^;]*\)\s*;\s*\(.*\)/\2/')
      echo "$actual_cmd" >> "$script_file"
      chmod +x "$script_file"
      
      # Replace original command with qsub to our script file
      job_cmd="qsub $script_file"
    else
      log "ERROR: Unsupported scheduler type: $scheduler_type"
      echo "FAILED"
      return 1
    fi
    
    # Submit the job
    log "Submitting $scheduler_type job for process $proc_name in step $step_name"
    local JOB_ID=""
    
    if [[ "$scheduler_type" == "LSF" ]]; then
      JOB_ID=$(eval "$job_cmd" | awk '{print $2}' | tr -d '<>')
    elif [[ "$scheduler_type" == "SLURM" ]]; then
      JOB_ID=$(eval "$job_cmd")
    else
      JOB_ID=$(eval "$job_cmd")
    fi
    
    # Get scheduler from model.json
    local scheduler=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].scheduler" "$MODEL_FILE" 2>/dev/null)
    
    # Update status to running with job ID and scheduler
    if [ -n "$scheduler" ] && [ "$scheduler" != "null" ]; then
      # Update status file with scheduler information
      jq ".steps[$step_idx].process_execs[$proc_idx].status = \"RUNNING\" | 
          .steps[$step_idx].process_execs[$proc_idx].last_updated = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\" |
          .steps[$step_idx].process_execs[$proc_idx].scheduler_job_id = \"$JOB_ID\" |
          .steps[$step_idx].process_execs[$proc_idx].scheduler = \"$scheduler\"" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
      mv "${STATUS_FILE}.tmp" "$STATUS_FILE"
    else
      update_process_status "$step_idx" "$proc_idx" "RUNNING" "$JOB_ID"
    fi
    
    echo "$JOB_ID"
  fi
}

# Job status checking is now handled directly within the wait_for_jobs function

# Function to wait for jobs to complete
wait_for_jobs() {
  local job_ids="$1"
  local step_idx="$2"
  local timeout="$3"  # Optional timeout in seconds
  
  # If no jobs, return immediately
  if [ -z "$job_ids" ]; then
    return 0
  fi
  
  log "Waiting for jobs to complete for step $step_idx: $job_ids"
  
  # Convert comma-separated job IDs to array
  IFS=',' read -ra JOB_ID_ARRAY <<< "$job_ids"
  
  # Initialize counters
  local start_time=$(date +%s)
  local elapsed=0
  local check_interval=30  # Check every 30 seconds
  
  # Wait for all jobs to complete
  while true; do
    local all_done=true
    
    for job_id in "${JOB_ID_ARRAY[@]}"; do
      # Find process information for this job
      local proc_info=$(jq -r ".steps[$step_idx].process_execs[] | select(.scheduler_job_id==\"$job_id\")" "$STATUS_FILE" 2>/dev/null)
      local proc_idx=$(jq -r ".steps[$step_idx].process_execs[] | select(.scheduler_job_id==\"$job_id\") | .process_id" "$STATUS_FILE" 2>/dev/null)
      
      # If not found, skip this job
      if [ -z "$proc_info" ]; then
        continue
      fi
      
      # Get scheduler type from status file (which we populated from model.json)
      local scheduler=$(jq -r ".steps[$step_idx].process_execs[] | select(.scheduler_job_id==\"$job_id\") | .scheduler" "$STATUS_FILE" 2>/dev/null)
      
      # If scheduler not found in status file, try model.json
      if [ -z "$scheduler" ] || [ "$scheduler" = "null" ]; then
        scheduler=$(jq -r ".steps[$step_idx].process_execs[] | select(.scheduler_job_id==\"$job_id\") | .scheduler" "$MODEL_FILE" 2>/dev/null)
      fi
      
      # If still not found, try to determine from job ID format as fallback
      if [ -z "$scheduler" ] || [ "$scheduler" = "null" ]; then
        if [[ "$job_id" =~ ^[0-9]+$ ]]; then
          # Simple numeric job ID - most likely LSF
          scheduler="LSF"
        elif [[ "$job_id" =~ ^[0-9]+\.[a-zA-Z0-9]+$ ]]; then
          # Format like "12345.server" - most likely PBS
          scheduler="PBS"
        else
          # Default to SLURM for everything else
          scheduler="SLURM"
        fi
      fi
      
      # Convert scheduler to uppercase for consistency
      scheduler=$(echo "$scheduler" | tr '[:lower:]' '[:upper:]')
      
      # Check job status
      local status=""
      case "$scheduler" in
        "LSF")
          # Check if job exists in bjobs output
          if bjobs -a "$job_id" 2>/dev/null | grep -q "$job_id"; then
            # Get job status
            local lsf_status=$(bjobs -noheader -o stat "$job_id" 2>/dev/null)
            case "$lsf_status" in
              "DONE")
                status="COMPLETE"
                ;;
              "EXIT"|"ZOMBI")
                status="FAILED"
                ;;
              *)
                status="RUNNING"
                ;;
            esac
          else
            # Job not found, assume completed
            status="COMPLETE"
          fi
          ;;
          
        "SLURM")
          # Check if job exists
          if squeue -j "$job_id" -h 2>/dev/null | grep -q "$job_id"; then
            # Job exists, still running
            status="RUNNING"
          else
            # Job not in queue, check if it completed successfully
            if sacct -j "$job_id" -n -o State | grep -q "COMPLETED"; then
              status="COMPLETE"
            else
              status="FAILED"
            fi
          fi
          ;;
          
        "PBS")
          # Check if job exists
          if qstat "$job_id" 2>/dev/null | grep -q "$job_id"; then
            # Job exists, still running
            status="RUNNING"
          else
            # Job not in queue, check exit status if possible
            if [ -f "${LOG_DIR}/${job_id}.exit_status" ]; then
              if [ "$(cat "${LOG_DIR}/${job_id}.exit_status")" = "0" ]; then
                status="COMPLETE"
              else
                status="FAILED"
              fi
            else
              # No exit status file, assume completed
              status="COMPLETE"
            fi
          fi
          ;;
          
        *)
          log "ERROR: Could not determine scheduler type for job $job_id"
          status="UNKNOWN"
          ;;
      esac
      
      # Update status based on job status
      if [ "$status" = "COMPLETE" ]; then
        log "Job $job_id completed successfully"
        update_process_status "$step_idx" "$proc_idx" "COMPLETE"
      elif [ "$status" = "FAILED" ]; then
        log "Job $job_id failed"
        local error_msg="Job failed in scheduler"
        update_process_status "$step_idx" "$proc_idx" "FAILED" "$job_id" "$error_msg"
      elif [ "$status" = "RUNNING" ]; then
        all_done=false
      fi
    done
    
    # If all jobs are done or timeout reached, break the loop
    if [ "$all_done" = true ]; then
      break
    fi
    
    # Check if timeout has been reached
    if [ -n "$timeout" ]; then
      elapsed=$(($(date +%s) - start_time))
      if [ $elapsed -ge $timeout ]; then
        log "Timeout reached waiting for jobs to complete"
        return 1
      fi
    fi
    
    # Sleep before checking again
    sleep $check_interval
  done
  
  log "All jobs completed for step $step_idx"
  return 0
}

# ===== PIPELINE EXECUTION =====

# Initialize status file
initialize_status_file

# Update pipeline status to running
if command -v jq &> /dev/null; then
  jq '.status = "running" | .last_updated = "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"' "$STATUS_FILE" > "${STATUS_FILE}.tmp"
  mv "${STATUS_FILE}.tmp" "$STATUS_FILE"
fi

log "Starting pipeline: ${PIPELINE_ID}"

# Validate that model.json exists
if [ ! -f "$MODEL_FILE" ]; then
  log "ERROR: Model file not found: $MODEL_FILE"
  exit 1
fi

# Validate that jq is installed
if ! command -v jq &> /dev/null; then
  log "ERROR: jq is required but not found. Please install jq."
  exit 1
fi

# Get total number of steps
TOTAL_STEPS=$(jq '.steps | length' "$MODEL_FILE")
log "Pipeline has $TOTAL_STEPS steps"

# Process each step
for ((step_idx=0; step_idx<TOTAL_STEPS; step_idx++)); do
  # Get step information
  STEP_NAME=$(jq -r ".steps[$step_idx].name" "$MODEL_FILE")
  STEP_DESC=$(jq -r ".steps[$step_idx].description" "$MODEL_FILE")
  log "Processing step $((step_idx+1))/$TOTAL_STEPS: $STEP_NAME"
  if [ "$STEP_DESC" != "null" ]; then
    log "Description: $STEP_DESC"
  fi
  
  # Check if step is already completed
  STEP_STATUS=$(jq -r ".steps[$step_idx].status" "$STATUS_FILE" 2>/dev/null)
  if [ "$STEP_STATUS" = "COMPLETE" ]; then
    log "Step $((step_idx+1)) already completed, skipping"
    continue
  fi
  
  # Get number of processes in this step
  TOTAL_PROCS=$(jq ".steps[$step_idx].process_execs | length" "$MODEL_FILE")
  log "Step has $TOTAL_PROCS processes"
  
  # Array to store job IDs for this step
  STEP_JOB_IDS=()
  
  # Process each process execution in this step
  for ((proc_idx=0; proc_idx<TOTAL_PROCS; proc_idx++)); do
    # Get process exec information
    PROC_ID=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].exec_id" "$MODEL_FILE")
    PROC_NAME=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].name" "$MODEL_FILE")
    if [ "$PROC_NAME" = "null" ]; then
      PROC_NAME="$PROC_ID"
    fi
    
    log "Processing process $((proc_idx+1))/$TOTAL_PROCS: $PROC_NAME"
    
    # Check if process is already completed
    PROC_STATUS=$(check_process_status "$step_idx" "$proc_idx")
    if [ "$PROC_STATUS" = "COMPLETE" ]; then
      log "Process $PROC_NAME already completed, skipping"
      continue
    fi
    
    # Get the pre-generated execution command from model.json
    # This eliminates the need to reconstruct complex commands with bind paths and env vars
    PROC_CMD=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].exec_command" "$MODEL_FILE")
    if [ "$PROC_CMD" = "null" ]; then
      # If command is not in model.json, log an error
      log "ERROR: Process command not found in model.json for $PROC_NAME"
      PROC_CMD="echo 'Command not found for $PROC_NAME'"
    fi
    
    # Execute the process using the pre-generated command
    # No need to specify scheduler as it's already part of the command
    JOB_ID=$(execute_process "$PROC_CMD" "$step_idx" "$proc_idx" "$STEP_NAME" "$PROC_NAME")
    
    # If not already completed, add to job IDs
    if [ "$JOB_ID" != "COMPLETED" ] && [ "$JOB_ID" != "FAILED" ]; then
      STEP_JOB_IDS+=("$JOB_ID")
      log "Submitted job $PROC_NAME with ID: $JOB_ID"
    fi
  done
  
  # Wait for all processes in this step to complete before moving to next step
  if [ ${#STEP_JOB_IDS[@]} -gt 0 ]; then
    # Convert array to comma-separated string
    STEP_JOB_IDS_STR=$(IFS=,; echo "${STEP_JOB_IDS[*]}")
    log "Waiting for step $((step_idx+1)) jobs to complete: $STEP_JOB_IDS_STR"
    
    # Wait for jobs to complete
    wait_for_jobs "$STEP_JOB_IDS_STR" "$step_idx"
    
    # Check if step completed successfully
    STEP_STATUS=$(jq -r ".steps[$step_idx].status" "$STATUS_FILE")
    if [ "$STEP_STATUS" = "FAILED" ]; then
      log "ERROR: Step $((step_idx+1)) failed, stopping pipeline"
      jq '.status = "failed" | .last_updated = "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"' "$STATUS_FILE" > "${STATUS_FILE}.tmp"
      mv "${STATUS_FILE}.tmp" "$STATUS_FILE"
      exit 1
    fi
  else
    log "No jobs submitted for step $((step_idx+1)) (all processes already completed)"
  fi
  
  log "Step $((step_idx+1)) completed successfully"
done

# Update final status if not already done
if command -v jq &> /dev/null; then
  current_status=$(jq -r '.status' "$STATUS_FILE")
  if [ "$current_status" != "complete" ] && [ "$current_status" != "failed" ]; then
    jq '.status = "complete" | .last_updated = "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"' "$STATUS_FILE" > "${STATUS_FILE}.tmp"
    mv "${STATUS_FILE}.tmp" "$STATUS_FILE"
  fi
fi

log "Pipeline completed: ${PIPELINE_ID}"
exit 0
