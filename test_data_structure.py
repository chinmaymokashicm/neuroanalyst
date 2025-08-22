#!/usr/bin/env python3

import tempfile
import json
from pathlib import Path
from app.models.process.wrapper.core import neuprocess_decorator, NeuProcessDecoratorConfig
import numpy as np

# Create a test file
with tempfile.TemporaryDirectory() as temp_dir:
    bids_root = Path(temp_dir)
    input_file = bids_root / 'sub-02' / 'ses-02' / 'func' / 'sub-02_ses-02_task-rest_run-01_bold.nii.gz'
    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text('dummy data')
    
    config = NeuProcessDecoratorConfig(
        pipeline_name='functional_connectivity',
        bids_root=bids_root,
        overwrite=True
    )
    
    @neuprocess_decorator(config)
    def calculate_functional_connectivity(input_filepath):
        n_regions = 100
        connectivity_matrix = np.random.rand(n_regions, n_regions)
        np.fill_diagonal(connectivity_matrix, 1.0)
        
        mean_connectivity = float(np.mean(connectivity_matrix[np.triu_indices(n_regions, k=1)]))
        max_connectivity = float(np.max(connectivity_matrix[np.triu_indices(n_regions, k=1)]))
        
        output_data = {
            'connectivity_matrix': connectivity_matrix.tolist(),
            'n_regions': n_regions,
            'analysis_type': 'pearson_correlation'
        }
        
        result_dict = {
            'data': output_data,
            'description': 'Functional connectivity analysis using Pearson correlation',
            'metadata': {
                'metrics': {
                    'mean_connectivity': mean_connectivity,
                    'max_connectivity': max_connectivity,
                    'n_regions': n_regions,
                    'matrix_density': float(np.count_nonzero(connectivity_matrix > 0.5) / (n_regions * n_regions))
                },
                'output_bids_entities': {
                    'desc': 'connectivity',
                    'suffix': 'matrix',
                    'extension': '.json'
                }
            }
        }
        
        print("Function returning:", list(result_dict.keys()))
        print("Data contains:", list(result_dict['data'].keys()))
        return result_dict
    
    result = calculate_functional_connectivity(str(input_file))
    
    if result.success:
        print(f'Output file path: {result.output_filepath}')
        print(f'Sidecar file path: {result.sidecar_filepath}')
        print(f'Same file? {result.output_filepath == result.sidecar_filepath}')
        
        print('\nOutput file contents:')
        with open(result.output_filepath, 'r') as f:
            output_content = json.load(f)
        print(f'Keys in output file: {list(output_content.keys())}')
        print(f'n_regions available: {"n_regions" in output_content}')
        
        if result.output_filepath != result.sidecar_filepath:
            print('\nSidecar file contents:')
            with open(result.sidecar_filepath, 'r') as f:
                sidecar_content = json.load(f)
            print(f'Keys in sidecar file: {list(sidecar_content.keys())}')
            print(f'Metrics available: {"metrics" in sidecar_content}')
            if 'metrics' in sidecar_content:
                print(f'Metrics keys: {list(sidecar_content["metrics"].keys())}')
        else:
            print('\nOutput and sidecar are the same file!')
    else:
        print(f'Failed: {result.error_message}')
