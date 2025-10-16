from bids import BIDSLayout

def split_by_subject_session(
    bids_layout: BIDSLayout, 
    bids_filters: dict, 
    max_chunk_size: int = 5
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
        
    Returns:
    --------
    list[dict]
        List of dictionaries, where each dictionary contains:
        - 'bids_filters': dict of filters to get files in this chunk
        - 'n_files': number of files in the chunk
    """
    # Validate input
    for key in ["subject", "session"]:
        if key in bids_filters:
            raise ValueError(f"'bids_filters' should not contain '{key}' key. It is handled separately.")
    
    # 1. Get all matching files
    files = bids_layout.get(**bids_filters, return_type="file", target="subject")
    if not files:
        return []

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
                    "n_files": subject_info["n_files"]
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
                        "n_files": session_info["n_files"]
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
                                "n_files": current_chunk["n_files"]
                            }
                        else:
                            # Multiple sessions
                            new_chunk = {
                                "bids_filters": {
                                    **bids_filters,
                                    "subject": subject,
                                    "session": current_chunk["sessions"]
                                },
                                "n_files": current_chunk["n_files"]
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
                        "n_files": current_chunk["n_files"]
                    }
                else:
                    # Multiple sessions
                    new_chunk = {
                        "bids_filters": {
                            **bids_filters,
                            "subject": subject,
                            "session": current_chunk["sessions"]
                        },
                        "n_files": current_chunk["n_files"]
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