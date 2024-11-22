import os, json, subprocess

from bids import BIDSLayout

layout = BIDSLayout("/bids_dir/")

bids_filters: dict[str, str] = json.loads(os.environ.get("BIDS_FILTERS", "{}"))

filepaths: list[str] = layout.get(**bids_filters)

# Stage 1: Loaded filepaths
subprocess.run("./update_progress.sh", check=True)

n_files: int = len(filepaths)

# Stage 2: Counted files
subprocess.run("./update_progress.sh", check=True)

# Save the number of files to a file
with open("/output_dir/n_files.json", "w") as f:
    json.dump({"n_files": n_files}, f, indent=4)

# Stage 3: Saved the number of files to a file
subprocess.run("./update_progress.sh", check=True)