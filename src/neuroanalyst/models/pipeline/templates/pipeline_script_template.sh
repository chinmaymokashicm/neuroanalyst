#!/bin/bash
# ===== PIPELINE SCRIPT =====
# This script orchestrates a pipeline of NeuProcess executions.
# It uses the model.json file for execution commands and scheduler information,
# and updates status.json to track progress.

# ====  # Use the pipeline's scheduler setting for all processes
log "Using scheduler: $SCHEDULER for process $exec_id"
# Load environment variables if they exist
[ -f "${HOME}/.neuroanalyst/env.sh" ] && source "${HOME}/.neuroanalyst/env.sh"

# ===== PIPELINE VARIABLES =====
PIPELINE_ID="PL_ID_PLACEHOLDER"
PIPELINE_DIR="PL_DIR_PLACEHOLDER"
MODEL_FILE="${PIPELINE_DIR}/model.json"
STATUS_FILE="${PIPELINE_DIR}/status.json"

# Set the scheduler type - this is passed from the Python NeuPipeline model
SCHEDULER="SCHEDULER_PLACEHOLDER"  

# As a fallback, try to read scheduler from model.json if the placeholder wasn't replaced
if [ "$SCHEDULER" = "SCHEDULER_PLACEHOLDER" ] && command -v jq &> /dev/null; then
  SCHEDULER=$(jq -r '.scheduler' "$MODEL_FILE" 2>/dev/null)
  if [ "$SCHEDULER" = "null" ] || [ -z "$SCHEDULER" ]; then
    SCHEDULER="LSF"  # Default to LSF if not specified
  fi
fi

# Convert to uppercase for consistency
SCHEDULER=$(echo "$SCHEDULER" | tr '[:lower:]' '[:upper:]')

# ===== LOG DIRECTORY SETUP =====
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ -n "${NEUROANALYST_LOGS}" ]; then
  LOG_BASE="${NEUROANALYST_LOGS}"
else
  LOG_BASE="${HOME}/.neuroanalyst/logs"
fi
LOG_DIR="${LOG_BASE}/pipelines/${PIPELINE_ID}/${TIMESTAMP}"
mkdir -p "${LOG_DIR}"
MAIN_LOG="${LOG_DIR}/pipeline.log"

# ===== UTILITY FUNCTIONS =====

# Function to log messages with timestamp
log() {
  local message="$1"
  local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
  echo "[${timestamp}] ${message}" | tee -a "${MAIN_LOG}"
}

# Extract error messages from log files
extract_error() {
  local log_file="$1"
  local lines=20
  
  if [ -f "$log_file" ]; then
    tail -n $lines "$log_file"
  else
    echo "Log file not found: $log_file"
  fi
}

# ===== STATUS MANAGEMENT FUNCTIONS =====

# Update the status of the entire pipeline
update_pipeline_status() {
  local status="$1"
  local error_msg="$2"
  
  if command -v jq &> /dev/null; then
    local error_field=""
    if [ -n "$error_msg" ]; then
      # Escape quotes in error message
      error_msg=$(echo "$error_msg" | sed 's/"/\\"/g')
      error_field=", \"error\": \"$error_msg\""
    fi
    
    jq ".status = \"$status\" | .last_updated = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"$error_field" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
    mv "${STATUS_FILE}.tmp" "$STATUS_FILE"
  else
    log "ERROR: jq not found. Cannot update status"
  fi
}

# Update the status of a specific step
update_step_status() {
  local step_idx="$1"
  local status="$2"
  local error_msg="$3"
  
  if command -v jq &> /dev/null; then
    local error_field=""
    local timestamp_field=""
    
    # Set timestamp fields based on status
    if [ "$status" = "RUNNING" ]; then
      timestamp_field=", \"started_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\""
    elif [ "$status" = "COMPLETE" ] || [ "$status" = "FAILED" ]; then
      timestamp_field=", \"completed_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\""
    fi
    
    # Add error message if provided
    if [ -n "$error_msg" ]; then
      # Escape quotes in error message
      error_msg=$(echo "$error_msg" | sed 's/"/\\"/g')
      error_field=", \"error\": \"$error_msg\""
    fi
    
    jq ".steps[$step_idx].status = \"$status\" | .steps[$step_idx].last_updated = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"$timestamp_field$error_field" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
    mv "${STATUS_FILE}.tmp" "$STATUS_FILE"
  else
    log "ERROR: jq not found. Cannot update status"
  fi
}

