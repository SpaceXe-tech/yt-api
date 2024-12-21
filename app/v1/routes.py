from fastapi import APIRouter, Query, Request
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
from yt_dlp_bonus import YoutubeDLBonus, Download
from yt_dlp_bonus.constants import audioQualities
from yt_dlp_bonus.utils import get_size_in_mb_from_bytes

router = APIRouter()

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


@router.get("/search", name="Search videos")
@router_exception_handler
def search_videos(
    q: str = Query(description="Video title"),
    # limit: int = Query(10, gt=0, le=loaded_config.search_limit, description="Search results limit"),
) -> models.SearchVideosResponse:
    """Search videos"""
    videos_found_container = []
    video_count = 0
    for video in Search(q, **po_kwargs).videos:
        videos_found_container.append(
            dict(title=video.title, url=video.watch_url, duration=video.length)
        )
        video_count += 1
        if video_count == loaded_config.search_limit:
            break
    return models.SearchVideosResponse(query=q, results=videos_found_container)


@router.get("/search/url", name="Search videos (url)")
@router_exception_handler
def search_videos(
    q: str = Query(description="Video title"),
) -> models.SearchVideosResponseUrlsOnly:
    """Search videos and return video urls only"""
    videos_found_container = []
    for video in Search(q, **po_kwargs).videos:
        videos_found_container.append(dict(url=video.watch_url))
    return models.SearchVideosResponseUrlsOnly(query=q, results=videos_found_container)


@router.post("/metadata", name="Video metadata")
@router_exception_handler
def get_video_metadata(
    payload: models.VideoMetadataPayload,
) -> models.VideoMetadataResponse:
    extracted_info = get_extracted_info(yt=yt, url=str(payload.url))
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
    extracted_info = get_extracted_info(yt=yt, url=str(payload.url))
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
