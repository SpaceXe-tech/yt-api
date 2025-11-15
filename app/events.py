"""Startup and shutdown events"""

from app.utils import create_temp_dirs, download_dir, utc_now, logger
from fastapi import FastAPI
from shutil import rmtree
from app.db import create_tables, VideoInfo, engine
from sqlmodel import Session, delete
from app.config import loaded_config
from datetime import timedelta


def event_startup_create_tempdirs():
    create_temp_dirs()


def event_startup_create_tables():
    create_tables()


def event_all_delete_expired_extracted_info():
    time_offset = utc_now() - timedelta(
        hours=loaded_config.video_info_cache_period_in_hrs
    )
    delete_query = delete(VideoInfo).where(VideoInfo.updated_on < time_offset)
    with Session(bind=engine) as session:
        logger.info(f"Deleting expired extracted-infos [< {time_offset}]")
        session.exec(delete_query)
        session.commit()
        return time_offset


def event_shutdown_clear_previous_downloads():
    rmtree(download_dir)


def register_events(app: FastAPI) -> FastAPI:
    """Sets up event handlers"""
    for var in globals().values():
        if callable(var):
            if var.__name__.startswith("event_startup_"):
                app.add_event_handler("startup", var)
            elif var.__name__.startswith("event_shutdown_"):
                app.add_event_handler("shutdown", var)
            elif var.__name__.startswith("event_all_"):
                app.add_event_handler("startup", var)
                app.add_event_handler("shutdown", var)
    return app
