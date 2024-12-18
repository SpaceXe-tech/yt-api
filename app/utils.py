"""Common functions and variable to the APP"""

import os
import re
import logging
from pathlib import Path
import typing as t
from app.config import loaded_config
from functools import wraps
from fastapi import HTTPException
from fastapi import status
from yt_dlp_bonus.exceptions import UserInputError

working_dir = Path(loaded_config.working_directory)

temp_dir = working_dir / "static"

download_dir = temp_dir / "media"

logger = logging.getLogger(__file__)


def create_temp_dirs() -> t.NoReturn:
    """Create temp-dir for saving files temporarily"""
    for directory in [temp_dir, download_dir]:
        os.makedirs(directory, exist_ok=True)


def sanitize_filename(filename: Path | str) -> Path:
    # Remove illegal characters
    cleaned = re.sub(r'[\\/:*?"<>|\s#]', "_", str(filename))
    # Remove leading/trailing whitespace
    return Path(cleaned.strip())


def router_exception_handler(func: t.Callable):
    """Decorator for handling api routes exceptions accordingly

    Args:
        func (t.Callable): FastAPI router.
    """

    @wraps(func)
    async def decorator(*args, **kwargs):
        try:
            resp = await func(*args, **kwargs)
            return resp
        except (AssertionError, UserInputError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "There was an issue with the server while "
                    "while trying to handle that request!",
                ),
            )

    return decorator
