"""
Core wrapper functions for NeuProcess with PyBIDS integration.

This module provides a comprehensive decorator system for wrapping NeuProcessLogic
functions with BIDS-compliant output path construction, metadata generation,
and enhanced neuroimaging data handling capabilities using PyBIDS.
"""

import functools
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps

from pydantic import BaseModel, Field
from bids import BIDSLayout
from bids.layout import parse_file_entities

import json
import os
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import time
import warnings

from pydantic import BaseModel, Field

from ....utils import PATHS, CONFIG

# PyBIDS imports
try:
    from bids import BIDSLayout
    from bids.layout import parse_file_entities
    PYBIDS_AVAILABLE = True
except ImportError:
    warnings.warn("PyBIDS not available. BIDS path construction will use fallback methods.")
    BIDSLayout = None
    parse_file_entities = None
    PYBIDS_AVAILABLE = False

from ..logic.core import NeuProcessLogic


# =======================Wrapper Models=======================

class NeuProcessOutput(BaseModel):
    """Model for validating the expected output from a NeuProcessLogic function."""
    data: Any = Field(..., description="The main output data from the process")
    description: str = Field(..., description="Description of the processing performed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata and parameters")


class NeuProcessDecoratorConfig(BaseModel):
    """Configuration for the NeuProcess decorator."""
    pipeline_name: str = Field(..., description="Name of the pipeline")
    bids_root: Union[str, Path] = Field(..., description="BIDS root directory path")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing files")
    create_sidecar: bool = Field(default=True, description="Whether to create sidecar JSON files")
    derivatives_dir: Optional[str] = Field(default=CONFIG.DERIVATIVES_DIR, description="Custom derivatives directory name")
    bids_layout: Optional[Any] = Field(default=None, description="Pre-initialized BIDSLayout object", exclude=True)
    bids_validate: bool = Field(default=False, description="Whether to validate BIDS compliance")
    
    class Config:
        arbitrary_types_allowed = True  # Allow BIDSLayout object
    
    def model_post_init(self, __context: Any) -> None:
        """Convert string paths to Path objects and initialize BIDSLayout."""
        if isinstance(self.bids_root, str):
            self.bids_root = Path(self.bids_root)
        
        # Initialize BIDSLayout if not provided
        if self.bids_layout is None:
            self.bids_layout = BIDSLayout(
                root=str(self.bids_root),
                validate=self.bids_validate,
                derivatives=True
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
                    func_error_message = str(func_error)

                # Validate the result format using NeuProcessOutput
                if not error_in_func:
                    if isinstance(raw_result, dict):
                        validated_result = NeuProcessOutput(**raw_result)
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
                    else:
                        error_in_func = True
                        func_error_message = (
                            f"Function must return a dictionary with keys: "
                            f"'data', 'description', 'metadata' "
                            f"or a tuple (output_data, metrics, output_entities[, forced_outputs]). "
                            f"Got: {type(raw_result)}"
                        )
                if error_in_func:
                    # Prepare error metadata
                    validated_result = NeuProcessOutput(
                        data=None,
                        description=f"Error in {config.pipeline_name}",
                        metadata={
                            "error": func_error_message,
                            "function_name": func.__name__,
                            "function_module": func.__module__,
                            "input_filepath": str(input_filepath)
                        }
                    )
                
                # Construct output filepath using PyBIDS
                output_entities = validated_result.metadata.get('output_bids_entities', {})
                output_filepath = _construct_output_path(
                    input_path=input_path,
                    config=config,
                    output_entities=output_entities
                )
                
                # Create output directory if it doesn't exist
                output_filepath.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if output file exists and handle overwrite
                if output_filepath.exists() and not config.overwrite:
                    raise FileExistsError(f"Output file already exists: {output_filepath}")
                
                # Write output data
                _write_output_data(validated_result.data, output_filepath)
                
                # Prepare comprehensive metadata
                execution_time = time.time() - start_time
                metadata = {
                    'Description': validated_result.description,
                    'ProcessingPipeline': config.pipeline_name,
                    'InputFile': str(input_path),
                    'OutputFile': str(output_filepath),
                    'ProcessingTime': round(execution_time, 3),
                    'ProcessingDate': datetime.now().isoformat(),
                    'BIDSEntities': bids_entities,
                    'FunctionName': func.__name__,
                    'FunctionModule': func.__module__,
                    **validated_result.metadata  # Include any additional metadata
                }
                
                # Add PyBIDS dataset information if available
                if config.bids_layout:
                    try:
                        dataset_desc = config.bids_layout.get_dataset_description()
                        if dataset_desc:
                            metadata['DatasetName'] = dataset_desc.get('Name', 'Unknown')
                            metadata['BIDSVersion'] = dataset_desc.get('BIDSVersion', 'Unknown')
                    except Exception:
                        pass  # Continue without dataset info
                
                # Create sidecar JSON file if enabled
                sidecar_filepath = None
                if config.create_sidecar:
                    # Handle sidecar filename to avoid overwriting output file
                    if output_filepath.suffix.lower() == CONFIG.JSON_EXTENSION:
                        # If output is already JSON, create sidecar with different name
                        sidecar_filepath = output_filepath.with_name(
                            output_filepath.stem + f'_sidecar{CONFIG.JSON_EXTENSION}'
                        )
                    else:
                        # Standard case: add .json extension
                        sidecar_filepath = output_filepath.with_suffix(CONFIG.BIDS_SIDECAR_SUFFIX)
                    
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
                    'ProcessingPipeline': config.pipeline_name,
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
    if config.bids_layout:
        try:
            file_obj = config.bids_layout.get_file(str(input_path))
            if file_obj:
                layout_entities = file_obj.get_entities()
                # Merge with parsed entities, preferring layout entities
                entities.update({k: str(v) for k, v in layout_entities.items() if v is not None})
        except Exception:
            pass  # Continue with parsed entities only
    
    return entities


def _construct_output_path(
    input_path: Path, 
    config: NeuProcessDecoratorConfig, 
    output_entities: Optional[Dict[str, str]] = None,
    suffix: Optional[str] = None,
    extension: Optional[str] = None
) -> Path:
    """
    Construct BIDS-compliant output path using PyBIDS with entity override support.
    
    This function creates output paths by:
    1. Extracting entities from the input file path
    2. Allowing functions to override/add entities via output_entities
    3. Using intelligent defaults when entities are not specified
    4. Constructing BIDS-compliant paths using PyBIDS or manual fallback
    
    Args:
        input_path: Input file path
        config: Decorator configuration
        output_entities: Dict of entities from function output to override/add to input entities.
                        Common entities include:
                        - 'desc': Description suffix (e.g., 'preprocessed', 'smoothed')
                        - 'space': Coordinate space (e.g., 'MNI152', 'T1w')
                        - 'datatype': BIDS datatype directory (e.g., 'anat', 'func', 'dwi')
                        - 'extension': File extension (e.g., '.nii.gz', '.json')
                        - Any other BIDS entities (e.g., 'res', 'atlas', 'fwhm')
        suffix: Legacy parameter - will be overridden by output_entities['desc'] if present
        extension: Legacy parameter - will be overridden by output_entities['extension'] if present
        
    Returns:
        Path: BIDS-compliant output file path
        
    Examples:
        # Function specifies custom entities
        output_entities = {
            'desc': 'preprocessed',
            'space': 'MNI152', 
            'extension': '.nii.gz'
        }
        # Result: derivatives/pipeline/sub-01/func/sub-01_space-MNI152_desc-preprocessed_bold.nii.gz
        
        # Function changes datatype
        output_entities = {
            'desc': 'transformed',
            'datatype': 'anat'
        }
        # Result: derivatives/pipeline/sub-01/anat/sub-01_desc-transformed_T1w.nii.gz
        
        # No entities specified - uses pipeline_name as desc
        output_entities = {}
        # Result: derivatives/pipeline/sub-01/func/sub-01_desc-pipeline_name_bold.nii.gz
    """
    
    # Extract entities from input path
    entities = _extract_bids_entities(input_path, config)
    
    # Override/add entities from function output
    if output_entities:
        entities.update(output_entities)
    
    # Handle legacy suffix parameter - only use if 'desc' not in output_entities
    if 'desc' not in entities:
        if suffix is not None:
            entities['desc'] = suffix
        else:
            # Only use pipeline_name as default if no desc entity provided
            entities['desc'] = config.pipeline_name
    
    # Handle legacy extension parameter - only use if 'extension' not in output_entities
    if 'extension' not in entities:
        if extension is not None:
            entities['extension'] = extension
        else:
            entities['extension'] = input_path.suffix
    
    # Use PyBIDS build_path
    if config.bids_layout:
        try:
            # Determine derivatives directory - use pipeline_name if derivatives_dir is default
            if config.derivatives_dir == CONFIG.DERIVATIVES_DIR:
                derivatives_name = config.pipeline_name
            else:
                derivatives_name = config.derivatives_dir or config.pipeline_name
            
            # Add pipeline to entities for path construction
            entities['pipeline'] = derivatives_name
            
            # Build the path
            built_path = config.bids_layout.build_path(
                entities,
                path_patterns=[
                    'derivatives/{pipeline}/sub-{subject}/[ses-{session}/]{datatype}/sub-{subject}[_ses-{session}][_task-{task}][_acq-{acquisition}][_run-{run}][_space-{space}]_desc-{desc}{extension}',
                    'derivatives/{pipeline}/sub-{subject}/[ses-{session}/]func/sub-{subject}[_ses-{session}][_task-{task}][_acq-{acquisition}][_run-{run}][_space-{space}]_desc-{desc}_bold{extension}',
                    'derivatives/{pipeline}/sub-{subject}/[ses-{session}/]anat/sub-{subject}[_ses-{session}][_acq-{acquisition}][_run-{run}][_space-{space}]_desc-{desc}_T1w{extension}'
                ],
                validate=False,
                absolute_paths=True
            )
            
            if built_path:
                return Path(built_path)
                
        except Exception:
            pass  # Fall back to manual construction
    
    # Manual path construction as fallback
    # Determine derivatives directory - use pipeline_name if derivatives_dir is default
    if config.derivatives_dir == CONFIG.DERIVATIVES_DIR:
        derivatives_name = config.pipeline_name
    else:
        derivatives_name = config.derivatives_dir or config.pipeline_name
    derivatives_path = Path(config.bids_root) / "derivatives" / derivatives_name
    
    # Build subject directory path
    subject_id = entities.get('sub') or entities.get('subject', 'unknown')
    subject_dir = derivatives_path / f"sub-{subject_id}"
    
    # Add session directory if present
    session_id = entities.get('ses') or entities.get('session')
    if session_id:
        subject_dir = subject_dir / f"ses-{session_id}"
    
    # Determine datatype (use extracted entities first, then infer from input path)
    datatype = entities.get('datatype', 'func')  # Use extracted datatype if available
    if datatype == 'func' and 'datatype' not in entities:  # Only infer if not already determined
        if 'anat' in str(input_path):
            datatype = 'anat'
        elif 'dwi' in str(input_path):
            datatype = 'dwi'
        elif 'fmap' in str(input_path):
            datatype = 'fmap'
        elif any(x in str(input_path).lower() for x in ['t1w', 't2w', 'flair', 'pd']):
            datatype = 'anat'
        elif any(x in str(input_path).lower() for x in ['bold', 'task-']):
            datatype = 'func'
    
    output_dir = subject_dir / datatype
    
    # Construct filename
    filename_parts = [f"sub-{subject_id}"]
    
    # Add entities in BIDS order
    entity_order = ['ses', 'task', 'acq', 'run', 'space']
    entity_map = {
        'ses': entities.get('ses') or entities.get('session'),
        'task': entities.get('task'),
        'acq': entities.get('acq') or entities.get('acquisition'),
        'run': entities.get('run'),
        'space': entities.get('space')
    }
    
    for entity in entity_order:
        value = entity_map[entity]
        if value:
            filename_parts.append(f"{entity}-{value}")
    
    # Add description suffix
    desc_value = entities.get('desc')
    if desc_value:
        filename_parts.append(f"desc-{desc_value}")
    
    # Add modality suffix (infer from input or use generic)
    if datatype == 'func':
        filename_parts.append('bold')
    elif datatype == 'anat':
        if 'T1w' in input_path.name:
            filename_parts.append('T1w')
        elif 'T2w' in input_path.name:
            filename_parts.append('T2w')
        else:
            filename_parts.append('T1w')  # Default
    
    extension_value = entities.get('extension', input_path.suffix)
    filename = "_".join(filename_parts) + extension_value
    
    return output_dir / filename


def _infer_datatype(input_path: Path) -> str:
    """
    Infer BIDS datatype from input path.
    
    Args:
        input_path: Input file path
        
    Returns:
        BIDS datatype (e.g., 'anat', 'func', 'dwi')
    """
    path_str = str(input_path).lower()
    
    if 'anat' in path_str or any(x in path_str for x in ['t1w', 't2w', 'flair', 'pd']):
        return 'anat'
    elif 'func' in path_str or any(x in path_str for x in ['bold', 'task-']):
        return 'func'
    elif 'dwi' in path_str or any(x in path_str for x in ['dwi', 'bval', 'bvec']):
        return 'dwi'
    elif 'fmap' in path_str:
        return 'fmap'
    else:
        return 'derivatives'  # Default for processed data


def _write_output_data(data: Any, output_path: Path) -> None:
    """
    Write output data to file based on file extension.
    
    Args:
        data: Data to write
        output_path: Path to output file
    """
    extension = output_path.suffix.lower()
    
    if extension == '.json':
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    elif extension in ['.txt', '.csv']:
        with open(output_path, 'w') as f:
            if isinstance(data, str):
                f.write(data)
            else:
                f.write(str(data))
    elif extension in ['.nii', '.gz']:
        # For neuroimaging data, assume it's already in the correct format
        # This would typically require nibabel or similar library
        if hasattr(data, 'to_filename'):
            data.to_filename(output_path)
        else:
            raise ValueError(f"Cannot write data of type {type(data)} to neuroimaging file {output_path}")
    else:
        # Default: try to save as pickle or string
        if isinstance(data, (str, bytes)):
            with open(output_path, 'w' if isinstance(data, str) else 'wb') as f:
                f.write(data)
        else:
            import pickle
            with open(output_path, 'wb') as f:
                pickle.dump(data, f)


def _create_sidecar_file(
    output_filepath: Path,
    function_metadata: Dict[str, Any],
    metrics: Dict[str, Any],
    config: NeuProcessDecoratorConfig,
    execution_time: float,
    input_filepath: Path,
    forced_outputs: Optional[List[str]] = None
) -> Path:
    """
    Create sidecar JSON file with metadata.
    
    Args:
        output_filepath: Path to the output file
        function_metadata: Metadata about the function
        metrics: Metrics from the process
        config: Decorator configuration
        execution_time: Time taken for execution
        input_filepath: Path to the input file
        forced_outputs: List of forced output filepaths
        
    Returns:
        Path to the created sidecar file
    """
    # Create sidecar path - if output is already .json, add '_meta' to distinguish
    if output_filepath.suffix.lower() == '.json':
        sidecar_path = output_filepath.with_suffix('.meta.json')
    else:
        sidecar_path = output_filepath.with_suffix('.json')
    
    sidecar_data = {
        "GeneratedBy": {
            "Name": config.pipeline_name,
            "Version": "1.0.0",  # Could be made configurable
            "Description": function_metadata.get("function_docstring", ""),
            "CodeURL": function_metadata.get("module", ""),
        },
        "SourceDatasets": [
            {
                "URL": str(input_filepath),
                "Version": "unknown"
            }
        ],
        "ProcessingDetails": {
            "FunctionName": function_metadata["function_name"],
            "ExecutionTime": execution_time,
            "Timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "Configuration": config.model_dump(exclude={"bids_root"}),
        },
        "Metrics": metrics,
        "OutputFiles": [str(output_filepath)],
        "ForcedOutputFiles": forced_outputs or [],
    }
    
    with open(sidecar_path, 'w') as f:
        json.dump(sidecar_data, f, indent=2)
    
    return sidecar_path


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
