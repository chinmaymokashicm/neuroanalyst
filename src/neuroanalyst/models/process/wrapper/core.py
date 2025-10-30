"""
Core wrapper functions for NeuProcess with PyBIDS integration.

This module provides a comprehensive decorator system for wrapping NeuProcessLogic
functions with BIDS-compliant output path construction, metadata generation,
and enhanced neuroimaging data handling capabilities using PyBIDS.
"""

import json
import time
import pickle
import warnings
import platform
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps

from pydantic import BaseModel, Field
from bids import BIDSLayout
from bids.layout import parse_file_entities
from bids_validator import BIDSValidator

from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
import nibabel as nib

from ....utils import CONFIG

# PyBIDS imports
from bids import BIDSLayout
from bids.layout import parse_file_entities
PYBIDS_AVAILABLE = True

from ..logic.core import NeuProcessLogic


# =======================Wrapper Models=======================


class NeuProcessOutput(BaseModel):
    """Model for validating the expected output from a NeuProcessLogic function."""
    data: Any = Field(..., description="The main output data from the process")
    description: str = Field(..., description="Description of the processing performed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata and parameters")
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the NeuProcessOutput."""
        data_type = type(self.data).__name__
        return f"NeuProcessOutput(data_type='{data_type}', description='{self.description[:30]}{'...' if len(self.description) > 30 else ''}')"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the NeuProcessOutput."""
        data_type = type(self.data).__name__
        meta_keys = list(self.metadata.keys())
        
        return f"NeuProcessOutput(data_type='{data_type}', "\
               f"description='{self.description[:50]}{'...' if len(self.description) > 50 else ''}', "\
               f"metadata_keys={meta_keys})"


class NeuProcessDecoratorConfig(BaseModel):
    """Configuration for the NeuProcess decorator."""
    process_id: str = Field(..., description="ID of the NeuProcess")
    pipeline_id: str = Field(..., description="ID of the NeuPipeline")
    pipeline_name: str = Field(..., description="Name of the pipeline")
    process_exec_id: str = Field(..., description="ID of the NeuProcessExec instance")
    bids_root: Union[str, Path] = Field(..., description="BIDS root directory path")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing files")
    create_sidecar: bool = Field(default=True, description="Whether to create sidecar JSON files")
    derivatives_dir: Optional[str] = Field(default=CONFIG.DERIVATIVES_DIR, description="Custom derivatives directory name")
    bids_layout: Optional[Any] = Field(default=None, description="Pre-initialized BIDSLayout object", exclude=True)
    bids_validate: bool = Field(default=True, description="Whether to validate BIDS compliance")
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the NeuProcessDecoratorConfig."""
        return f"NeuProcessDecoratorConfig(pipeline='{self.pipeline_name}', process_id='{self.process_id}')"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the NeuProcessDecoratorConfig."""
        return f"NeuProcessDecoratorConfig(process_id='{self.process_id}', "\
               f"pipeline_id='{self.pipeline_id}', "\
               f"pipeline_name='{self.pipeline_name}')"
    
    class Config:
        arbitrary_types_allowed = True  # Allow BIDSLayout object
    
    def model_post_init(self, __context: Any) -> None:
        """Convert string paths to Path objects and initialize BIDSLayout."""
        if isinstance(self.bids_root, str):
            self.bids_root = Path(self.bids_root)
        
        # Initialize BIDSLayout if not provided
        if self.bids_layout is None:
            custom_config: dict = {
                "name": "bids_with_desc",
                "entities": [ 
                    {
                        "name": "desc",
                        "pattern": "desc-(?P<desc>[a-zA-Z0-9]+)"
                    },
                    {
                        "name": "hemi",
                        "pattern": "hemi-(?P<hemi>[LR])"
                    }
                ],
                "default_path_patterns": [
                    "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][acq-{acquisition}_][run-{run}_][desc-{desc}_]{suffix}{extension}",
                    "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][task-{task}_][acq-{acquisition}_][ce-{ce}_][dir-{dir}_][rec-{rec}_][run-{run}_][echo-{echo}_][desc-{desc}_]{suffix}{extension}",
                    "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][task-{task}_][acq-{acquisition}_][run-{run}_][desc-{desc}_]{suffix}{extension}",
                    "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][space-{space}_][hemi-{hemi}_][model-{model}_][desc-{desc}_]{suffix}{extension<.nii,.nii.gz,.gii,.surf.gii,.shape.gii>}",
                    "[sub-{subject}/][ses-{session}/][sample-{sample}/]{datatype}/sub-{subject}_[ses-{session}_][sample-{sample}_][desc-{desc}_]{suffix}{extension}",
                    "[sub-{subject}/][ses-{session}/][sample-{sample}/][modality-{modality}_]{datatype}/sub-{subject}_[ses-{session}_][sample-{sample}_][modality-{modality}_][desc-{desc}_]{suffix}{extension}"
                ]
                }
            # Save custom config to a temporary JSON file and use the path
            with open("bids_config_temp.json", "w") as f:
                json.dump(custom_config, f, indent=2)

            absolute_config_path = str(Path.cwd() / "bids_config_temp.json")
            self.bids_layout = BIDSLayout(
                root=str(self.bids_root),
                validate=self.bids_validate,
                derivatives=True,
                config=["bids", absolute_config_path]
            )


