from pathlib import Path
import os, json, shutil, sys

import pandas as pd
from bids.layout import BIDSLayout

data_dir: str = sys.argv[1]  # e.g., "/data/neuroanalysis_test_data"
scope: str = sys.argv[2]  # e.g., "dwiRegionwiseAnalysis"

layout = BIDSLayout(data_dir, validate=False, derivatives=True)
bids_entities: dict = {
    "desc": "dwiRegionwise",
    "suffix": "stats",
    "extension": ".csv"
}

stats_files: list[str] = layout.get(bids_entities, return_type="file", scope=scope)

dfs: list[pd.DataFrame] = []
for stats_file in stats_files:
    df = pd.read_csv(stats_file)
    # Extract entities from filename
    entities = layout.parse_file_entities(stats_file)
    # Add columns for entities
    for key, value in entities.items():
        df[key] = value
    # Create a unique identifier for each file
    df["filepath"] = stats_file
    # Move 'filepath' and entity columns to the front
    first_cols = ["filepath"] + list(entities.keys())
    other_cols = [col for col in df.columns if col not in first_cols]
    df = df[first_cols + other_cols]
    dfs.append(df)
    
# Concatenate all dataframes
combined_df = pd.concat(dfs, ignore_index=True)
# Save to CSV
combined_df.to_csv("combined_stats.csv", index=False)