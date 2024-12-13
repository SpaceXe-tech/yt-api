from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal


class SearchVideosResponse(BaseModel):

    class VideoMetadata(BaseModel):
        title: str = Field(description="Video title as in Youtube")
        url: HttpUrl = Field(description="Link to the Youtube video")

    query: str = Field(description="Search query")
    results: list[VideoMetadata]


class SearchVideosResponseUrlsOnly(BaseModel):

    class VideoMetadata(BaseModel):
        url: HttpUrl = Field(description="Link to the Youtube video")

    query: str = Field(description="Search query")
    results: list[VideoMetadata]


class VideoDownloadPayload(BaseModel):

    url: HttpUrl = Field(description="Link to the Youtube video")
    format: Literal["mp4", "m4a"] = Field(description="Video or audio")
    quality: Literal["normal", "best"] = Field(
        "best", description="Video download quality"
    )


class MediaDownloadResponse(BaseModel):

    is_success: bool = Field(description="Download successful status")
    filename: Optional[str] = None
    link: Optional[HttpUrl] = Field(
        None, description="Link pointing to downloadable media file"
    )
