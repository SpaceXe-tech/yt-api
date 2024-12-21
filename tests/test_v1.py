import pytest
from tests import client
import app.v1.models as models
from app.events import event_startup_create_tempdirs, event_startup_create_tables

video_link = "https://youtu.be/S3wsCRJVUyg?si=svRtQPHef9TSMABt"


def run_startup_events():
    for event in [event_startup_create_tempdirs, event_startup_create_tables]:
        event()


run_startup_events()


def test_video_search():
    resp = client.get("/v1/search", params=dict(q="Hello"))
    assert resp.is_success
    models.SearchVideosResponse(**resp.json())


def test_video_search_urls_only():
    resp = client.get("/v1/search/url", params=dict(q="Hello"))
    assert resp.is_success
    models.SearchVideosResponseUrlsOnly(**resp.json())


@pytest.mark.parametrize(
    ["url"],
    [
        ("https://youtu.be/lw5tB9LQQVM"),
        ("https://youtu.be/lw5tB9LQQVM"),
    ],
)
def test_video_metadata(url, extension):
    resp = client.post("/v1/metadata", json=dict(url=url))
    assert resp.is_success
    models.VideoMetadataResponse(**resp.json())


@pytest.mark.parametrize(
    ["url", "quality", "audio_bitrates", "audio_only"],
    [
        ("https://youtu.be/S3wsCRJVUyg", "1080p", "128k", False),
        ("https://youtu.be/S3wsCRJVUyg", "720p", "128k", False),
        ("https://youtu.be/S3wsCRJVUyg", "medium", "192k", True),
        ("https://youtu.be/S3wsCRJVUyg", "low", "320k", True),
    ],
)
def test_download_processing(url, quality, audio_bitrates, audio_only):
    resp = client.post(
        "/v1/download",
        json=dict(
            url=url,
            quality=quality,
            audio_bitrates=audio_bitrates,
            audio_only=audio_only,
        ),
    )
    assert resp.is_success
    models.MediaDownloadResponse(**resp.json())


@pytest.mark.parametrize(
    ["url", "quality", "extension", "audio_bitrates", "audio_only"],
    [
        ("https://youtu.be/S3wsCRJVUyg", "1080p", "128k", False),
        ("https://youtu.be/S3wsCRJVUyg", "medium", "192k", True),
    ],
)
def test_download_media(url, quality, audio_bitrates, audio_only):
    resp = client.post(
        "/v1/download",
        json=dict(
            url=url,
            quality=quality,
            audio_bitrates=audio_bitrates,
            audio_only=audio_only,
        ),
    )
    assert resp.is_success
    media = models.MediaDownloadResponse(**resp.json())
    # These will raise 404 since the static contents are served by flask (wsgi).
    # static_resp = client.get(str(media.link))
    # assert static_resp.is_success