# Update the status of a specific process
update_process_status() {
  local step_idx="$1"
  local proc_idx="$2"
  local status="$3"
  local job_id="$4"
  local error_msg="$5"
  
  if command -v jq &> /dev/null; then
    local job_id_field=""
    local error_field=""
    local timestamp_field=""
    
    # Set timestamp fields based on status
    if [ "$status" = "RUNNING" ]; then
      timestamp_field=", \"started_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\""
    elif [ "$status" = "COMPLETE" ] || [ "$status" = "FAILED" ]; then
      timestamp_field=", \"completed_at\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\""
    fi
    
    # Add job_id if provided
    if [ -n "$job_id" ]; then
      job_id_field=", \"scheduler_job_id\": \"$job_id\""
    fi
    
    # Scheduler is now set only at the pipeline level
    
    # Add error message if provided
    if [ -n "$error_msg" ]; then
      # Escape quotes in error message
      error_msg=$(echo "$error_msg" | sed 's/"/\\"/g')
      error_field=", \"error\": \"$error_msg\""
    fi
    
    # Get the process path in the JSON
    jq ".steps[$step_idx].processes[$proc_idx].status = \"$status\" | 
        .steps[$step_idx].processes[$proc_idx].last_updated = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"$timestamp_field$job_id_field$error_field" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
    mv "${STATUS_FILE}.tmp" "$STATUS_FILE"
    
    # Check if all processes in this step are complete or failed
    check_step_completion "$step_idx"
  else
    log "ERROR: jq not found. Cannot update status"
  fi
}

# Check if a step is complete (all processes are complete or failed)
check_step_completion() {
  local step_idx="$1"
  
  if command -v jq &> /dev/null; then
    local total_procs=$(jq ".steps[$step_idx].processes | length" "$STATUS_FILE")
    local complete_count=$(jq "[.steps[$step_idx].processes[] | select(.status == \"COMPLETE\")] | length" "$STATUS_FILE")
    local failed_count=$(jq "[.steps[$step_idx].processes[] | select(.status == \"FAILED\")] | length" "$STATUS_FILE")
    local finished_count=$((complete_count + failed_count))
    
    if [ "$finished_count" -eq "$total_procs" ]; then
      if [ "$failed_count" -gt 0 ]; then
        update_step_status "$step_idx" "FAILED" "One or more processes failed"
        log "Step $((step_idx+1)) failed: $failed_count out of $total_procs processes failed"
      else
        update_step_status "$step_idx" "COMPLETE"
        log "Step $((step_idx+1)) completed successfully (all $total_procs processes completed)"
      fi
      return 0
    fi
    return 1
  else
    log "ERROR: jq not found. Cannot check step completion"
    return 1
  fi
}

# Find the first incomplete step
find_next_step() {
  if command -v jq &> /dev/null; then
    local total_steps=$(jq ".steps | length" "$STATUS_FILE")
    
    for ((i=0; i<total_steps; i++)); do
      local step_status=$(jq -r ".steps[$i].status" "$STATUS_FILE")
      if [ "$step_status" != "COMPLETE" ] && [ "$step_status" != "FAILED" ]; then
        echo $i
        return 0
      fi
    done
    
    # No incomplete steps found
    echo "-1"
    return 0
  else
    log "ERROR: jq not found. Cannot find next step"
    echo "-1"
    return 1
  fi
}

# ===== PROCESS EXECUTION FUNCTIONS =====

