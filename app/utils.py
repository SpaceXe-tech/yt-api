"""Common functions and variable to the APP"""

import os
from pathlib import Path
from typing import NoReturn

project_dir = Path(__file__).parent.parent

temp_dir = project_dir / "static"

download_dir = temp_dir / "media"


def create_temp_dirs() -> NoReturn:
    """Create temp-dir for saving files temporarily"""
    for directory in [temp_dir, download_dir]:
        os.makedirs(directory, exist_ok=True)
