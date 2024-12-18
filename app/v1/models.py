from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal
from yt_dlp_bonus.constants import mediaQualitiesType, audioBitratesType


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
    extension: Literal["mp4", "webm"] = "mp4"

    model_config = {
        "json_schema_extra": {
            "example": {"url": "https://youtu.be/lw5tB9LQQVM", "extension": "mp4"}
        }
    }


class VideoMetadataResponse(BaseModel):
    class MediaMetadata(BaseModel):
        quality: str  # mediaQualitiesType
        size: int

    title: str
    id: str
    thumbnail: HttpUrl
    ext: Literal["webm", "mp4"]
    audio: list[MediaMetadata]
    video: list[MediaMetadata]

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Marioo feat Fathermoh, Sean Mmg, Ssaru & Motif - Statue (Official Music Video)",
                "id": "lw5tB9LQQVM",
                "thumbnail": "https://i.ytimg.com/vi/lw5tB9LQQVM/maxresdefault.jpg",
                "ext": "mp4",
                "audio": [
                    {"quality": "ultralow", "size": 682923},
                    {"quality": "low", "size": 1318452},
                    {"quality": "medium", "size": 2599235},
                ],
                "video": [
                    {"quality": "144p", "size": 4234331},
                    {"quality": "240p", "size": 6359946},
                    {"quality": "360p", "size": 9910457},
                    {"quality": "480p", "size": 15383561},
                    {"quality": "720p", "size": 25566169},
                    {"quality": "1080p", "size": 53647456},
                    {"quality": "1440p", "size": 135255080},
                    {"quality": "2160p", "size": 263936850},
                ],
            }
        }
    }


class MediaDownloadProcessPayload(BaseModel):

    url: HttpUrl = Field(description="Link to the Youtube video")
    quality: mediaQualitiesType
    extension: Literal["mp4", "webm"] = "mp4"
    audio_bitrates: audioBitratesType = "128k"
    audio_only: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://youtu.be/S3wsCRJVUyg",
                "quality": "720p",
                "extension": "mp4",
                "audio_bitrates": "192k",
                "audio_only": False,
            }
        }
    }


class MediaDownloadResponse(BaseModel):

    is_success: bool = Field(description="Download successful status")
    filename: Optional[str] = None
    link: Optional[HttpUrl] = Field(
        None, description="Link pointing to downloadable media file"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_success": True,
                "filename": "DEMO_A Few Moments Later | SpongeBob Time Card #8.mp4",
                "link": "http://localhost:8000/static/media/DEMO_A_Few_Moments_Later___SpongeBob_Time_Card__8.mp4",
            }
        }
    }
