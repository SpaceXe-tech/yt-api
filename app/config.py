from app.models import EnvVariables
from dotenv import dotenv_values
from pathlib import Path

loaded_config = EnvVariables(**dotenv_values())
"""Loaded from .env file"""

working_dir = Path(loaded_config.working_directory)

download_dir = working_dir / "downloads"