# Function to execute a process
execute_process() {
  local step_idx="$1"
  local proc_idx="$2"
  
  # Get process information
  local exec_id=$(jq -r ".steps[$step_idx].processes[$proc_idx].exec_id" "$STATUS_FILE")
  local process_status=$(jq -r ".steps[$step_idx].processes[$proc_idx].status" "$STATUS_FILE")
  local step_name=$(jq -r ".steps[$step_idx].name" "$STATUS_FILE")
  
  # If process is already complete or failed, skip it
  if [ "$process_status" = "COMPLETE" ] || [ "$process_status" = "FAILED" ]; then
    log "Process $exec_id in step $step_name already has status $process_status, skipping"
    return 0
  fi
  
  # Get the execution command from model.json
  local exec_command=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].exec_command" "$MODEL_FILE")
  if [ "$exec_command" = "null" ] || [ -z "$exec_command" ]; then
    log "ERROR: No execution command found for process $exec_id"
    update_process_status "$step_idx" "$proc_idx" "FAILED" "" "" "No execution command found"
    return 1
  fi
  
  # Get scheduler type - first check process-specific setting, then fall back to global setting
  local scheduler_type=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].scheduler" "$MODEL_FILE" 2>/dev/null)
  if [ "$scheduler_type" = "null" ] || [ -z "$scheduler_type" ]; then
    # Use the global scheduler setting if no process-specific setting is found
    scheduler_type="$GLOBAL_SCHEDULER"
    log "Using global scheduler setting: $scheduler_type for process $exec_id"
  fi
  
  # If process is explicitly marked as LOCAL, honor that setting
  local is_local_process=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].is_local" "$MODEL_FILE" 2>/dev/null)
  if [ "$is_local_process" = "true" ]; then
    scheduler_type="LOCAL"
    log "Process $exec_id is marked as local, overriding scheduler setting"
  fi
  
  # Setup log files
  local stdout_file="${LOG_DIR}/step${step_idx}_proc${proc_idx}_${exec_id}.out"
  local stderr_file="${LOG_DIR}/step${step_idx}_proc${proc_idx}_${exec_id}.err"
  
  log "Executing process $exec_id in step $step_name (scheduler: $scheduler_type)"
  update_process_status "$step_idx" "$proc_idx" "RUNNING"
  
  # Execute based on scheduler type
  local job_id=""
  
  if [ "$SCHEDULER" = "LOCAL" ]; then
    # Local execution
    if eval "$exec_command" > "$stdout_file" 2> "$stderr_file"; then
      log "Process $exec_id completed successfully"
      update_process_status "$step_idx" "$proc_idx" "COMPLETE" ""
      return 0
    else
      local exit_code=$?
      local error_msg=$(extract_error "$stderr_file")
      log "ERROR: Process $exec_id failed with exit code $exit_code"
      update_process_status "$step_idx" "$proc_idx" "FAILED" "" "$error_msg"
      return $exit_code
    fi
  elif [ "$SCHEDULER" = "LSF" ]; then
    # LSF submission
    local lsf_output
    
    # Modify the command to include job name and output redirection if needed
    if [[ "$exec_command" != *"-J "* ]]; then
      exec_command="$exec_command -J ${PIPELINE_ID}_${step_name}_${exec_id}"
    fi
    if [[ "$exec_command" != *"-o "* ]]; then
      exec_command="$exec_command -o $stdout_file"
    fi
    if [[ "$exec_command" != *"-e "* ]]; then
      exec_command="$exec_command -e $stderr_file"
    fi
    
    log "Submitting LSF job for process $exec_id in step $step_name"
    lsf_output=$(eval "$exec_command" 2>&1)
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
      log "ERROR: Failed to submit job for process $exec_id: $lsf_output"
      update_process_status "$step_idx" "$proc_idx" "FAILED" "" "$lsf_output"
      return $exit_code
    fi
    
    # Extract job ID using various patterns
    job_id=$(echo "$lsf_output" | grep -o "Job <[0-9]*>" | grep -o "[0-9]*" || echo "")
    if [ -z "$job_id" ]; then
      # Try alternative pattern
      job_id=$(echo "$lsf_output" | grep -o "[0-9]\+" | head -1 || echo "")
    fi
    
    if [ -n "$job_id" ]; then
      log "LSF job submitted for process $exec_id with ID: $job_id"
      update_process_status "$step_idx" "$proc_idx" "RUNNING" "$job_id"
      return 0
    else
      log "WARNING: Could not extract job ID from LSF output: $lsf_output"
      update_process_status "$step_idx" "$proc_idx" "RUNNING" "unknown"
      return 0
    fi
  elif [ "$SCHEDULER" = "SLURM" ]; then
    # SLURM submission
    local slurm_output
    
    # Modify the command to include job name and output redirection if needed
    if [[ "$exec_command" != *"-J "* ]]; then
      exec_command="$exec_command -J ${PIPELINE_ID}_${step_name}_${exec_id}"
    fi
    if [[ "$exec_command" != *"-o "* ]]; then
      exec_command="$exec_command -o $stdout_file"
    fi
    if [[ "$exec_command" != *"-e "* ]]; then
      exec_command="$exec_command -e $stderr_file"
    fi
    
    log "Submitting SLURM job for process $exec_id in step $step_name"
    slurm_output=$(eval "$exec_command" 2>&1)
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
      log "ERROR: Failed to submit job for process $exec_id: $slurm_output"
      update_process_status "$step_idx" "$proc_idx" "FAILED" "" "$slurm_output"
      return $exit_code
    fi
    
    # Extract job ID
    job_id=$(echo "$slurm_output" | grep -o "Submitted batch job [0-9]*" | awk '{print $4}' || echo "")
    if [ -z "$job_id" ]; then
      job_id=$(echo "$slurm_output" | grep -o "[0-9]\+" | head -1 || echo "")
    fi
    
    if [ -n "$job_id" ]; then
      log "SLURM job submitted for process $exec_id with ID: $job_id"
      update_process_status "$step_idx" "$proc_idx" "RUNNING" "$job_id"
      return 0
    else
      log "WARNING: Could not extract job ID from SLURM output: $slurm_output"
      update_process_status "$step_idx" "$proc_idx" "RUNNING" "unknown"
      return 0
    fi
  elif [ "$SCHEDULER" = "PBS" ]; then
    # PBS submission
    local pbs_output
    
    # Create a PBS script wrapper if needed
    local script_file="${LOG_DIR}/step${step_idx}_proc${proc_idx}_${exec_id}.pbs"
    echo "#!/bin/bash" > "$script_file"
    echo "#PBS -N ${PIPELINE_ID}_${step_name}_${exec_id}" >> "$script_file"
    echo "#PBS -o $stdout_file" >> "$script_file"
    echo "#PBS -e $stderr_file" >> "$script_file"
    
    # Extract the actual command and add it to the script
    if [[ "$exec_command" == qsub* ]]; then
      local actual_cmd=$(echo "$exec_command" | sed 's/^qsub\s*\([^;]*\)\s*;\s*\(.*\)/\2/')
      echo "$actual_cmd" >> "$script_file"
      exec_command="qsub $script_file"
    else
      echo "$exec_command" >> "$script_file"
      exec_command="qsub $script_file"
    fi
    
    chmod +x "$script_file"
    
    log "Submitting PBS job for process $exec_id in step $step_name"
    pbs_output=$(eval "$exec_command" 2>&1)
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
      log "ERROR: Failed to submit job for process $exec_id: $pbs_output"
      update_process_status "$step_idx" "$proc_idx" "FAILED" "" "$pbs_output"
      return $exit_code
    fi
    
    # Extract job ID
    job_id=$(echo "$pbs_output" | grep -o "[0-9]\+" | head -1 || echo "")
    
    if [ -n "$job_id" ]; then
      log "PBS job submitted for process $exec_id with ID: $job_id"
      update_process_status "$step_idx" "$proc_idx" "RUNNING" "$job_id"
      return 0
    else
      log "WARNING: Could not extract job ID from PBS output: $pbs_output"
      update_process_status "$step_idx" "$proc_idx" "RUNNING" "unknown"
      return 0
    fi
  else
    log "ERROR: Unsupported scheduler type: $scheduler_type"
    update_process_status "$step_idx" "$proc_idx" "FAILED" "" "Unsupported scheduler type: $SCHEDULER"
    return 1
  fi
}

