from lib.process.create import ProcessImage, WorkingDirectory

working_directory: WorkingDirectory = WorkingDirectory.from_user(
    root_dir="working_dirs/count_files/",
    main_file="main.py",
    requirements_file="install_requirements.sh",
    main_exec_prefix="python",
    requirements_exec_prefix="bash"
)

process_image: ProcessImage = ProcessImage(
    name="Count Files",
    tag="count-files",
    description="Count the number of files in a BIDS directory.",
    base_docker_image="python:3.12",
    working_directory=working_directory,
    stages=["Loaded filepaths", "Counted files", "Saved the number of files to a file"]
)

process_image_id, dest_dir = process_image.create_image_workdir()
process_image.build_image(dest_dir=dest_dir)


# print(process_image)