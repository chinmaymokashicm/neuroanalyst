# NeuroAnalyst Process Docker Image: ${name}

## Description
${description}

## Version
${version}

## Author
${author}

## Created At
${created_at}

## Base Docker Image
${base_docker_image}

## Volumes
${container_volumes_bullets}

## Environment Variables
${environment_variables}

## Usage

### Building the Docker Image
To build the Docker image, run the following command:
```bash
cd $$NEUROANALYST_IMAGES/
apptainer build ${process_image_id}.sif ${process_image_id}.def 
```

# Running the Docker Container
To run the Docker container, use the following command:

```bash
apptainer run \
  ${iter_mount_volume_command} \
  ${iter_env_command} \
  ${tag}
```

# Checking Apptainer Installation
Ensure Apptainer is installed and properly set up by running:

```bash
apptainer --version
```

# Updating progress
To keep track of progress, edit your main script to run this bash script at the end of every important stage. This is the only intervention from the user since determining the stages of a process is subject to that process and cannot be easily detected automatically.

```bash
./update_progress.sh
```