# Function to check the status of a job
check_job_status() {
  local job_id="$1"
  
  case "$SCHEDULER" in
    "LSF")
      # Check LSF job status
      local bjobs_output=$(bjobs -noheader $job_id 2>/dev/null)
      
      if [ -z "$bjobs_output" ]; then
        # Job not found in queue, assume it's done
        # Check with bhist to see if it finished successfully
        local bhist_output=$(bhist -n 1 -l $job_id 2>/dev/null | grep -E "Done|Exit")
        
        if [[ "$bhist_output" == *"Done"* ]]; then
          echo "COMPLETE"
        else
          echo "FAILED"
        fi
      elif [[ "$bjobs_output" == *"PEND"* ]]; then
        echo "RUNNING"
      elif [[ "$bjobs_output" == *"RUN"* ]]; then
        echo "RUNNING"
      elif [[ "$bjobs_output" == *"DONE"* ]]; then
        echo "COMPLETE"
      elif [[ "$bjobs_output" == *"EXIT"* ]]; then
        echo "FAILED"
      else
        echo "UNKNOWN"
      fi
      ;;
      
    "SLURM")
      # Check SLURM job status
      local squeue_output=$(squeue -h -j $job_id -o "%t" 2>/dev/null)
      
      if [ -z "$squeue_output" ]; then
        # Job not in queue, check if it completed successfully
        local sacct_output=$(sacct -j $job_id -n -o State 2>/dev/null | head -1)
        
        if [[ "$sacct_output" == *"COMPLETED"* ]]; then
          echo "COMPLETE"
        else
          echo "FAILED"
        fi
      elif [[ "$squeue_output" == *"PD"* ]]; then
        echo "RUNNING"
      elif [[ "$squeue_output" == *"R"* ]]; then
        echo "RUNNING"
      else
        echo "RUNNING"  # Default to running if status unclear
      fi
      ;;
      
    "PBS")
      # Check PBS job status
      local qstat_output=$(qstat -f $job_id 2>/dev/null)
      
      if [ -z "$qstat_output" ]; then
        # Job not in queue, check completion status
        if [ -f "Job $job_id completed" ]; then
          echo "COMPLETE"
        else
          echo "FAILED"
        fi
      elif [[ "$qstat_output" == *"job_state = C"* ]]; then
        echo "COMPLETE"
      elif [[ "$qstat_output" == *"job_state = F"* ]]; then
        echo "FAILED"
      else
        echo "RUNNING"
      fi
      ;;
      
    *)
      echo "UNKNOWN"
      ;;
  esac
}

