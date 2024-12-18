from fastapi import APIRouter, Query, Request
import app.v1.models as models
from app.utils import download_dir, sanitize_filename, router_exception_handler
from app.config import loaded_config
from pathlib import Path
from pytubefix import Search, YouTube
from os import rename, path
from yt_dlp_bonus import YoutubeDLBonus, Download
from yt_dlp_bonus.constants import audioQualities
from yt_dlp_bonus.utils import get_size_in_mb_from_bytes

router = APIRouter()

yt = YoutubeDLBonus()

download = Download(
    working_directory=download_dir,
    clear_temps=loaded_config.clear_temps,
    file_prefix=loaded_config.filename_prefix,
)

po_kwargs = dict(
    use_po_token=True,
    po_token_verifier=loaded_config.po_token_verifier,
    proxies={"https": loaded_config.proxy} if loaded_config.proxy else None,
)


@router.get("/search", name="Search videos")
@router_exception_handler
async def search_videos(
    q: str = Query(description="Video title"),
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
async def search_videos(
    q: str = Query(description="Video title"),
) -> models.SearchVideosResponseUrlsOnly:
    """Search videos and return video urls only"""
    videos_found_container = []
    for video in Search(q, **po_kwargs).videos:
        videos_found_container.append(dict(url=video.watch_url))
    return models.SearchVideosResponseUrlsOnly(query=q, results=videos_found_container)


@router.post("/metadata", name="Video metadata")
@router_exception_handler
async def get_video_metadata(
    payload: models.VideoMetadataPayload,
) -> models.VideoMetadataResponse:
    extracted_info = yt.extract_info_and_form_model(payload.url.__str__())
    video_formats = yt.get_videos_quality_by_extension(
        extracted_info, ext=payload.extension
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
        ext=payload.extension,
        thumbnail=f"https://i.ytimg.com/vi/{extracted_info.id}/maxresdefault.jpg",
        audio=audio_formats,
        video=video_formats,
    )


@router.post("/download", name="Process download")
@router_exception_handler
async def process_video_for_download(
    request: Request, payload: models.MediaDownloadProcessPayload
) -> models.MediaDownloadResponse:
    host = f"{request.url.scheme}://{request.url.netloc}"
    extracted_info = yt.extract_info_and_form_model(payload.url.__str__())
    video_formats = yt.get_videos_quality_by_extension(
        extracted_info, ext=payload.extension
    )
    saved_to: Path = download.run(
        title=extracted_info.title,
        quality=payload.quality,
        quality_infoFormat=video_formats,
        audio_bitrates=payload.audio_bitrates,
        audio_only=payload.audio_only,
    )
    filename = sanitize_filename(saved_to.name)
    new_saved_to = Path(download_dir) / filename
    rename(saved_to, new_saved_to)

    return models.MediaDownloadResponse(
        is_success=True,
        filename=saved_to.name,
        filesize=get_size_in_mb_from_bytes(path.getsize(new_saved_to)),
        link=f"{host}/static/{download_dir.name}/{filename}",
    )
