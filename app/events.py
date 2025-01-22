"""Startup and shutdown events"""

from app.utils import create_temp_dirs, download_dir
from fastapi import FastAPI
from shutil import rmtree
from app.db import create_tables


def event_startup_create_tempdirs():
    create_temp_dirs()


def event_startup_create_tables():
    create_tables()


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
