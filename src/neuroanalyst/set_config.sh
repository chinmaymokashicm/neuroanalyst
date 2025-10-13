#!/bin/bash
# filepath: setup_bids_config.sh

# # Check if NEUROANALYST_CONFIG environment variable is set
# if [ -z "$NEUROANALYST_CONFIG" ]; then
#     echo "Error: NEUROANALYST_CONFIG environment variable is not set."
#     echo "Please set it to the directory where configuration files should be stored."
#     exit 1
# fi

# # Ensure the directory exists
# if [ ! -d "$NEUROANALYST_CONFIG" ]; then
#     echo "Creating directory $NEUROANALYST_CONFIG"
#     mkdir -p "$NEUROANALYST_CONFIG"
# fi

# Define the output file path
CONFIG_FILE="bids_with_desc.json"

# Check if the file already exists
if [ -f "$CONFIG_FILE" ]; then
    echo "$CONFIG_FILE already exists. Skipping creation."
    exit 0
fi

# Write the JSON content to the file
cat > "$CONFIG_FILE" << 'EOF'
{
  "entities": {
    "subject": {"pattern": "sub-(?P<subject>[a-zA-Z0-9]+)"},
    "session": {"pattern": "ses-(?P<session>[a-zA-Z0-9]+)"},
    "acquisition": {"pattern": "acq-(?P<acquisition>[a-zA-Z0-9]+)"},
    "run": {"pattern": "run-(?P<run>[0-9]+)"},
    "desc": {"pattern": "desc-(?P<desc>[a-zA-Z0-9]+)"},
    "suffix": {"pattern": "(?P<suffix>[a-zA-Z0-9]+)"}
  },
  "path_patterns": [
    "[sub-{subject}/][ses-{session}/]{datatype}/sub-{subject}_[ses-{session}_][acq-{acquisition}_][run-{run}_][desc-{desc}_][{suffix}]{extension}"
  ]
}
EOF

# Check if the file was created successfully
if [ -f "$CONFIG_FILE" ]; then
    echo "Successfully created $CONFIG_FILE"
    echo "BIDS configuration with 'desc' entity is now available."
else
    echo "Error: Failed to create $CONFIG_FILE"
    exit 1
fi