class NeuProcessResult(BaseModel):
    """Result from a decorated NeuProcess function."""
    output_filepath: Optional[Path] = Field(default=None, description="Path to the output file")
    sidecar_filepath: Optional[Path] = Field(default=None, description="Path to the sidecar JSON file")
    execution_time: float = Field(..., description="Execution time in seconds")
    success: bool = Field(..., description="Whether the process succeeded")
    error_message: Optional[str] = Field(default=None, description="Error message if process failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Processing metadata")
    bids_entities: Optional[Dict[str, str]] = Field(default=None, description="Extracted BIDS entities")


# =======================Decorator Functions=======================

def neuprocess_decorator(config: NeuProcessDecoratorConfig):
    """
    Decorator that wraps around a NeuProcessLogic function with PyBIDS integration.
    
    This decorator:
    1. Constructs BIDS-appropriate output paths using PyBIDS
    2. Writes output data to the constructed path
    3. Creates sidecar JSON files with metadata, metrics, and process descriptions
    4. Handles error logging and cleanup
    
    Args:
        config: Configuration for the decorator
        
    Returns:
        Decorated function that returns NeuProcessResult
        
    Usage:
        @neuprocess_decorator(NeuProcessDecoratorConfig(
            pipeline_name="my_pipeline",
            bids_root="/path/to/bids/root"
        ))
        def my_process_function(input_filepath: str) -> Dict[str, Any]:
            # Your processing logic here
            return {
                "data": processed_data,
                "description": "Processing description",
                "metadata": {"parameters": {...}}
            }
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(input_filepath: Union[str, Path], *args, **kwargs) -> NeuProcessResult:
            start_time = time.time()
            
            try:
                # Convert input_filepath to Path
                input_path = Path(input_filepath)
                
                # Extract BIDS entities
                bids_entities = _extract_bids_entities(input_path, config)
                
                # Execute the wrapped function
                try:
                    raw_result = func(input_filepath, *args, **kwargs)
                    error_in_func = False
                except Exception as func_error:
                    raw_result = None
                    error_in_func = True
                    func_error_message = f"""Error in function '{func.__name__}': {str(func_error)}.
