from fastapi import APIRouter, Query, Request
from fastapi import status, HTTPException
import app.v1.models as models
from app.v1.utils import get_extracted_info
from app.utils import (
    router_exception_handler,
    get_absolute_link_to_static_file,
)
from app.config import loaded_config, download_dir
from pathlib import Path
from os import path
from yt_dlp_bonus import YoutubeDLBonus, Download
from yt_dlp_bonus.constants import audioQualities
from yt_dlp_bonus.utils import get_size_string
from functools import lru_cache

router = APIRouter(prefix="/v1")

yt = YoutubeDLBonus(params=loaded_config.ytdlp_params)

download = Download(
    yt=yt,
    working_directory=download_dir,
    clear_temps=loaded_config.clear_temps,
    filename_prefix=loaded_config.filename_prefix,
)

from innertube import InnerTube
from httpx import Proxy

PARAMS_TYPE_VIDEO = "EgIQAQ%3D%3D"

innertube_client = InnerTube(
    "WEB",
    "2.20230920.00.00",
    # proxies=None if not loaded_config.proxy else Proxy(loaded_config.proxy),
)


@lru_cache(maxsize=100)
def search_videos_by_key(query: str, limit: int = -1) -> list[dict[str, str]]:
    """Perform a video search.

    Args:
        query (str): Search keyword
        limit (int): Total results not to exceed. Defaults to -1 (No limit).

    Returns:
        list[dict[str, str]]: Sorted shallow results.
    """
    video_search_results = innertube_client.search(query, params=PARAMS_TYPE_VIDEO)
    video_metadata_container: list[dict] = []
    contents = video_search_results["contents"]["twoColumnSearchResultsRenderer"][
        "primaryContents"
    ]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
    count = 0
    for content in contents:
        try:
            video = content["videoRenderer"]
            video_id = video["videoId"]
            video_title = video["title"]["runs"][0]["text"]
            video_duration = video["lengthText"]["simpleText"]
            video_metadata_container.append(
                dict(id=video_id, title=video_title, duration=video_duration)
            )
            count += 1
            if count == limit:
                break
        except:  # KeyError etc
            pass
    return video_metadata_container


@router.get("/search", name="Search videos")
@router_exception_handler
def search_videos(
    q: str = Query(description="Video title or keyword"),
    limit: int = Query(
        10,
        gt=0,
        le=loaded_config.search_limit,
        description="Videos amount not to exceed.",
    ),
) -> models.SearchVideosResponse:
    """Search videos
    - Search videos matching the query and return whole results at once.
    - Serves from cache similar `99` subsequent queries.
    """
    videos_found = search_videos_by_key(query=q, limit=limit)
    if not videos_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No video matched that query - {q}!",
        )
    return models.SearchVideosResponse(query=q, results=videos_found)


@router.post("/metadata", name="Video metadata")
@router_exception_handler
def get_video_metadata(
    payload: models.VideoMetadataPayload,
) -> models.VideoMetadataResponse:
    """Get metadata of a specific video
    - Similar subsequent requests will be faster as they will be served
    from cache for a few hours.
    """
    extracted_info = get_extracted_info(yt=yt, url=payload.url)
    video_formats = yt.get_video_qualities_with_extension(
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
                    size=get_size_string(format.audio_video_size),
                )
            )
        else:
            video_formats.append(
                dict(
                    quality=quality,
                    size=get_size_string(format.audio_video_size),
                )
            )
    return models.VideoMetadataResponse(
        id=extracted_info.id,
        title=extracted_info.title,
        channel=extracted_info.channel,
        uploader_url=extracted_info.uploader_url,
        duration_string=extracted_info.duration_string,
        thumbnail=extracted_info.thumbnail,
        audio=audio_formats,
        video=video_formats,
        default_audio_format=loaded_config.default_audio_format,
    )


@router.post("/download", name="Process download")
@router_exception_handler
def process_video_for_download(
    request: Request, payload: models.MediaDownloadProcessPayload
) -> models.MediaDownloadResponse:
    """Initiate download processing
    - To download the media file: Add parameter `download` with value
    `true` to the returned link i.e `?download=true`.
    """
    extracted_info = get_extracted_info(yt=yt, url=payload.url)
    video_formats = yt.get_video_qualities_with_extension(
        extracted_info,
        ext=loaded_config.default_extension,
        audio_ext=(
            loaded_config.default_audio_format
            if payload.quality in audioQualities
            else "webm"
        ),
    )
    updated_video_formats = yt.update_audio_video_size(
        video_formats,
        payload.quality if payload.quality in audioQualities else "medium",
    )
    saved_to: Path = download.run(
        title=extracted_info.title,
        qualities_format=updated_video_formats,
        quality=payload.quality,
        bitrate=payload.bitrate,
    )
    filename = saved_to.name

    return models.MediaDownloadResponse(
        is_success=True,
        filename=saved_to.name,
        filesize=get_size_string(path.getsize(saved_to)),
        link=get_absolute_link_to_static_file(filename, request),
    )
