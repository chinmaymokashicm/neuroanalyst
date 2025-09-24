#!/bin/bash
# ===== ENVIRONMENT SETUP =====
# Load environment variables if they exist
[ -f "${HOME}/.neuroanalyst/env.sh" ] && source "${HOME}/.neuroanalyst/env.sh"

# ===== PIPELINE VARIABLES =====
PIPELINE_ID="PL_ID_PLACEHOLDER"
PIPELINE_DIR="PL_DIR_PLACEHOLDER"
MODEL_FILE="${PIPELINE_DIR}/model.json"
STATUS_FILE="${PIPELINE_DIR}/status.json"
SCHEDULER="SCHEDULER_PLACEHOLDER"

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
    
    if [ -n "$job_id" ]; then
      job_id_str=", \"scheduler_job_id\": \"$job_id\""
    fi
    
    if [ -n "$error_msg" ]; then
      # Escape quotes in error message
      error_msg=$(echo "$error_msg" | sed 's/"/\\"/g')
      error_msg_str=", \"error\": \"$error_msg\""
    fi
    
    # Update the status
    jq ".steps[$step_idx].process_execs[$proc_idx].status = \"$status\" | 
        .steps[$step_idx].process_execs[$proc_idx].last_updated = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"
        $job_id_str $error_msg_str" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
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

# Function to execute a command with the appropriate scheduler
execute_with_scheduler() {
  local scheduler="$1"
  local cmd="$2"
  local step_idx="$3"
  local proc_idx="$4"
  local step_name="$5"
  local proc_name="$6"
  local depends="$7"
  
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
  
  # Based on scheduler, use the appropriate submit command
  case "$scheduler" in
    "LSF")
      # Prepare dependency string if needed
      local depend_str=""
      if [ -n "$depends" ]; then
        depend_str="-w \"$depends\""
      fi
      
      # Submit job
      log "Submitting LSF job for process $proc_name in step $step_name"
      local JOB_ID=$(bsub -J "${PIPELINE_ID}_${step_name}_${proc_name}" $depend_str -o "$stdout_file" -e "$stderr_file" "$cmd" | awk '{print $2}' | tr -d '<>')
      ;;
      
    "SLURM")
      # Prepare dependency string if needed
      local depend_str=""
      if [ -n "$depends" ]; then
        depend_str="--dependency=afterok:$depends"
      fi
      
      # Submit job
      log "Submitting SLURM job for process $proc_name in step $step_name"
      local JOB_ID=$(sbatch --parsable -J "${PIPELINE_ID}_${step_name}_${proc_name}" $depend_str -o "$stdout_file" -e "$stderr_file" --wrap="$cmd")
      ;;
      
    "PBS")
      # Prepare dependency string if needed
      local depend_str=""
      if [ -n "$depends" ]; then
        depend_str="-W depend=afterok:$depends"
      fi
      
      # PBS needs a script file
      local script_file="${LOG_DIR}/step${step_idx}_proc${proc_idx}_${proc_name}.pbs"
      echo "#!/bin/bash" > "$script_file"
      echo "#PBS -N ${PIPELINE_ID}_${step_name}_${proc_name}" >> "$script_file"
      echo "#PBS -o $stdout_file" >> "$script_file"
      echo "#PBS -e $stderr_file" >> "$script_file"
      echo "$cmd" >> "$script_file"
      chmod +x "$script_file"
      
      # Submit job
      log "Submitting PBS job for process $proc_name in step $step_name"
      local JOB_ID=$(qsub $depend_str "$script_file")
      ;;
      
    "LOCAL")
      # Run locally
      log "Running local process $proc_name in step $step_name"
      
      # Update status to running
      update_process_status "$step_idx" "$proc_idx" "RUNNING"
      
      # Execute command
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
      ;;
      
    *)
      log "ERROR: Unknown scheduler type: $scheduler"
      return 1
      ;;
  esac
  
  # For schedulers (not LOCAL which already handles status updates)
  if [ "$scheduler" != "LOCAL" ]; then
    # Update status to running with job ID
    update_process_status "$step_idx" "$proc_idx" "RUNNING" "$JOB_ID"
    echo "$JOB_ID"
  fi
}

