"""Youtube downloader app"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.events import register_events
from app.utils import temp_dir, create_temp_dirs

create_temp_dirs()

from app.v1 import v1_router

app = FastAPI(
    title="Youtube-Downloader",
    version="0.0.1",
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

app.include_router(v1_router, prefix="/v1", tags=["v1"])
app.mount("/static", StaticFiles(directory=temp_dir, check_dir=False), name="static")


@app.get("/", include_in_schema=False)
async def home():
    return RedirectResponse("/api/docs")


app = register_events(app)