# Function to wait for all jobs in a step to complete
wait_for_step_jobs() {
  local step_idx="$1"
  local max_wait_time="${2:-3600}"  # Default max wait time: 1 hour
  local check_interval="${3:-60}"    # Default check interval: 60 seconds
  
  log "Waiting for all jobs in step $((step_idx+1)) to complete"
  
  local start_time=$(date +%s)
  local all_complete=false
  
  while [ "$all_complete" = false ]; do
    local current_time=$(date +%s)
    local elapsed=$((current_time - start_time))
    
    # Check if we've exceeded max wait time
    if [ $elapsed -gt $max_wait_time ]; then
      log "WARNING: Max wait time ($max_wait_time seconds) exceeded for step $((step_idx+1))"
      return 1
    fi
    
    # Get all processes for this step
    local total_procs=$(jq ".steps[$step_idx].processes | length" "$STATUS_FILE")
    all_complete=true
    
    for ((proc_idx=0; proc_idx<total_procs; proc_idx++)); do
      local proc_status=$(jq -r ".steps[$step_idx].processes[$proc_idx].status" "$STATUS_FILE")
      local exec_id=$(jq -r ".steps[$step_idx].processes[$proc_idx].exec_id" "$STATUS_FILE")
      
      if [ "$proc_status" = "RUNNING" ]; then
        # Get job ID
        local job_id=$(jq -r ".steps[$step_idx].processes[$proc_idx].scheduler_job_id" "$STATUS_FILE")
        
        if [ -n "$job_id" ] && [ "$job_id" != "null" ] && [ "$job_id" != "unknown" ]; then
          # Check job status using the global scheduler setting
          local job_status=$(check_job_status "$job_id")
          
          if [ "$job_status" = "COMPLETE" ]; then
            log "Process $exec_id completed successfully"
            update_process_status "$step_idx" "$proc_idx" "COMPLETE"
          elif [ "$job_status" = "FAILED" ]; then
            log "Process $exec_id failed"
            update_process_status "$step_idx" "$proc_idx" "FAILED" "$job_id" "Job failed on scheduler"
          else
            # Job still running
            all_complete=false
          fi
        else
          # Local process or job ID not captured
          # Check if output file exists and contains success/failure indicators
          local stdout_file="${LOG_DIR}/step${step_idx}_proc${proc_idx}_${exec_id}.out"
          local stderr_file="${LOG_DIR}/step${step_idx}_proc${proc_idx}_${exec_id}.err"
          
          # Simple heuristic: if stderr has content, consider as failed
          if [ -s "$stderr_file" ]; then
            local error_msg=$(extract_error "$stderr_file")
            log "Process $exec_id likely failed based on stderr content"
            update_process_status "$step_idx" "$proc_idx" "FAILED" "" "$error_msg"
          elif [ -f "$stdout_file" ] && [ -s "$stdout_file" ]; then
            # Output file exists and has content, assume success
            log "Process $exec_id likely completed based on stdout content"
            update_process_status "$step_idx" "$proc_idx" "COMPLETE"
          else
            # Can't determine status, consider still running
            all_complete=false
          fi
        fi
      elif [ "$proc_status" != "COMPLETE" ] && [ "$proc_status" != "FAILED" ]; then
        # Process not in terminal state
        all_complete=false
      fi
    done
    
    if [ "$all_complete" = true ]; then
      break
    fi
    
    log "Still waiting for jobs in step $((step_idx+1)), checking again in $check_interval seconds..."
    sleep $check_interval
  done
  
  # Check if step was updated to complete or failed
  check_step_completion "$step_idx"
  
  local step_status=$(jq -r ".steps[$step_idx].status" "$STATUS_FILE")
  if [ "$step_status" = "FAILED" ]; then
    log "Step $((step_idx+1)) failed"
    return 1
  fi
  
  log "All jobs in step $((step_idx+1)) completed"
  return 0
}

