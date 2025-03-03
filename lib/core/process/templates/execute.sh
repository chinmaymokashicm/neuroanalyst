#!/bin/bash

# Usage: execute.sh <exec_prefix> <main_file> <stages>

exec_prefix=$1
main_file=$2
stages=$3

# Set DB_PATH as environment variable.
export DB_PATH="/output_dir/progress.db"

# Ensure the database directory exists:
mkdir -p "$(dirname "$DB_PATH")"

# Create the SQLite database with a progress table, initializing rows for each stage:
echo "Initializing SQLite database at $DB_PATH..."
sqlite3 "$DB_PATH" <<EOF
CREATE TABLE IF NOT EXISTS stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage_name TEXT NOT NULL,
    status TEXT DEFAULT 'incomplete',
    completed_at TIMESTAMP
);

DELETE FROM stages; -- Reset stages in case the script is rerun
EOF

# Split the stages string into an array by the "," delimiter:
IFS=',' read -ra stage_array <<< "$stages"

# Insert stages into the database:
for stage in "${stage_array[@]}"; do
    sqlite3 "$DB_PATH" <<EOF
INSERT INTO stages (stage_name) VALUES ('$stage');
EOF
done
echo "Inserted ${#stage_array[@]} stages into the database."

# Execute the main file:
echo "Executing main file: $main_file"
$exec_prefix $main_file 