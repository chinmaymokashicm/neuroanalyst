# from lib.process.create import ProcessImage, WorkingDirectory

# config: list = [
#     {
#         "working_directory": {
#             "root_dir": "working_dirs/count_files/",
#             "main_file": "main.py",
#             "requirements_file": "install_requirements.sh",
#             "main_exec_prefix": "python",
#             "requirements_exec_prefix": "bash"
#         },
#         "process_image": {
#             "name": "Count Files",
#             "tag": "count-files",
#             "description": "Count the number of files in a BIDS directory.",
#             "base_docker_image": "python:3.12",
#             "stages": ["Loaded filepaths", "Counted files", "Saved the number of files to a file"],
#             "expected_outputs": ["n_files"]
#         }
#     },
#     {
#         "working_directory": {
#             "root_dir": "working_dirs/regional_volumes/",
#             "main_file": "main.py",
#             "requirements_file": "install_requirements.sh",
#             "main_exec_prefix": "python",
#             "requirements_exec_prefix": "bash"
#         },
#         "process_image": {
#             "name": "Regional Volumes",
#             "tag": "regional-volumes",
#             "description": "Extract region-wise signals from T1w images. Uses the Harvard-Oxford atlas.",
#             "base_docker_image": "python:3.12",
#             "stages": ["Loaded images", "Loaded the Harvard-Oxford atlas", "Extracted region-wise signals", "Saved the region-wise signals to a file"],
#             "expected_outputs": ["region_signals"]
#         }
#     }
# ]

# for process_config in config:
#     working_directory = WorkingDirectory.from_user(**process_config["working_directory"])
#     process_image = ProcessImage(working_directory=working_directory, **process_config["process_image"])
    
#     print(f"Working directory: {working_directory}")
#     print(f"Process image: {process_image}")
#     print("\n")
    
#     process_image_id, dest_dir = process_image.create_image_workdir()
#     print(f"Process image ID: {process_image_id}")
#     print(f"Destination directory: {dest_dir}")
#     process_image.build_image(dest_dir=dest_dir)