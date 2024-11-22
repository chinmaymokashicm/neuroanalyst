from lib.process.create import ProcessExecConfig, ProcessExec

process_exec_config: ProcessExecConfig = ProcessExecConfig(
    output_volumes={
        "data_dir": "/Users/cmokashi/Documents/GitHub/ukb2bids/bids",
        "output_dir": "$PWD/outputs/"
    },
    environment_var_values={
        "BIDS_FILTERS": {"suffix": "T1w", "extension": "nii.gz"}
    }
)

process_exec: ProcessExec = ProcessExec.from_user(
    process_exec_config=process_exec_config,
    process_image_id="PR-050881"
)

# print(process_exec.model_dump_json(indent=4))
# print(process_exec.model_dump())

process_exec.execute()