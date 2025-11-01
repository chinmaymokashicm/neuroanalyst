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
    for key in ["subject", "session"]:
        if key in bids_filters:
            raise ValueError(f"'bids_filters' should not contain '{key}' key. It is handled separately.")

    subject_session_filters: dict = {}
    if subjects is not None:
        subjects = [subject for subject in subjects if subject is not None] # Clean None values
        if subjects: # Only add if list is not empty
            subject_session_filters["subject"] = subjects
            if sessions is not None:
                sessions = [session for session in sessions if session is not None] # Clean None values
                if sessions: # Only add if list is not empty
                    subject_session_filters["session"] = sessions
            
    bids_filters = {**bids_filters, **subject_session_filters}
    
    # 1. Get all matching files
    files = bids_layout.get(**bids_filters, return_type="file", target="subject")
    if not files:
        print("No files found with the given filters.")
        return [{
            "bids_filters": bids_filters,
            "n_files": 0,
            "subject_session_pair": ([], [])
        }]

    # 2. Get metadata for each file: subject and session
    grouped = {}
    for f in files:
        entities = bids_layout.parse_file_entities(f)
        subject = entities.get("subject")
        session = entities.get("session")
        if subject not in grouped:
            grouped[subject] = {"sessions": {}, "n_files": 0}
        if session not in grouped[subject]["sessions"]:
            grouped[subject]["sessions"][session] = {"files": [], "n_files": 0}
        grouped[subject]["sessions"][session]["files"].append(f)
        grouped[subject]["sessions"][session]["n_files"] += 1
        grouped[subject]["n_files"] += 1
        
    # 3. Use a bin packing algorithm to efficiently combine subject-session pairs
    chunks = []
    
    # Sort subjects by descending number of files for better bin packing
    sorted_subjects = sorted(grouped.items(), key=lambda x: x[1]["n_files"], reverse=True)
    
    for subject, subject_info in sorted_subjects:
        if subject_info["n_files"] <= max_chunk_size:
            # Simple case: subject fits in a chunk
            # Try to find an existing chunk with enough space
            added_to_existing = False
            for chunk in chunks:
                # Skip chunks that already have sessions split across subjects
                if "session" in chunk["bids_filters"]:
                    continue
                
                if chunk["n_files"] + subject_info["n_files"] <= max_chunk_size:
                    # Add subject to this chunk
                    subjects = chunk["bids_filters"]["subject"]
                    if isinstance(subjects, str):
                        chunk["bids_filters"]["subject"] = [subjects, subject]
                    else:
                        chunk["bids_filters"]["subject"].append(subject)
                    chunk["n_files"] += subject_info["n_files"]
                    added_to_existing = True
                    break
            
            if not added_to_existing:
                # Create a new chunk for this subject
                new_chunk = {
                    "bids_filters": {**bids_filters, "subject": subject},
                    "n_files": subject_info["n_files"],
                    "subject_session_pair": ([subject], [ None])
                }
                chunks.append(new_chunk)
        else:
            # Complex case: subject exceeds max_chunk_size, handle sessions individually
            sorted_sessions = sorted(subject_info["sessions"].items(), 
                                   key=lambda x: x[1]["n_files"], 
                                   reverse=True)
            
            # First pass: handle sessions that exceed max_chunk_size on their own
            remaining_sessions = []
            for session, session_info in sorted_sessions:
                if session_info["n_files"] > max_chunk_size:
                    # This session must be in its own chunk(s)
                    # Since a session can't be split, put all its files in one chunk
                    new_chunk = {
                        "bids_filters": {
                            **bids_filters,
                            "subject": subject,
                            "session": session
                        },
                        "n_files": session_info["n_files"],
                        "subject_session_pair": ([subject], [session])
                    }
                    chunks.append(new_chunk)
                else:
                    remaining_sessions.append((session, session_info))
            
            # Second pass: bin pack remaining sessions
            current_chunk = {"sessions": [], "n_files": 0}
            for session, session_info in remaining_sessions:
                if current_chunk["n_files"] + session_info["n_files"] <= max_chunk_size:
                    # Add session to current chunk
                    current_chunk["sessions"].append(session)
                    current_chunk["n_files"] += session_info["n_files"]
                else:
                    # Finalize current chunk and start a new one
                    if current_chunk["sessions"]:
                        if len(current_chunk["sessions"]) == 1:
                            # Just one session
                            new_chunk = {
                                "bids_filters": {
                                    **bids_filters,
                                    "subject": subject,
                                    "session": current_chunk["sessions"][0]
                                },
                                "n_files": current_chunk["n_files"],
                                "subject_session_pair": ([subject], [current_chunk["sessions"][0]])
                            }
                        else:
                            # Multiple sessions
                            new_chunk = {
                                "bids_filters": {
                                    **bids_filters,
                                    "subject": subject,
                                    "session": current_chunk["sessions"]
                                },
                                "n_files": current_chunk["n_files"],
                                "subject_session_pair": ([subject], current_chunk["sessions"])
                            }
                        chunks.append(new_chunk)
                    
                    # Start a new chunk with this session
                    current_chunk = {"sessions": [session], "n_files": session_info["n_files"]}
            
            # Don't forget the last chunk
            if current_chunk["sessions"]:
                if len(current_chunk["sessions"]) == 1:
                    # Just one session
                    new_chunk = {
                        "bids_filters": {
                            **bids_filters,
                            "subject": subject,
                            "session": current_chunk["sessions"][0]
                        },
                        "n_files": current_chunk["n_files"],
                        "subject_session_pair": ([subject], [current_chunk["sessions"][0]])
                    }
                else:
                    # Multiple sessions
                    new_chunk = {
                        "bids_filters": {
                            **bids_filters,
                            "subject": subject,
                            "session": current_chunk["sessions"]
                        },
                        "n_files": current_chunk["n_files"],
                        "subject_session_pair": ([subject], current_chunk["sessions"])
                    }
                chunks.append(new_chunk)
    
    # Final validation: verify each chunk's file count matches our expectation
    for chunk in chunks:
        # Get the actual count of files with these filters
        actual_count = len(bids_layout.get(**chunk["bids_filters"], return_type="file"))
        
        # Update the count in case our calculations were off
        # chunk["n_files"] = actual_count
        assert chunk["n_files"] == actual_count, (
            f"Chunk file count mismatch: expected {chunk['n_files']}, got {actual_count}. "
            f"Filters: {chunk['bids_filters']}"
        )

    assert sum([chunk["n_files"] for chunk in chunks]) == len(files), (
        f"Total file count mismatch: expected {len(files)}, got {sum([chunk['n_files'] for chunk in chunks])}."
    )

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