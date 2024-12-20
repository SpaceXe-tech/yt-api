from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal
from yt_dlp_bonus.constants import mediaQualitiesType, audioBitratesType
from datetime import datetime


class SearchVideosResponse(BaseModel):

    class VideoMetadata(BaseModel):
        title: str = Field(description="Video title as in Youtube")
        url: HttpUrl = Field(description="Link to the Youtube video")

    query: str = Field(description="Search query")
    results: list[VideoMetadata]

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "hello",
                "results": [
                    {
                        "title": "Adele - Hello (Official Music Video)",
                        "url": "https://youtube.com/watch?v=YQHsXMglC9A",
                    },
                    {
                        "title": "FATIMA ALTIERI- HELLO- ( OFFICIAL MUSIC VIDEO)",
                        "url": "https://youtube.com/watch?v=X_jX3D9lCCM",
                    },
                    {
                        "title": "Hello (Folklore Riddim) | Kes | Soca 2018 (AdvoKit Productions x Julianspromo)",
                        "url": "https://youtube.com/watch?v=Nh_iSHsVsPA",
                    },
                    {
                        "title": "Aqyila - Hello (Official Audio)",
                        "url": "https://youtube.com/watch?v=k5t0RrijpHg",
                    },
                    {
                        "title": "Adele - Hello (Lyrics)",
                        "url": "https://youtube.com/watch?v=be12BC5pQLE",
                    },
                ],
            }
        }
    }


class SearchVideosResponseUrlsOnly(BaseModel):

    class VideoMetadata(BaseModel):
        url: HttpUrl = Field(description="Link to the Youtube video")

    query: str = Field(description="Search query")
    results: list[VideoMetadata]

    model_config = {
        "json_config_extras": {
            "example": {
                "query": "hello",
                "results": [
                    {"url": "https://youtube.com/watch?v=YQHsXMglC9A"},
                    {"url": "https://youtube.com/watch?v=k5t0RrijpHg"},
                    {"url": "https://youtube.com/watch?v=X_jX3D9lCCM"},
                    {"url": "https://youtube.com/watch?v=mHONNcZbwDY"},
                    {"url": "https://youtube.com/watch?v=Nh_iSHsVsPA"},
                    {"url": "https://youtube.com/watch?v=be12BC5pQLE"},
                    {"url": "https://youtube.com/watch?v=eldeaIAv_wE"},
                    {"url": "https://youtube.com/watch?v=8zDSikCh96c"},
                    {"url": "https://youtube.com/watch?v=-YV58L-jDsY"},
                    {"url": "https://youtube.com/watch?v=ZGCQ2jkq5O0"},
                ],
            }
        }
    }


class VideoDownloadPayload(BaseModel):

    url: HttpUrl = Field(description="Link to the Youtube video")
    format: Literal["mp4", "m4a"] = Field(description="Video or audio")
    quality: Literal["normal", "best"] = Field(
        "best", description="Video download quality"
    )

    model_config = {
        "json_config_extras": {
            "example": [
                {
                    "url": "https://youtu.be/S3wsCRJVUyg",
                    "format": "mp4",
                    "quality": "best",
                },
                {
                    "url": "https://youtu.be/S3wsCRJVUyg",
                    "format": "m4a",
                    "quality": "normal",
                },
            ]
        }
    }


class VideoMetadataPayload(BaseModel):
    url: HttpUrl = Field(description="Link to the Youtube video")

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

    url: HttpUrl = Field(description="Link to the Youtube video")
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
    link: Optional[HttpUrl] = Field(
        None, description="Link pointing to downloadable media file"
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
