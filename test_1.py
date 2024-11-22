from lib.process.create import ProcessExecConfig, ProcessExec
from lib.pipeline.build import PipelineStep, Pipeline

pr_id_count_files: str = "PR-668141"
pr_id_regional_volumes: str = "PR-426083"

def generate_process_exec(process_exec_config: ProcessExecConfig, process_image_id: str) -> ProcessExec:
    process_exec: ProcessExec = ProcessExec.from_user(
        process_exec_config=process_exec_config,
        process_image_id=process_image_id
    )
    return process_exec

process_exec_config_count_files: ProcessExecConfig = ProcessExecConfig(
    output_volumes={
        "data_dir": "/Users/cmokashi/Documents/GitHub/ukb2bids/bids",
        "output_dir": "$PWD/outputs/"
    },
    environment_var_values={
        "BIDS_FILTERS": {"datatype": "func", "extension": "nii.gz"}
    }
)

# ==================================================================================================

process_exec_regional_volumes_config: ProcessExecConfig = ProcessExecConfig(
    output_volumes={
        "data_dir": "/Users/cmokashi/Documents/GitHub/ukb2bids/bids",
        "output_dir": "$PWD/outputs/"
    },
    environment_var_values={
        "BIDS_FILTERS": {"datatype": "anat", "extension": "nii.gz", "suffix": "T1w"}
    }
)

# Build pipeline steps
step1: PipelineStep = PipelineStep(name="Count Files", process_execs=[generate_process_exec(process_exec_config_count_files, pr_id_count_files)])
step2: PipelineStep = PipelineStep(name="Regional Volumes", process_execs=[generate_process_exec(process_exec_regional_volumes_config, pr_id_regional_volumes)])
step3: PipelineStep = PipelineStep(name="Count Files again", process_execs=[generate_process_exec(process_exec_config_count_files, pr_id_count_files)])
step4: PipelineStep = PipelineStep(name="Count Files and Regional Volumes", process_execs=[generate_process_exec(process_exec_config_count_files, pr_id_count_files), generate_process_exec(process_exec_regional_volumes_config, pr_id_regional_volumes)])

# Construct pipeline
pipeline: Pipeline = Pipeline(name="Test Pipeline", description="Pipeline to convert UKB data to BIDS format.", steps=[step1, step2, step3, step4])

# Execute pipeline
pipeline.execute()