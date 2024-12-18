"""Global models"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from pathlib import Path
import os


class EnvVariables(BaseModel):
    visitorData: str = Field(description="Extracted along with po token")
    po_token: str = Field(
        "How to extract it refer to : https://github.com/yt-dlp/yt-dlp/wiki/Extractors#"
        "manually-acquiring-a-po-token-from-a-browser-for-use-when-logged-out"
    )
    proxy: Optional[str] = None
    cookiefile: Optional[str] = None
    filename_prefix: Optional[str] = ""
    working_directory: Optional[str] = os.getcwd()
    clear_temps: Optional[bool] = True
    search_limit: Optional[int] = 5
    chunk_size: Optional[int] = 4096

    @field_validator("working_directory")
    def validate_working_directory(value):
        working_dir = Path(value)
        if not working_dir.exists() or not working_dir.is_dir():
            raise TypeError(f"Invalid working_directory passed - {value}")
        return value

    @field_validator("cookiefile")
    def validate_cookiefile(value):
        if not value:
            return
        cookiefile = Path(value)
        if not cookiefile.exists() or not cookiefile.is_file():
            raise TypeError(f"Invalid cookiefile passed - {value}")
        return value

    def po_token_verifier(self) -> tuple[str, str]:
        return self.visitorData, self.po_token
