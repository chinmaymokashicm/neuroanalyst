from lib.process.create import spawn_container

process_image_id: str = "PI-850811"
process_image_name: str = "count-files"

container_name, docker_run_command = spawn_container(
    process_image_id, 
    process_image_name, 
    {
        "data_dir": "/Users/cmokashi/Documents/GitHub/ukb2bids/bids",
        "output_dir": f"$PWD/outputs/{process_image_name}"
    },
    {
        "BIDS_FILTERS": {"datatype": "anat"}
    }
)

print(f"Container name: {container_name}")
print(f"Docker run command: {docker_run_command}")