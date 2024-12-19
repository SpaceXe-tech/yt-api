"""Global models"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from pathlib import Path
import os


class EnvVariables(BaseModel):
    visitorData: Optional[str] = Field(
        None, description="Extracted along with po token"
    )
    po_token: Optional[str] = Field(
        None,
        description="How to extract it refer to : https://github.com/yt-dlp/yt-dlp/wiki/Extractors#"
        "manually-acquiring-a-po-token-from-a-browser-for-use-when-logged-out",
    )
    filename_prefix: Optional[str] = ""
    working_directory: Optional[str] = os.getcwd()
    clear_temps: Optional[bool] = True
    search_limit: Optional[int] = 5
    # Downloader params - yt_dlp
    proxy: Optional[str] = None
    cookiefile: Optional[str] = None
    http_chunk_size: Optional[int] = 2048
    updatetime: Optional[bool] = False
    buffersize: Optional[int] = None
    ratelimit: Optional[int] = None
    throttledratelimit: Optional[int] = None
    min_filesize: Optional[int] = None
    max_filesize: Optional[int] = None
    noresizebuffer: Optional[bool] = None
    retries: Optional[int] = 2
    continuedl: Optional[bool] = False
    noprogress: Optional[bool] = True
    nopart: Optional[bool] = False
    # YoutubeDL params
    verbose: Optional[bool] = None
    quiet: Optional[bool] = None
    allow_multiple_video_streams: Optional[bool] = None
    allow_multiple_audio_streams: Optional[bool] = None
    geo_bypass: Optional[bool] = None
    geo_bypass_country: Optional[str] = None

    @property
    def ytdlp_params(self) -> dict[str, int | bool | None]:
        return dict(
            proxy=self.proxy,
            cookiefile=self.cookiefile,
            http_chunk_size=self.http_chunk_size,
            updatetime=self.updatetime,
            buffersize=self.buffersize,
            ratelimit=self.ratelimit,
            throttledratelimit=self.throttledratelimit,
            min_filesize=self.min_filesize,
            max_filesize=self.max_filesize,
            noresizebuffer=self.noresizebuffer,
            retries=self.retries,
            continuedl=self.continuedl,
            noprogress=self.noprogress,
            nopart=self.nopart,
            verbose=self.verbose,
            quiet=self.quiet,
            allow_multiple_video_streams=self.allow_multiple_video_streams,
            allow_multiple_audio_streams=self.allow_multiple_audio_streams,
            geo_bypass=self.geo_bypass,
            geo_bypass_country=self.geo_bypass_country,
        )

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
