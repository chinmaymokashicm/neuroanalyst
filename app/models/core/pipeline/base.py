from pathlib import Path, PosixPath
from typing import Optional, Any
import json

from pydantic import BaseModel, DirectoryPath, FilePath, Field, field_validator
from rich.progress import track
    
def update_participants_json(participants_dict: Optional[dict], overwrite: bool = False, **kwargs) -> dict[str, Any]:
    """
    Add/update participants.json information.
    """
    default_participants_dict: dict[str, Any] = {
        "age": {
            "Description": "age of the participant",
            "Units": "year"
        },
        "sex": {
            "Description": "sex of the participant as reported by the participant",
            "Levels": {
                "M": "male",
                "F": "female"
            }
        },
        "handedness": {
            "Description": "handedness of the participant as reported by the participant",
            "Levels": {
                "left": "left",
                "right": "right"
            }
        },
        "group": {
            "Description": "experimental group the participant belonged to",
            "Levels": {
                "read": "participants who read an inspirational text before the experiment",
                "write": "participants who wrote an inspirational text before the experiment"
            }
        }
    }
    if participants_dict is None:
        participants_dict = default_participants_dict
    
    for key, value in kwargs.items():
        if overwrite or key not in participants_dict:
            participants_dict[key] = value
    return participants_dict