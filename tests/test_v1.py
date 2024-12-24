import pytest
from tests import client
import app.v1.models as models
from app.events import event_startup_create_tempdirs, event_startup_create_tables

video_link = "https://youtu.be/S3wsCRJVUyg?si=svRtQPHef9TSMABt"


def run_startup_events():
    for event in [event_startup_create_tempdirs, event_startup_create_tables]:
        event()


run_startup_events()


@pytest.mark.parametrize(["query", "limit"], [("hello", 2), ("hey", 1)])
def test_video_search(query, limit):
    resp = client.get("/api/v1/search", params=dict(q=query, limit=limit))
    assert resp.is_success
    videos = models.SearchVideosResponse(**resp.json())
    assert len(videos.results) <= limit


@pytest.mark.parametrize(["query", "limit"], [("hello", 2), ("hey", 1)])
def test_stream_video_search(query, limit):
    resp = client.get("/api/v1/search/stream", params=dict(q=query, limit=limit))
    assert resp.is_success
    assert len(resp.text.split("\n")) <= limit + 1


@pytest.mark.parametrize(["query", "limit"], [("hello", 3), ("hey", 4)])
def test_video_search_urls_only(query, limit):
    resp = client.get("/api/v1/search/url", params=dict(q=query, limit=limit))
    assert resp.is_success
    videos = models.SearchVideosUrlResponse(**resp.json())
    assert len(videos.shorts) <= limit


@pytest.mark.parametrize(
    ["url"],
    [
        ("https://youtu.be/HUGcwe93F9E?si=Ajunj8GlRs-DzKnQ",),
        ("HUGcwe93F9E",),
        ("https://www.youtube.com/watch?v=HUGcwe93F9E",),
    ],
)
def test_video_metadata(url):
    resp = client.post("/api/v1/metadata", json=dict(url=url))
    assert resp.is_success
    models.VideoMetadataResponse(**resp.json())


@pytest.mark.parametrize(
    ["url", "quality", "bitrate"],
    [
        ("https://youtu.be/S3wsCRJVUyg", "1080p", None),
        ("https://youtu.be/S3wsCRJVUyg", "720p", "128k"),
        ("https://youtu.be/S3wsCRJVUyg", "medium", "192k"),
        ("https://youtu.be/S3wsCRJVUyg", "low", None),
    ],
)
def test_download_processing(url, quality, bitrate):
    resp = client.post(
        "/api/v1/download",
        json=dict(
            url=url,
            quality=quality,
            bitrate=bitrate,
        ),
    )
    assert resp.is_success
    models.MediaDownloadResponse(**resp.json())


@pytest.mark.parametrize(
    ["url", "quality", "audio_bitrate", "audio_only"],
    [
        ("https://youtu.be/S3wsCRJVUyg", "1080p", "128k", False),
        ("S3wsCRJVUyg", "medium", "192k", True),
    ],
)
def test_download_media(url, quality, audio_bitrate, audio_only):
    resp = client.post(
        "/api/v1/download",
        json=dict(
            url=url,
            quality=quality,
            audio_bitrate=audio_bitrate,
            audio_only=audio_only,
        ),
    )
    assert resp.is_success
    media = models.MediaDownloadResponse(**resp.json())
    # This will raise 404 since the static contents are served by flask (wsgi).
    # static_resp = client.get(str(media.link))
    # assert static_resp.is_success
