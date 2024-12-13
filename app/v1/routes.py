from fastapi import APIRouter, Query, Request
import app.v1.models as models
from app.utils import download_dir
from app.config import loaded_config
from pathlib import Path

from pytubefix import Search, YouTube

router = APIRouter()

po_kwargs = dict(
    use_po_token=True,
    po_token_verifier=loaded_config.po_token_verifier,
    proxies={"https": loaded_config.proxy} if loaded_config.proxy else None,
)

search_limit = 5


@router.get("/search", name="Search videos")
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
        if video_count >= search_limit:
            break
    return models.SearchVideosResponse(query=q, results=videos_found_container)


@router.get("/search/url", name="Search videos (url)")
async def search_videos(
    q: str = Query(description="Video title"),
) -> models.SearchVideosResponseUrlsOnly:
    """Search videos and return video urls only"""
    videos_found_container = []
    for video in Search(q, **po_kwargs).videos:
        videos_found_container.append(dict(url=video.watch_url))
    return models.SearchVideosResponseUrlsOnly(query=q, results=videos_found_container)


@router.post("/download", name="Process download")
async def process_video_for_download(
    request: Request,
    download_payload: models.VideoDownloadPayload,
) -> models.MediaDownloadResponse:
    """Download video in mp4 or m4a formats"""
    # Quality check implementation needed
    yt = YouTube(download_payload.url.__str__(), **po_kwargs)
    host = f"{request.url.scheme}://{request.url.netloc}"
    if download_payload.format == "m4a":
        ys = yt.streams.get_audio_only()

    else:
        ys = yt.streams.get_highest_resolution()

    saved_to = ys.download(
        output_path=download_dir, skip_existing=True, filename_prefix="DEMO_"
    )
    filename = Path(saved_to).name
    return models.MediaDownloadResponse(
        is_success=True,
        filename=filename,
        link=f"{host}/static/{download_dir.name}/{filename}",
    )