Traceback: {traceback.format_exc()}
Error message: {str(func_error)}
                    """
                    raise RuntimeError(func_error_message)
                    # func_error_message = str(func_error)

                # Validate the result format using NeuProcessOutput
                if not error_in_func:
                    if isinstance(raw_result, dict):
                        validated_result = NeuProcessOutput(**raw_result)
                        forced_outputs = validated_result.metadata.get("forced_output_filepaths", None)
                        print(f"Function returned dict format. Validated successfully.")
                        print(f"Data type: {type(validated_result.data)}")
                    elif isinstance(raw_result, tuple) and len(raw_result) >= 3:
                        # Handle legacy tuple format
                        output_data, metrics, output_entities = raw_result[:3]
                        forced_outputs = raw_result[3] if len(raw_result) > 3 else None

                        validated_result = NeuProcessOutput(
                            data=output_data,
                            description=f"Processed by {config.pipeline_name}",
                            metadata={
                                "metrics": metrics,
                                "output_bids_entities": output_entities,
                                "forced_output_filepaths": forced_outputs
                            }
                        )
                        print(f"Legacy tuple format detected. Converted to NeuProcessOutput.")
                        print(f"Data type: {type(output_data)}")
                    else:
                        error_in_func = True
                        func_error_message = (
                            f"Function must return a dictionary with keys: "
                            f"'data', 'description', 'metadata' "
                            f"or a tuple (output_data, metrics, output_entities[, forced_outputs]). "
                            f"Got: {type(raw_result)}"
                        )
                else:
                    forced_outputs = None
                
                # Construct output filepath using PyBIDS
                output_entities = validated_result.metadata.get('output_bids_entities', {})
                print(f"Output BIDS entities from function: {output_entities}")
                output_filepath = _construct_output_path(
                    input_path=input_path,
                    config=config,
                    output_entities=output_entities
                )
                print(f"Input file: {input_path}")
                print(f"Output file: {output_filepath}")
                
                if input_filepath == output_filepath:
                    raise ValueError("Input and output file paths cannot be the same.")

                # Create output directory if it doesn't exist
                output_filepath.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if output file exists and handle overwrite
                if output_filepath.exists() and not config.overwrite:
                    raise FileExistsError(f"Output file already exists: {output_filepath}")
                
                # Write output data
                _write_output_data(validated_result.data, output_filepath)
                
                # Delete files under forced_outputs if specified
                if forced_outputs:
                    for fpath in forced_outputs:
                        try:
                            f = Path(fpath)
                            if f.exists():
                                f.unlink()
                                print(f"Deleted forced output file: {f}")
                            # Delete folder if empty
                            if f.parent.exists() and not any(f.parent.iterdir()):
                                f.parent.rmdir()
                                print(f"Deleted empty directory: {f.parent}")
                        except Exception:
                            pass  # Ignore errors during forced file deletion
                
                # Prepare comprehensive metadata
                execution_time = time.time() - start_time
                metadata = {
                    'Description': validated_result.description,
                    'ProcessID': config.process_id,
                    'PipelineID': config.pipeline_id,
                    'ProcessingPipeline': config.pipeline_name,
                    'ProcessExecID': config.process_exec_id,
                    'InputFile': str(input_path),
                    'OutputFile': str(output_filepath),
                    'ProcessingTime': round(execution_time, 3),
                    'ProcessingDate': datetime.now().isoformat(),
                    'BIDSEntities': bids_entities,
                    'FunctionName': func.__name__,
                    'FunctionModule': func.__module__,
                    **validated_result.metadata  # Include any additional metadata
                }
                
                # Create sidecar JSON file if enabled
                sidecar_filepath = None
                if config.create_sidecar:
                    # Handle sidecar filename to avoid overwriting output file
                    if output_filepath.suffix.lower() == CONFIG.JSON_EXTENSION:
                        # If output is already JSON, create sidecar with different name
                        sidecar_filepath = output_filepath.with_name(
                            str(output_filepath).split(".")[0] + f'_sidecar{CONFIG.JSON_EXTENSION}'
                        )
                    else:
                        # Standard case: add .json extension
                        # sidecar_filepath = output_filepath.with_suffix(CONFIG.BIDS_SIDECAR_SUFFIX)
                        sidecar_filepath = str(output_filepath).split(".")[0] + f'{CONFIG.BIDS_SIDECAR_SUFFIX}'
                    
                    with open(sidecar_filepath, 'w') as f:
                        json.dump(metadata, f, indent=2)
                
                return NeuProcessResult(
                    output_filepath=output_filepath,
                    sidecar_filepath=sidecar_filepath,
                    execution_time=execution_time,
                    success=True,
                    error_message=None,
                    metadata=metadata,
                    bids_entities=bids_entities
                )
                
            except Exception as e:
                # Log error and return failed result
                execution_time = time.time() - start_time
                error_message = f"Processing failed: {str(e)}"
                
                # Create error metadata
                error_metadata = {
                    'ProcessID': config.process_id,
                    'PipelineID': config.pipeline_id,
                    'ProcessingPipeline': config.pipeline_name,
                    'ProcessExecID': config.process_exec_id,
                    'InputFile': str(input_filepath),
                    'ProcessingTime': round(execution_time, 3),
                    'ProcessingDate': datetime.now().isoformat(),
                    'Error': error_message,
                    'FunctionName': func.__name__,
                    'FunctionModule': func.__module__
                }
                
                return NeuProcessResult(
                    output_filepath=None,
                    sidecar_filepath=None,
                    execution_time=execution_time,
                    success=False,
                    error_message=error_message,
                    metadata=error_metadata,
                    bids_entities={}
                )
        
        return wrapper
    return decorator


def _extract_bids_entities(input_path: Path, config: NeuProcessDecoratorConfig) -> Dict[str, str]:
    """Extract BIDS entities from input path using PyBIDS."""
    entities = {}
    
    # Use PyBIDS to parse entities
    parsed_entities = parse_file_entities(str(input_path))
    # Filter out None values and convert to strings
    entities = {k: str(v) for k, v in parsed_entities.items() if v is not None}
    
    # Also try to get entities from the layout
    
    file_obj = config.bids_layout.get_file(str(input_path))
    if file_obj:
        layout_entities = file_obj.get_entities()
        # Merge with parsed entities, preferring layout entities
        entities.update({k: str(v) for k, v in layout_entities.items() if v is not None})
    
    return entities


def _construct_output_path(
    input_path: str | Path, 
    config: NeuProcessDecoratorConfig,
    output_entities: Dict[str, str] = {}
    
) -> Path:
    """
    Construct BIDS-compliant output path using PyBIDS.
    
    Args:
        input_path: Path to the input file
        config: NeuProcessDecoratorConfig with BIDS layout and root
        output_entities: Additional or overriding BIDS entities for output file
        
    Returns:
        Path: The constructed output file path
        
    Raises:
        ValueError: If output path cannot be constructed
    """
    # Extract entities from input path
    entities = parse_file_entities(str(input_path))
    
    # Override/add entities from function output
    entities.update(output_entities)
    
    bids_layout: BIDSLayout = config.bids_layout
    
    output_filename: str = bids_layout.build_path(entities, validate=False, strict=False, absolute_paths=False)
    print(f"Constructed output filename before desc check: {output_filename}")
    
    # Include 'desc' entity if provided in output_entities but not appearing in output_filename.
    # This can happen if 'desc' is not part of the original input file, or if the entire BIDS layout does not have it.
    if 'desc' in output_entities and 'desc-' not in output_filename:
        # Insert 'desc-{desc}_' before the suffix
        # Example filename: sub-01_ses-01_T1w.nii.gz -> sub-01_ses-01_desc-{desc}_T1w.nii.gz
        
        # Ensure that output_entities['desc'] is a valid string
        if not isinstance(output_entities['desc'], str) or not output_entities['desc'] or any(c in output_entities['desc'] for c in r'\/:*?"<>| '):
            raise ValueError(f"Invalid 'desc' value in output_entities: {output_entities['desc']}")
        
        # Re-parse to get suffix and extension
        new_output_entities: dict = parse_file_entities(output_filename)
        suffix = new_output_entities.get('suffix', '')
        extension = new_output_entities.get('extension', '')
        base_name = output_filename.replace(f"{suffix}{extension}", "").rstrip("_")
        output_filename = f"{base_name}_desc-{output_entities['desc']}_{suffix}{extension}"
        print(f"Updated output filename with desc: {output_filename}")

    output_filepath = Path(config.bids_root) / "derivatives" / config.pipeline_name / output_filename
    print(f"Final constructed output filepath: {output_filepath}")

    return output_filepath

def _write_output_data(data: Any, output_filepath: Union[str, Path]) -> None:
    """
    Save output data to disk, inferring format from file extension.

    Supported formats:
    - .nii, .nii.gz, .mgz (nibabel images or numpy arrays)
    - .npy (numpy arrays)
    - .npz (dict of numpy arrays)
    - .json (dict, list, JSON-serializable objects)
    - .csv, .tsv (pandas DataFrame, dict, list of dicts, numpy array)
    - .txt (string, list of strings, or any object via str())
    - .pkl (pickle serialization)

    Args:
        data: The data object to save.
        output_filepath: Path where the output should be written.

    Raises:
        ValueError: If format is unsupported or data type doesn't match extension.
    """
    output_filepath = Path(output_filepath)
    suffix = output_filepath.suffix.lower()
    
    # Skip if data is None
    if data is None:
        print(f"No data to write for {output_filepath}. Skipping.")
        return

    # Handle .nii.gz explicitly
    if suffix == ".gz" and output_filepath.name.endswith(".nii.gz"):
        suffix = ".nii.gz"
    
    print(f"Writing output data to {output_filepath} with inferred format {suffix}")

    if suffix in [".nii", ".nii.gz", ".mgz"]:
        print(f"Detected neuroimaging format: {suffix}")
        print(f"Data type: {type(data)}")
        if isinstance(data, nib.spatialimages.SpatialImage):
            print("Saving nibabel image directly")
            nib.save(data, str(output_filepath))
        elif isinstance(data, np.ndarray):
            print("Wrapping numpy array in Nifti1Image and saving")
            img = nib.Nifti1Image(data, affine=np.eye(4))
            nib.save(img, str(output_filepath))
        else:
            raise ValueError(f"Unsupported data type {type(data)} for {suffix}")

    elif suffix == ".gii":
        print(f"Detected Gifti format: {suffix}")
        print(f"Data type: {type(data)}")
        if isinstance(data, nib.gifti.GiftiImage):
            print("Saving Gifti image directly")
            nib.save(data, str(output_filepath))
        else:
            raise ValueError(f"Unsupported data type {type(data)} for {suffix}")
    
    elif suffix == ".npy":
        np.save(str(output_filepath), np.array(data))

    elif suffix == ".npz":
        if isinstance(data, dict):
            np.savez(str(output_filepath), **data)
        else:
            raise ValueError(".npz format requires a dict of numpy arrays")

    elif suffix == ".json":
        with open(output_filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

    elif suffix in [".csv", ".tsv"]:
        sep = "," if suffix == ".csv" else "\t"
        if isinstance(data, pd.DataFrame):
            data.to_csv(output_filepath, sep=sep, index=False)
        elif isinstance(data, (list, dict, np.ndarray)):
            df = pd.DataFrame(data)
            df.to_csv(output_filepath, sep=sep, index=False)
        else:
            raise ValueError(f"Unsupported data type {type(data)} for {suffix}")

    elif suffix == ".txt":
        with open(output_filepath, "w") as f:
            if isinstance(data, str):
                f.write(data)
            elif isinstance(data, (list, tuple)):
                f.write("\n".join(map(str, data)))
            else:
                f.write(str(data))

    elif suffix == ".pkl":
        with open(output_filepath, "wb") as f:
            pickle.dump(data, f)

    else:
        raise ValueError(f"Unsupported file extension: {suffix}")


# =======================Convenience Functions=======================

def create_neuprocess_function(
    logic: NeuProcessLogic,
    config: NeuProcessDecoratorConfig
) -> Callable:
    """
    Create a decorated function from NeuProcessLogic.
    
    Args:
        logic: NeuProcessLogic object containing the function code
        config: Configuration for the decorator
        
    Returns:
        Decorated function ready for execution
    """
    from ..logic.code.python import encode_logic
    
    # Generate the function code
    result = encode_logic(logic)
    
    if not result.is_valid:
        raise ValueError(f"Failed to encode logic: {result.validation_errors}")
    
    # Execute the code to create the function
    namespace = {}
    exec(result.code, namespace)
    
    # Get the function from the namespace
    func = namespace.get(logic.about.name)
    if func is None:
        raise ValueError(f"Function {logic.about.name} not found in generated code")
    
    # Apply the decorator
    decorated_func = neuprocess_decorator(config)(func)
    
    return decorated_func
