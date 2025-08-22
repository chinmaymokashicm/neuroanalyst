"""
Example usage of NeuroAnalyst constants in application code.

This demonstrates how to use the constants module throughout the NeuroAnalyst
framework for consistent path management and configuration.
"""

from app.utils import PATHS, CONFIG, ensure_directories
import os


def example_neuprocess_setup():
    """
    Example of how to set up directories and paths for a new NeuProcess.
    """
    print("Setting up NeuProcess example...")
    
    # Ensure all directories exist
    ensure_directories()
    
    # Create a specific process ID
    process_id = "example_fsl_bet"
    
    # Get process-specific paths
    process_workdir = PATHS.get_process_workdir(process_id)
    process_image_path = PATHS.get_process_image_path(process_id, "v1.0")
    log_file_path = PATHS.get_log_file_path("neuprocess", process_id)
    
    print(f"Process working directory: {process_workdir}")
    print(f"Process image path: {process_image_path}")
    print(f"Log file path: {log_file_path}")
    
    # Create process-specific working directory
    process_workdir.mkdir(parents=True, exist_ok=True)
    
    # Example of creating process files
    main_script_path = process_workdir / CONFIG.MAIN_SCRIPT_NAME
    install_script_path = process_workdir / CONFIG.INSTALL_SCRIPT_NAME
    config_path = process_workdir / CONFIG.CONFIG_NAME
    
    print(f"Main script: {main_script_path}")
    print(f"Install script: {install_script_path}")
    print(f"Config file: {config_path}")


def example_bids_dataset_handling():
    """
    Example of how to handle BIDS dataset paths.
    """
    print("\nBIDS dataset handling example...")
    
    # Example dataset name
    dataset_name = "example_study"
    
    # Get dataset path
    dataset_path = PATHS.datasets / dataset_name
    derivatives_path = dataset_path / CONFIG.DERIVATIVES_DIR
    
    print(f"Dataset path: {dataset_path}")
    print(f"Derivatives path: {derivatives_path}")
    
    # Example pipeline output path
    pipeline_name = "fsl_preprocessing"
    pipeline_output_path = derivatives_path / pipeline_name
    
    print(f"Pipeline output path: {pipeline_output_path}")


def example_image_management():
    """
    Example of Singularity image path management.
    """
    print("\nImage management example...")
    
    # Base images
    ubuntu_base = PATHS.get_base_image_path("ubuntu22.04")
    neurodebian_base = PATHS.get_base_image_path("neurodebian")
    
    print(f"Ubuntu base image: {ubuntu_base}")
    print(f"NeuroDebian base image: {neurodebian_base}")
    
    # Process images
    fsl_process = PATHS.get_process_image_path("fsl_bet", "v1.0")
    freesurfer_process = PATHS.get_process_image_path("freesurfer_recon", "v2.1")
    
    print(f"FSL BET process image: {fsl_process}")
    print(f"FreeSurfer recon process image: {freesurfer_process}")


def example_logging_setup():
    """
    Example of setting up logging with consistent paths.
    """
    print("\nLogging setup example...")
    
    import logging
    
    # Create logger
    logger = logging.getLogger("neuroanalyst.example")
    
    # Get log file path
    log_file = PATHS.get_log_file_path("example")
    
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Set up file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Set up formatter using constants
    formatter = logging.Formatter(CONFIG.LOG_FORMAT, CONFIG.LOG_DATE_FORMAT)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    
    print(f"Logger configured to write to: {log_file}")
    
    # Example log messages
    logger.info("Example log message")
    logger.info(f"Process working in: {PATHS.workdir}")
    logger.info(f"Images stored in: {PATHS.images}")


def example_template_usage():
    """
    Example of how to work with template files.
    """
    print("\nTemplate usage example...")
    
    from app.utils import get_template_path
    
    # Get template paths
    main_template = get_template_path(CONFIG.MAIN_SCRIPT_TEMPLATE)
    readme_template = get_template_path(CONFIG.README_TEMPLATE)
    singularity_template = get_template_path(CONFIG.SINGULARITY_TEMPLATE)
    
    print(f"Main script template: {main_template}")
    print(f"README template: {readme_template}")
    print(f"Singularity template: {singularity_template}")


if __name__ == "__main__":
    print("NeuroAnalyst Constants Usage Examples")
    print("=" * 50)
    
    example_neuprocess_setup()
    example_bids_dataset_handling()
    example_image_management()
    example_logging_setup()
    example_template_usage()
    
    print("\n" + "=" * 50)
    print("Examples completed successfully!")
