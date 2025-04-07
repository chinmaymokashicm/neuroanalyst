from ..utils.constants import *

from pathlib import Path, PosixPath
import os

def set_neuroanalyst_root_dirs() -> None:
    try:
        get_neuroanalyst_root_dirs("all")
    except Exception as e:
        print(f"Error setting environment values: {e}")
    
    home_dir: str = os.environ.get("HOME", None)
    if not home_dir:
        raise ValueError("'$HOME' environment variable is not set.")
    
    root_dirs = {
        ENV_NEUROANALYST_HOME: str(Path(home_dir) / "neuroanalyst"),
        ENV_NEUROANALYST_IMAGES: str(Path(home_dir) / "neuroanalyst" / "apptainer"/ "images"),
        ENV_NEUROANALYST_DOCS: str(Path(home_dir) / "neuroanalyst" / "apptainer"/ "docs"),
        ENV_NEUROANALYST_WORKDIR: str(Path(home_dir) / "neuroanalyst" / "working_dirs"),
        ENV_NEUROANALYST_REPORTS: str(Path(home_dir) / "neuroanalyst" / "reports"),
        ENV_NEUROANALYST_LOGS: str(Path(home_dir) / "neuroanalyst" / "logs"),
        ENV_NEUROANALYST_DATASETS: str(Path(home_dir) / "neuroanalyst" / "datasets")
    }
    
    for env_var, dir_path in root_dirs.items():
        os.environ[env_var] = dir_path
        os.makedirs(dir_path, exist_ok=True)
        print(f"{env_var}: {dir_path}")

def get_neuroanalyst_root_dirs(dir_type: str = "all") -> str | dict[str, str]:
    root_dirs = {
        "home": ENV_NEUROANALYST_HOME,
        "images": ENV_NEUROANALYST_IMAGES,
        "docs": ENV_NEUROANALYST_DOCS,
        "workdir": ENV_NEUROANALYST_WORKDIR,
        "reports": ENV_NEUROANALYST_REPORTS,
        "logs": ENV_NEUROANALYST_LOGS,
        "datasets": ENV_NEUROANALYST_DATASETS
    }
    
    if dir_type == "all":
        return {dir_type: os.environ.get(env_var, None) for dir_type, env_var in root_dirs.items()}
    elif dir_type in root_dirs:
        return os.environ.get(root_dirs[dir_type], None)
    else:
        raise ValueError(f"Incorrect argument '{dir_type=}")