# Function to check job status based on scheduler
check_job_status() {
  local scheduler="$1"
  local job_id="$2"
  
  case "$scheduler" in
    "LSF")
      # Check if job exists in bjobs output
      if bjobs -a "$job_id" 2>/dev/null | grep -q "$job_id"; then
        # Get job status
        local status=$(bjobs -noheader -o stat "$job_id" 2>/dev/null)
        case "$status" in
          "DONE")
            echo "COMPLETE"
            ;;
          "EXIT"|"ZOMBI")
            echo "FAILED"
            ;;
          *)
            echo "RUNNING"
            ;;
        esac
      else
        # Job not found, assume completed
        echo "COMPLETE"
      fi
      ;;
      
    "SLURM")
      # Check if job exists
      if squeue -j "$job_id" -h 2>/dev/null | grep -q "$job_id"; then
        # Job exists, still running
        echo "RUNNING"
      else
        # Job not in queue, check if it completed successfully
        if sacct -j "$job_id" -n -o State | grep -q "COMPLETED"; then
          echo "COMPLETE"
        else
          echo "FAILED"
        fi
      fi
      ;;
      
    "PBS")
      # Check if job exists
      if qstat "$job_id" 2>/dev/null | grep -q "$job_id"; then
        # Job exists, still running
        echo "RUNNING"
      else
        # Job not in queue, check exit status if possible
        if [ -f "${LOG_DIR}/${job_id}.exit_status" ]; then
          if [ "$(cat "${LOG_DIR}/${job_id}.exit_status")" = "0" ]; then
            echo "COMPLETE"
          else
            echo "FAILED"
          fi
        else
          # No exit status file, assume completed
          echo "COMPLETE"
        fi
      fi
      ;;
      
    "LOCAL")
      # For local execution, this isn't used as status is updated directly
      echo "UNKNOWN"
      ;;
      
    *)
      log "ERROR: Unknown scheduler type: $scheduler"
      echo "UNKNOWN"
      ;;
  esac
}

# Function to wait for jobs to complete
wait_for_jobs() {
  local scheduler="$1"
  local job_ids="$2"
  local step_idx="$3"
  local timeout="$4"  # Optional timeout in seconds
  
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
      # Find process ID for this job
      if [ "$scheduler" != "LOCAL" ]; then
        local proc_info=$(jq -r ".steps[$step_idx].process_execs[] | select(.scheduler_job_id==\"$job_id\") | .process_id" "$STATUS_FILE" 2>/dev/null)
        local proc_idx=$(jq -r ".steps[$step_idx].process_execs[] | select(.scheduler_job_id==\"$job_id\") | .process_id" "$STATUS_FILE" 2>/dev/null)
        
        # If not found, skip this job
        if [ -z "$proc_info" ]; then
          continue
        fi
        
        # Check job status
        local status=$(check_job_status "$scheduler" "$job_id")
        
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
    
    # Get process command
    PROC_CMD=$(jq -r ".steps[$step_idx].process_execs[$proc_idx].exec_command" "$MODEL_FILE")
    if [ "$PROC_CMD" = "null" ]; then
      # If command is not in model.json, log an error
      log "ERROR: Process command not found in model.json for $PROC_NAME"
      PROC_CMD="echo 'Command not found for $PROC_NAME'"
    fi
    
    # Execute the process using the appropriate scheduler
    JOB_ID=$(execute_with_scheduler "$SCHEDULER" "$PROC_CMD" "$step_idx" "$proc_idx" "$STEP_NAME" "$PROC_NAME" "")
    
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
    wait_for_jobs "$SCHEDULER" "$STEP_JOB_IDS_STR" "$step_idx"
    
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
