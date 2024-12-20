"""Youtube downloader app"""

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from app.events import register_events
from app.utils import create_temp_dirs
import time

create_temp_dirs()

from app.v1 import v1_router

app = FastAPI(
    title="Youtube-Downloader",
    version="0.0.3",
    summary="Download Youtube videos in mp4, webm and mp3 formats.",
    description="_Under development_",
    terms_of_service="",
    contact={
        "name": "Smartwa",
        "url": "https://simatwa.vercel.app",
        "email": "simatwacaleb@proton.me",
    },
    license_info={
        "name": "GPLv3",
        "url": "https://raw.githubusercontent.com/Simatwa/youtube-downloader/refs/heads/main/LICENSE",
    },
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

@app.get("/", include_in_schema=False)
async def home():
    return RedirectResponse("/api/docs")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


app = register_events(app)
