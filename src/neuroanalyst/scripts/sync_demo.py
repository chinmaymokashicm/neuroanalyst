"""
Sync Module Demonstration Script

This script demonstrates the usage of the sync module to synchronize
NeuroAnalyst components between HPC and DB.
"""

import argparse
import logging
from pathlib import Path
import sys
import os

# Add src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.append(repo_root)

from src.neuroanalyst.models.sync import (
    NeuProcessSync, 
    NeuProcessExecSync, 
    NeuPipelineSync, 
    LogSync,
    SyncDirection
)


def setup_logging():
    """Setup logging for the demonstration script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('sync_demo.log')
        ]
    )
    return logging.getLogger('sync_demo')


def sync_process(process_id, direction):
    """Sync a NeuProcess."""
    logger.info(f"Syncing process {process_id}")
    process_sync = NeuProcessSync()
    
    if direction == "hpc_to_db":
        result = process_sync.sync_to_db(process_id)
        logger.info(f"Sync result: {result}")
    elif direction == "db_to_hpc":
        result = process_sync.sync_from_db(process_id)
        logger.info(f"Sync successful: {result}")
    else:
        # Compare differences
        diff = process_sync.compare_diff(process_id)
        logger.info(f"Differences: {diff}")


def sync_exec(exec_id, direction):
    """Sync a NeuProcessExec."""
    logger.info(f"Syncing exec {exec_id}")
    exec_sync = NeuProcessExecSync()
    
    if direction == "hpc_to_db":
        result = exec_sync.sync_to_db(exec_id)
        logger.info(f"Sync result: {result}")
    elif direction == "db_to_hpc":
        result = exec_sync.sync_from_db(exec_id)
        logger.info(f"Sync successful: {result}")
    else:
        # Compare differences
        diff = exec_sync.compare_diff(exec_id)
        logger.info(f"Differences: {diff}")


def sync_pipeline(pipeline_id, direction):
    """Sync a NeuPipeline."""
    logger.info(f"Syncing pipeline {pipeline_id}")
    pipeline_sync = NeuPipelineSync()
    
    if direction == "hpc_to_db":
        result = pipeline_sync.sync_to_db(pipeline_id)
        logger.info(f"Sync result: {result}")
    elif direction == "db_to_hpc":
        result = pipeline_sync.sync_from_db(pipeline_id)
        logger.info(f"Sync successful: {result}")
    else:
        # Compare differences
        diff = pipeline_sync.compare_diff(pipeline_id)
        logger.info(f"Differences: {diff}")


def sync_logs(component_id, component_type, direction):
    """Sync logs for a component."""
    logger.info(f"Syncing logs for {component_type} {component_id}")
    log_sync = LogSync()
    
    if direction == "hpc_to_db":
        result = log_sync.sync_to_db(component_id, component_type)
        logger.info(f"Sync result: {result}")
    elif direction == "db_to_hpc":
        result = log_sync.sync_from_db(component_id, component_type)
        logger.info(f"Sync successful: {result}")
    else:
        # Compare differences
        diff = log_sync.compare_diff(component_id, component_type)
        logger.info(f"Differences: {diff}")


def main():
    """Main function for the demonstration script."""
    parser = argparse.ArgumentParser(description="Sync Module Demonstration")
    parser.add_argument("--component-type", type=str, required=True, 
                       choices=["process", "exec", "pipeline", "logs"],
                       help="Type of component to sync")
    parser.add_argument("--component-id", type=str, required=True,
                       help="ID of the component to sync")
    parser.add_argument("--direction", type=str, default="compare",
                       choices=["hpc_to_db", "db_to_hpc", "compare"],
                       help="Direction of sync")
    
    args = parser.parse_args()
    
    if args.component_type == "process":
        sync_process(args.component_id, args.direction)
    elif args.component_type == "exec":
        sync_exec(args.component_id, args.direction)
    elif args.component_type == "pipeline":
        sync_pipeline(args.component_id, args.direction)
    elif args.component_type == "logs":
        # For logs, we need to infer the component type from the ID format
        # or ask the user to provide it
        component_type = input("Enter the component type for logs (process/exec/pipeline): ")
        sync_logs(args.component_id, component_type, args.direction)


if __name__ == "__main__":
    logger = setup_logging()
    main()
