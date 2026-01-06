import json, subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from bids import BIDSLayout
from pydantic import validate_call, ConfigDict

allow_arbitrary_config = ConfigDict(arbitrary_types_allowed=True)

def get_bids_files(bids_filters: dict, scope: str, bids_root: Path, relative_path: bool = False, return_as_list: bool = True) -> List[str] | str:
    """
    Retrieve BIDS files for a given scope from the BIDS dataset.
    
    Parameters:
    -----------
    bids_filters : dict
        Filters to apply to the BIDS query.
    scope : str
        The scope to filter files by (e.g., 'subject', 'session', etc.).
    bids_root : Path
        The root path of the BIDS dataset.
    relative_path : bool, optional
        Whether to return file paths as relative to the BIDS root (default: False).
    return_as_list : bool, optional
        Whether to return the file paths as a list (default: True). If False, returns
        
    Returns:
    --------
    List[str] | str
        List of file paths matching the specified scope. If return_as_list is False, returns a single
        string with file paths joined by newlines.
    """
    # Remove 'scope' and 'return_type' from filters if present
    bids_filters = {k: v for k, v in bids_filters.items() if k not in ["scope", "return_type"]}
    layout = BIDSLayout(str(bids_root), validate=False)
    files = layout.get(**bids_filters, scope=scope, return_type="file")
    if relative_path:
        files = [str(Path(f).relative_to(bids_root)) for f in files]
    if return_as_list:
        return files
    else:
        return "\n".join(files)

