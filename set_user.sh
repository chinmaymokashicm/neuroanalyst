#!/usr/bin/env bash

set -euo pipefail

# -----------------------------
# Configuration & validation
# -----------------------------

if [[ -z "${NEUROANALYST_HOME:-}" ]]; then
    echo "ERROR: NEUROANALYST_HOME is not set."
    echo "Please export NEUROANALYST_HOME before running this script."
    exit 1
fi

USERS_DIR="${NEUROANALYST_HOME}/users"
mkdir -p "$USERS_DIR"

USERNAME_REGEX='^[a-zA-Z][a-zA-Z0-9_-]{2,31}$'

# -----------------------------
# Helper functions
# -----------------------------

is_valid_username() {
    local username="$1"
    [[ "$username" =~ $USERNAME_REGEX ]]
}

create_user_dir() {
    local username="$1"
    local user_path="${USERS_DIR}/${username}"

    if [[ -d "$user_path" ]]; then
        echo "⚠️  User '$username' already exists — skipping."
        return
    fi

    mkdir "$user_path"
    echo "✅ Created user directory: $user_path"
}

# -----------------------------
# Show existing users
# -----------------------------

echo "Existing users in ${USERS_DIR}:"
if compgen -G "${USERS_DIR}/*" > /dev/null; then
    ls -1 "$USERS_DIR"
else
    echo "  (none)"
fi
echo

# -----------------------------
# Input handling
# -----------------------------

if [[ $# -eq 1 ]]; then
    USERS_FILE="$1"

    if [[ ! -f "$USERS_FILE" ]]; then
        echo "ERROR: File not found: $USERS_FILE"
        exit 1
    fi

    echo "Reading usernames from file: $USERS_FILE"
    while IFS= read -r username || [[ -n "$username" ]]; do
        # Trim whitespace
        username="$(echo "$username" | xargs)"

        # Skip empty lines or comments
        [[ -z "$username" || "$username" =~ ^# ]] && continue

        if ! is_valid_username "$username"; then
            echo "❌ Invalid username '$username' — skipping."
            continue
        fi

        create_user_dir "$username"
    done < "$USERS_FILE"

else
    echo "Enter usernames (one per line). Press Ctrl+D when done:"
    while IFS= read -r username; do
        [[ -z "$username" ]] && continue

        if ! is_valid_username "$username"; then
            echo "❌ Invalid username '$username'."
            echo "   Must start with a letter and contain only letters, numbers, '_' or '-'."
            continue
        fi

        create_user_dir "$username"
    done
fi

# Set the first user to NEUROANALYST_USER as the default user if none exists
if [[ -z "${NEUROANALYST_USER:-}" ]]; then
    first_user="$(ls -1 "$USERS_DIR" | head -n 1 || true)"
    if [[ -n "$first_user" ]]; then
        echo
        echo "Setting NEUROANALYST_USER to the first user: $first_user"
        echo "export NEUROANALYST_USER=${first_user}" >> ~/.bashrc
        export NEUROANALYST_USER="$first_user"
    else
        echo
        echo "No users found to set as NEUROANALYST_USER. Creating default user 'default_user'."
        create_user_dir "default_user"
        echo "export NEUROANALYST_USER=default_user" >> ~/.bashrc
        export NEUROANALYST_USER="default_user"
    fi
fi