# ===== MAIN EXECUTION =====
main() {
  # Validate that required files exist
  if [ ! -f "$MODEL_FILE" ]; then
    log "ERROR: Model file not found: $MODEL_FILE"
    exit 1
  fi
  
  if [ ! -f "$STATUS_FILE" ]; then
    log "ERROR: Status file not found: $STATUS_FILE"
    exit 1
  fi
  
  # Validate that jq is installed
  if ! command -v jq &> /dev/null; then
    log "ERROR: jq is required but not found. Please install jq."
    exit 1
  fi
  
  # Update pipeline status to running
  update_pipeline_status "running"
  
  log "Starting pipeline execution: ${PIPELINE_ID}"
  
  # Get total number of steps
  local total_steps=$(jq '.steps | length' "$STATUS_FILE")
  log "Pipeline has $total_steps steps"
  
  # Find the next step to execute
  local next_step=$(find_next_step)
  
  # Process each remaining step in sequence
  while [ "$next_step" -ne -1 ] && [ "$next_step" -lt "$total_steps" ]; do
    local step_idx=$next_step
    local step_name=$(jq -r ".steps[$step_idx].name" "$STATUS_FILE")
    
    log "Processing step $((step_idx+1))/$total_steps: $step_name"
    update_step_status "$step_idx" "RUNNING"
    
    # Get number of processes in this step
    local total_procs=$(jq ".steps[$step_idx].processes | length" "$STATUS_FILE")
    log "Step has $total_procs processes"
    
    # Execute all processes in this step
    for ((proc_idx=0; proc_idx<total_procs; proc_idx++)); do
      execute_process "$step_idx" "$proc_idx"
    done
    
    # Wait for all processes in this step to complete
    wait_for_step_jobs "$step_idx"
    
    # Check if step failed
    local step_status=$(jq -r ".steps[$step_idx].status" "$STATUS_FILE")
    if [ "$step_status" = "FAILED" ]; then
      log "Step $((step_idx+1)) failed, stopping pipeline"
      update_pipeline_status "failed" "Step $((step_idx+1)) failed"
      exit 1
    fi
    
    log "Step $((step_idx+1)) completed successfully"
    
    # Find the next step
    next_step=$(find_next_step)
  done
  
  # Check if all steps are completed
  local all_completed=$(jq -r 'all(.steps[]; .status == "COMPLETE")' "$STATUS_FILE")
  
  if [ "$all_completed" = "true" ]; then
    log "All steps completed successfully"
    update_pipeline_status "complete"
  else
    local incomplete_steps=$(jq '[.steps[] | select(.status != "COMPLETE")] | length' "$STATUS_FILE")
    log "Pipeline execution incomplete: $incomplete_steps steps not completed"
    update_pipeline_status "incomplete" "$incomplete_steps steps not completed"
    exit 1
  fi
  
  log "Pipeline execution completed: ${PIPELINE_ID}"
  exit 0
}

# Execute main function
main
