"""Common functions and variable to the APP"""

import os
import re
import logging
from pathlib import Path
import typing as t
from functools import wraps
from fastapi import HTTPException
from fastapi import status
from yt_dlp_bonus.exceptions import (
    UserInputError,
    FileSizeOutOfRange,
    UknownDownloadFailure,
)
from yt_dlp.utils import DownloadError
from datetime import datetime, timezone
from app.exceptions import InvalidVideoUrl
from app.config import download_dir, temp_dir, loaded_config
from fastapi import Request

logger = logging.getLogger(__file__)

compiled_video_id_patterns = (
    re.compile(r"^https?://youtu\.be/([\w\-_]{11}).*"),  # shareable link
    re.compile(r"^https?://www\.youtube\.com/watch\?v=([\w\-_]{11})$"),  # watch link
    re.compile(r"^https?://www\.youtube\.com/embed/([\w\-_]{11})$"),  # embedded link
    re.compile(r"^([\w\-_]{11})$"),  # video id only
    re.compile(
        r"^https?://youtube\.com/shorts/([\w\-_]{11}).*"
    ),  # Short shareable link
    re.compile(
        r"^https?://www\.youtube\.com/shorts/([\w\-_]{11})$"
    ),  # Short watch link
)

compiled_ytdlp_download_error_msg_pattern = re.compile(
    r".*\s[\w\-_]{11}:\s+(Video\s+.+)"
)


def create_temp_dirs() -> t.NoReturn:
    """Create temp-dir for saving files temporarily"""
    for directory in [download_dir, temp_dir]:
        os.makedirs(directory, exist_ok=True)


def sanitize_filename(filename: Path | str) -> str:
    # Remove illegal characters
    cleaned = re.sub(r'[\\/:*?"<>|#]', "", Path(filename).name)
    # Remove leading/trailing whitespace
    return cleaned.strip()


def router_exception_handler(func: t.Callable):
    """Decorator for handling api routes exceptions accordingly

    Args:
        func (t.Callable): FastAPI router.
    """

    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            resp = func(*args, **kwargs)
            return resp
        except HTTPException as e:
            raise e

        except (
            AssertionError,
            UserInputError,
            InvalidVideoUrl,
            FileSizeOutOfRange,
            UknownDownloadFailure,
        ) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except DownloadError as e:
            msg = re.findall(compiled_ytdlp_download_error_msg_pattern, e.msg)
            if msg:
                detail = msg[0]
                status_code = status.HTTP_403_FORBIDDEN
            else:
                detail = (
                    "Server encountered an issue while trying to handle that request!"
                )
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            raise HTTPException(status_code, detail)
        except Exception as e:
            logger.exception(e)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            detail = "Server encountered an issue while trying to handle that request!"
            raise HTTPException(status_code=status_code, detail=detail)

    return decorator


def utc_now() -> datetime:
    """current time in utc"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_video_id(url: str) -> str:
    """Extracts youtube video_id from video url

    Args:
        url (str): Youtube video url/id

    Raises:
       InvalidVideoUrl : Incase url is invalid.

    Returns:
        str: video_id
    """
    for compiled_pattern in compiled_video_id_patterns:
        match = compiled_pattern.match(url)
        if match:
            return match.group()
    raise InvalidVideoUrl(f"Invalid video url passed - {url}")


def get_absolute_link_to_static_file(filename: str, request: Request):
    """Get absolute url to a static file"""
    if loaded_config.static_server_url:
        return os.path.join(loaded_config.static_server_url.__str__(), filename)
    else:
        return os.path.join(
            f"{request.url.scheme}://{request.url.netloc}", "static", "file", filename
        )