@validate_call(config=allow_arbitrary_config)
def split_by_subject_session(
    bids_layout: BIDSLayout, 
    bids_filters: dict, 
    max_chunk_size: int = 5,
    subjects: Optional[list[str]] = None,
    sessions: Optional[list[str]] = None
) -> list[dict]:
    """
    Split a BIDS query into the minimum number of filter dicts such that
    each filter returns <= max_chunk_size files.
    
    This function uses a bin packing algorithm to create chunks of files based on subject and session,
    ensuring that each chunk contains no more than max_chunk_size files. It maintains the integrity
    of subject-session pairs to avoid splitting related data.
    
    Parameters:
    -----------
    bids_layout : BIDSLayout
        The BIDS layout object.
    bids_filters : dict
        Filters to apply to the BIDS query. Should not contain 'subject' or 'session' keys.
    max_chunk_size : int, optional
        Maximum number of files per chunk (default: 5).
    subjects : list[str], optional
        List of subjects to consider. If None, all subjects are considered.
    sessions : list[str], optional
        List of sessions to consider, only if subjects is provided. If None, all sessions are considered.

    Returns:
    --------
    list[dict]
        List of dictionaries, where each dictionary contains:
        - 'bids_filters': dict of filters to get files in this chunk
        - 'n_files': number of files in the chunk
        - 'subject_session_pair': ([subjects], [sessions]) pair to get this chunk.
    Raises:
    -------
    ValueError
        If 'subject' or 'session' keys are present in bids_filters.
    """
    # Validate input
    for key in ("subject", "session"):
        if key in bids_filters:
            raise ValueError(f"'bids_filters' must not include '{key}'")

    base_filters = dict(bids_filters)

    if subjects:
        base_filters["subject"] = [s for s in subjects if s is not None]
    if sessions:
        base_filters["session"] = [s for s in sessions if s is not None]

    # ---- Collect files ----------------------------------------------
    files = bids_layout.get(**base_filters, return_type="file")
    if not files:
        return []

    # ---- Group by subject → session --------------------------------
    grouped: dict[str, dict[str, list[str]]] = {}

    for f in files:
        ent = bids_layout.parse_file_entities(f)
        subj = ent.get("subject")
        ses = ent.get("session")

        grouped.setdefault(subj, {}).setdefault(ses, []).append(f)

    # Precompute counts
    subject_counts = {
        s: sum(len(v) for v in sessions.values())
        for s, sessions in grouped.items()
    }

    chunks: list[dict] = []

    # ---- Phase A: pack whole subjects (no session key) ---------------
    subject_bins: list[dict] = []

    for subject, n_files in sorted(
        subject_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        if n_files > max_chunk_size:
            continue  # handled in phase B

        placed = False
        for bin_ in subject_bins:
            if bin_["n_files"] + n_files <= max_chunk_size:
                bin_["subjects"].append(subject)
                bin_["n_files"] += n_files
                placed = True
                break

        if not placed:
            subject_bins.append({
                "subjects": [subject],
                "n_files": n_files
            })

    for bin_ in subject_bins:
        filters = dict(bids_filters)
        filters["subject"] = bin_["subjects"]

        chunks.append({
            "bids_filters": filters,
            "n_files": bin_["n_files"],
            "subject_session_pair": (bin_["subjects"], None)
        })

    # ---- Phase B: split large subjects by session --------------------
    for subject, sessions_dict in grouped.items():
        if subject_counts[subject] <= max_chunk_size:
            continue

        sessions_sorted = sorted(
            sessions_dict.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        current_sessions: list[str] = []
        current_count = 0

        for session, files_ in sessions_sorted:
            n = len(files_)

            if n > max_chunk_size:
                # session alone, even if oversized
                chunks.append({
                    "bids_filters": {
                        **bids_filters,
                        "subject": subject,
                        "session": session
                    },
                    "n_files": n,
                    "subject_session_pair": ([subject], [session])
                })
                continue

            if current_count + n <= max_chunk_size:
                current_sessions.append(session)
                current_count += n
            else:
                # flush current
                chunks.append({
                    "bids_filters": {
                        **bids_filters,
                        "subject": subject,
                        "session": current_sessions if len(current_sessions) > 1 else current_sessions[0]
                    },
                    "n_files": current_count,
                    "subject_session_pair": ([subject], current_sessions)
                })
                current_sessions = [session]
                current_count = n

        if current_sessions:
            chunks.append({
                "bids_filters": {
                    **bids_filters,
                    "subject": subject,
                    "session": current_sessions if len(current_sessions) > 1 else current_sessions[0]
                },
                "n_files": current_count,
                "subject_session_pair": ([subject], current_sessions)
            })

    # ---- Final validation -------------------------------------------
    total = 0
    for c in chunks:
        actual = len(bids_layout.get(**c["bids_filters"], return_type="file"))
        assert actual == c["n_files"], (
            f"Mismatch: expected {c['n_files']}, got {actual} "
            f"for {c['bids_filters']}"
        )
        total += actual
    
    if total != len(files):
        raise RuntimeError(f"Total mismatch: expected {len(files)}, got {total}")

    return chunks

def validate_bids_dataset(dataset_path: str | Path, ignore_warnings: bool = False) -> Dict[str, Any]:
    """
    Validate a BIDS dataset using the BIDS Validator.
    
    Args:
        dataset_path: Path to the BIDS dataset to validate.
        ignore_warnings: Whether to ignore warnings during validation.
    Returns:
        A dictionary containing the validation results.
    Raises:
        FileNotFoundError: If the dataset path does not exist.
        RuntimeError: If the bids-validator is not installed.
    """
    # Run the BIDS validator
    cmd = ["bids-validator", str(dataset_path)]
    if ignore_warnings:
        cmd.append("--ignoreWarnings")

    # Run validator and capture output
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True
    )

    # Try to parse the JSON output from the validator
    validation_details = {}
    try:
        # Look for JSON in stdout
        stdout = result.stdout
        if stdout:
            # Try to find and extract JSON part
            json_start = stdout.find("{")
            json_end = stdout.rfind("}")
            if json_start >= 0 and json_end > json_start:
                json_part = stdout[json_start:json_end+1]
                validation_details = json.loads(json_part)
    except Exception:
        # If JSON parsing fails, use raw output
        validation_details = {
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    return validation_details