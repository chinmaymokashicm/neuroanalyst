#!/bin/bash

# Ensure the database path is set
if [ -z "$DB_PATH" ]; then
    echo "Error: DB_PATH environment variable is not set."
    exit 1
fi

# Find the next incomplete stage and mark it as complete
echo "Updating progress in the SQLite database at $DB_PATH..."

sqlite3 "$DB_PATH" <<EOF
BEGIN TRANSACTION;
-- Update the first incomplete stage to 'complete' and set the timestamp
UPDATE stages
SET status = 'complete',
    completed_at = CURRENT_TIMESTAMP
WHERE id = (SELECT id FROM stages WHERE status = 'incomplete' ORDER BY id LIMIT 1);

-- Check if any stage was updated
SELECT COUNT(*) AS updated_stages FROM stages WHERE status = 'complete' AND completed_at = CURRENT_TIMESTAMP;
COMMIT;
EOF
