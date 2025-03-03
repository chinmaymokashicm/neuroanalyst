# NeuroAnalyst Process Docker Image: ${name}

## Description
${description}

## Version
${version}

## Created At
${created_at}

## Base Docker Image
${base_docker_image}

## Stages
${stages}

## Volumes
${container_volumes_bullets}

## Environment Variables
${environment_variables}

## Usage

### Building the Docker Image
To build the Docker image, run the following command:
```bash
cd ${process_image_id}/
docker build -t '${tag}' .
```

# Running the Docker Container
To run the Docker container, use the following command:

```bash
docker run --name ${name} -d \
  ${iter_mount_volume_command} \
  ${iter_env_command} \
  ${tag}
```

# Checking Docker Installation
Ensure Docker is installed and properly set up by running:

```bash
docker --version
```

# Pulling the Docker Image
If the Docker image is not available locally, it will be pulled automatically. You can also pull it manually using:

```bash
docker pull ${base_docker_image}
```

# Updating progress
To keep track of progress, edit your main script to run this bash script at the end of every important stage. This is the only intervention from the user since determining the stages of a process is subject to that process and cannot be easily detected automatically.

```bash
./update_progress.sh
```