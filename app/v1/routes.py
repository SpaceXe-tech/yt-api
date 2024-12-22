from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
import app.v1.models as models
from app.v1.utils import get_extracted_info
from app.utils import (
    router_exception_handler,
    get_absolute_link_to_static_file,
)
from app.config import loaded_config, download_dir
from pathlib import Path
from pytubefix import Search
from os import path
from json import dumps
from yt_dlp_bonus import YoutubeDLBonus, Download
from yt_dlp_bonus.constants import audioQualities
from yt_dlp_bonus.utils import get_size_in_mb_from_bytes
import typing as t

router = APIRouter(prefix="/v1")

yt = YoutubeDLBonus(params=loaded_config.ytdlp_params)

download = Download(
    yt=yt,
    working_directory=download_dir,
    clear_temps=loaded_config.clear_temps,
    filename_prefix=loaded_config.filename_prefix,
)

po_kwargs = dict(
    use_po_token=type(loaded_config.po_token) is not None,
    po_token_verifier=loaded_config.po_token_verifier,
    proxies={"https": loaded_config.proxy} if loaded_config.proxy else None,
)


def search_videos_and_yield_results(
    query: str, limit: int
) -> t.Generator[dict, None, None]:
    """Search youtube video and yield results

    Args:
        query (str): Search paramter.
        limit (int): Results amount not to exceed.

    Yields:
        Iterator[t.Generator[dict, None, None]]: title, id & length.
    """
    for count, video in enumerate(Search(query, **po_kwargs).videos, start=1):
        yield dict(title=video.title, id=video.video_id, duration=video.length)
        if count >= limit:
            break


def generate_streaming_search_results(
    query: str, limit: int
) -> t.Generator[str, None, None]:
    """Performs a search, encode and yield results

    Args:
        query (str): Search parameter.
        limit (int): Results amount not to exceed.

    Yields:
        Iterator[t.Generator, None, None]: Video info (one video).
    """
    for video in search_videos_and_yield_results(query, limit):
        complete_vido_info = dict(query=query, results=[video])
        yield dumps(complete_vido_info) + "\n"


@router.get("/search", name="Search videos")
@router_exception_handler
def search_videos(
    q: str = Query(description="Video title"),
    limit: int = Query(
        10,
        gt=0,
        le=loaded_config.search_limit,
        description="Videos amount not to exceed.",
    ),
) -> models.SearchVideosResponse:
    """Search videos"""
    videos_found_container = []
    for video in search_videos_and_yield_results(query=q, limit=limit):
        videos_found_container.append(video)
    return models.SearchVideosResponse(query=q, results=videos_found_container)


@router.get("/search/stream", name="Search videos")
@router_exception_handler
def search_videos(
    q: str = Query(description="Video title"),
    limit: int = Query(
        10,
        gt=0,
        le=loaded_config.search_limit,
        description="Videos amount not to exceed.",
    ),
) -> t.Annotated[StreamingResponse, models.SearchVideosResponse]:
    """Search videos and yield results"""

    return StreamingResponse(
        content=generate_streaming_search_results(query=q, limit=limit),
        media_type="text/event-stream",
    )


@router.get("/search/url", name="Search videos (url)")
@router_exception_handler
def search_videos(
    q: str = Query(description="Video title"),
    limit: int = Query(
        50, description="Results amount not to exceed per category", gt=0
    ),
) -> models.SearchVideosUrlResponse:
    """Search videos and return video urls only"""
    search = Search(q, **po_kwargs)
    videos_found = [video.video_id for video in search.videos]
    shorts_found = [short.video_id for short in search.shorts]
    return models.SearchVideosUrlResponse(
        query=q,
        videos=videos_found[:limit] if len(videos_found) > limit else videos_found,
        shorts=shorts_found[:limit] if len(shorts_found) > limit else shorts_found,
    )


@router.post("/metadata", name="Video metadata")
@router_exception_handler
def get_video_metadata(
    payload: models.VideoMetadataPayload,
) -> models.VideoMetadataResponse:
    extracted_info = get_extracted_info(yt=yt, url=payload.url)
    video_formats = yt.get_videos_quality_by_extension(
        extracted_info, ext=loaded_config.default_extension
    )
    updated_video_formats = yt.update_audio_video_size(video_formats)
    audio_formats = []
    video_formats = []
    for quality, format in updated_video_formats.items():
        if quality in audioQualities:
            audio_formats.append(
                dict(
                    quality=quality,
                    size=get_size_in_mb_from_bytes(format.audio_video_size),
                )
            )
        else:
            video_formats.append(
                dict(
                    quality=quality,
                    size=get_size_in_mb_from_bytes(format.audio_video_size),
                )
            )
    return models.VideoMetadataResponse(
        id=extracted_info.id,
        title=extracted_info.title,
        channel=extracted_info.channel,
        upload_date=extracted_info.upload_date,
        uploader_url=extracted_info.uploader_url,
        duration_string=extracted_info.duration_string,
        thumbnail=f"https://i.ytimg.com/vi/{extracted_info.id}/maxresdefault.jpg",
        audio=audio_formats,
        video=video_formats,
    )


@router.post("/download", name="Process download")
@router_exception_handler
def process_video_for_download(
    request: Request, payload: models.MediaDownloadProcessPayload
) -> models.MediaDownloadResponse:
    extracted_info = get_extracted_info(yt=yt, url=payload.url)
    video_formats = yt.get_videos_quality_by_extension(
        extracted_info, ext=loaded_config.default_extension
    )
    saved_to: Path = download.run(
        title=extracted_info.title,
        quality=payload.quality,
        quality_infoFormat=video_formats,
        audio_bitrates=payload.audio_bitrates,
        audio_only=payload.audio_only,
    )
    filename = saved_to.name

    return models.MediaDownloadResponse(
        is_success=True,
        filename=saved_to.name,
        filesize=get_size_in_mb_from_bytes(path.getsize(saved_to)),
        link=get_absolute_link_to_static_file(filename, request),
    )
