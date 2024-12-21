from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal
from yt_dlp_bonus.constants import mediaQualitiesType, audioBitratesType
from datetime import datetime


class SearchVideosResponse(BaseModel):

    class VideoMetadata(BaseModel):
        title: str = Field(description="Video title as in Youtube")
        id: str = Field(description="Video id")
        duration: int = Field(description="Video's running time in seconds.")

    query: str = Field(description="Search query")
    results: list[VideoMetadata]

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "hello",
                "results": [
                    {
                        "title": "Adele - Hello (Official Music Video)",
                        "id": "YQHsXMglC9A",
                        "duration": 367,
                    },
                    {
                        "title": "Adele - Hello (Lyrics)",
                        "id": "be12BC5pQLE",
                        "duration": 296,
                    },
                    {
                        "title": "Lionel Richie - Hello (Official Music Video)",
                        "id": "mHONNcZbwDY",
                        "duration": 326,
                    },
                    {
                        "title": "Hello! | Kids Greeting Song and Feelings Song | Super Simple Songs",
                        "id": "tVlcKp3bWH8",
                        "duration": 78,
                    },
                    {
                        "title": "Hello Song for Kids | Greeting Song for Kids | The Singing Walrus",
                        "id": "gghDRJVxFxU",
                        "duration": 131,
                    },
                ],
            }
        }
    }


class SearchVideosUrlResponse(BaseModel):

    query: str = Field(description="Search query")
    videos: list[str] = Field(description="Youtube videos id")
    shorts: list[str] = Field(description="Short videos id")

    model_config = {
        "json_config_extra": {
            "example": {
                "query": "Alan Walker songs",
                "videos": [
                    "Wr1KbcjIW8Q",
                    "1-xGerv5FOk",
                    "ejbVsbrKd9U",
                    "60ItHLz5WEA",
                    "isVzVPpx3zc",
                    "gYrjTLVfJyM",
                    "kyLuzKbgXAs",
                    "M-P4QBt-FWw",
                ],
                "shorts": [
                    "uebrUqs6K50",
                    "t9qrSfSxP00",
                    "W9eSwb8zB7I",
                    "EjTswBdO7LA",
                    "AW5S4xSJBh0",
                    "14nKFaaogMU",
                    "nz3gXdAEG7k",
                    "uWI3yy9Qf54",
                ],
            }
        }
    }


class VideoMetadataPayload(BaseModel):
    url: str = Field(description="Link to the Youtube video or video id")

    model_config = {
        "json_schema_extra": {"example": {"url": "https://youtu.be/lw5tB9LQQVM"}}
    }


class VideoMetadataResponse(BaseModel):
    class MediaMetadata(BaseModel):
        quality: str  # mediaQualitiesType
        size: str

    id: str
    title: str
    channel: str
    upload_date: datetime
    uploader_url: str
    duration_string: str
    thumbnail: HttpUrl
    audio: list[MediaMetadata]
    video: list[MediaMetadata]

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "lw5tB9LQQVM",
                "title": "Marioo feat Fathermoh, Sean Mmg, Ssaru & Motif - Statue (Official Music Video)",
                "channel": "MariooOfficial",
                "upload_date": "1970-08-23T06:28:47Z",
                "uploader_url": "https://www.youtube.com/@MariooOfficialMusic",
                "duration_string": "2:34",
                "thumbnail": "https://i.ytimg.com/vi/lw5tB9LQQVM/maxresdefault.jpg",
                "audio": [
                    {"quality": "ultralow", "size": "0.68 MB"},
                    {"quality": "low", "size": "1.32 MB"},
                    {"quality": "medium", "size": "2.6 MB"},
                ],
                "video": [
                    {"quality": "144p", "size": "4.14 MB"},
                    {"quality": "240p", "size": "5.99 MB"},
                    {"quality": "360p", "size": "10.43 MB"},
                    {"quality": "480p", "size": "14.88 MB"},
                    {"quality": "720p", "size": "31.64 MB"},
                    {"quality": "1080p", "size": "52.14 MB"},
                    {"quality": "1440p", "size": "171.99 MB"},
                    {"quality": "2160p", "size": "342.56 MB"},
                ],
            }
        }
    }


class MediaDownloadProcessPayload(BaseModel):

    url: str = Field(description="Link to the Youtube video or video id")
    quality: mediaQualitiesType
    audio_bitrates: audioBitratesType | None = None
    audio_only: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://youtu.be/1-xGerv5FOk?si=Vv_FeKPF_6eDp5di",
                "quality": "480p",
                "audio_bitrates": "128k",
                "audio_only": False,
            }
        }
    }


class MediaDownloadResponse(BaseModel):

    is_success: bool = Field(description="Download successful status")
    filename: Optional[str] = None
    filesize: str
    link: Optional[str] = Field(
        description="Link pointing to downloadable media file or video id"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_success": True,
                "filename": "Alan Walker - Alone 1080p.mp4",
                "filesize": "35.37 MB",
                "link": "http://localhost:8000/static/file/Alan%20Walker%20-%20Alone%201080p.mp4",
            }
        }
    }
