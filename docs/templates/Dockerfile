# Base image
FROM $base_image

# Working directory
WORKDIR /app

# Copy current directory to /app
COPY . .

# Install SQLite
# RUN apt-get update && apt-get install -y --no-install-recommends sqlite3 && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN chmod +x $requirements_file && $requirements_exec_prefix $requirements_file

# Start the app
# RUN chmod +x execute.sh update_progress.sh
# CMD ["./execute.sh", "$main_exec_prefix", "$main_file"]
CMD ["$main_exec_prefix", "$main_file"]