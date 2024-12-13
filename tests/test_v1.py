import pytest
from tests import client
import app.v1.models as models
from app.events import (
    event_startup_create_tempdirs,
)

video_link = "https://youtu.be/S3wsCRJVUyg?si=svRtQPHef9TSMABt"


def run_startup_events():
    for event in [event_startup_create_tempdirs]:
        event()


run_startup_events()


def test_video_search():
    resp = client.get("/v1/search", params=dict(q="Hello"))
    assert resp.is_success
    models.SearchVideosResponse(**resp.json())


@pytest.mark.parametrize(
    ["link", "format", "quality"],
    [
        (video_link, "mp4", "best"),
        (video_link, "m4a", "normal"),
    ],
)
def test_download_processing(link, format, quality):
    resp = client.post(
        "/v1/download",
        json=dict(url=link, format=format, quality=quality),
    )
    assert resp.is_success
    models.MediaDownloadResponse(**resp.json())


@pytest.mark.parametrize(
    ["link", "format", "quality"],
    [
        (video_link, "mp4", "best"),
        (video_link, "m4a", "normal"),
    ],
)
def test_download_media(link, format, quality):
    resp = client.post(
        "/v1/download",
        json=dict(url=link, format=format, quality=quality),
    )
    assert resp.is_success
    media = models.MediaDownloadResponse(**resp.json())
    static_resp = client.get(media.link)
    assert static_resp.is_success
