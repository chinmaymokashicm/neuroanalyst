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
    
    os.environ[ENV_NEUROANALYST_HOME] = str(Path(home_dir) / "neuroanalyst")
    os.environ[ENV_NEUROANALYST_IMAGES] = str(Path(home_dir) / "neuroanalyst" / "apptainer"/ "images")
    os.environ[ENV_NEUROANALYST_DOCS] = str(Path(home_dir) / "neuroanalyst" / "apptainer"/ "docs")
    os.environ[ENV_NEUROANALYST_WORKDIR] = str(Path(home_dir) / "neuroanalyst" / "working_dirs")
    os.environ[ENV_NEUROANALYST_REPORTS] = str(Path(home_dir) / "neuroanalyst" / "reports")

def get_neuroanalyst_root_dirs(dir_type: str = "all") -> str | dict[str, str]:
    neuroanalyst_home_dir: str = os.environ.get(ENV_NEUROANALYST_HOME, None)
    if not neuroanalyst_home_dir:
        raise ValueError(f"'Variable {ENV_NEUROANALYST_HOME} is not set.'")
    
    neuroanalyst_images_dir: str = os.environ.get(ENV_NEUROANALYST_IMAGES, None)
    if not neuroanalyst_images_dir:
        raise ValueError(f"'Variable {ENV_NEUROANALYST_IMAGES} is not set.'")
    
    neuroanalyst_docs_dir: str = os.environ.get(ENV_NEUROANALYST_DOCS, None)
    if not neuroanalyst_docs_dir:
        raise ValueError(f"'Variable {ENV_NEUROANALYST_DOCS} is not set.'")
    
    neuroanalyst_working_dir: str = os.environ.get(ENV_NEUROANALYST_WORKDIR, None)
    if not neuroanalyst_working_dir:
        raise ValueError(f"'Variable {ENV_NEUROANALYST_WORKDIR} is not set.'")
    
    neuroanalyst_reports: str = os.environ.get(ENV_NEUROANALYST_REPORTS, None)
    if not neuroanalyst_reports:
        raise ValueError(f"'Variable {ENV_NEUROANALYST_REPORTS} is not set.'")
    
    if dir_type == "home":
        return neuroanalyst_home_dir
    elif dir_type == "images":
        return neuroanalyst_images_dir
    elif dir_type == "docs":
        return neuroanalyst_docs_dir
    elif dir_type == "workdir":
        return neuroanalyst_working_dir
    elif dir_type == "all":
        return {
            "root": neuroanalyst_home_dir,
            "images": neuroanalyst_images_dir,
            "docs": neuroanalyst_docs_dir,
            "workdir": neuroanalyst_working_dir
        }
    else:
        raise ValueError(f"Incorrect argument '{dir_type=}")