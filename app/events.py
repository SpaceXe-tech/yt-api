"""Startup and shutdown events"""

from app.utils import create_temp_dirs
from fastapi import FastAPI


def event_startup_create_tempdirs():
    create_temp_dirs()


def register_events(app: FastAPI) -> FastAPI:
    """Sets up event handlers"""
    for var in globals().values():
        if callable(var):
            if var.__name__.startswith("event_startup_"):
                app.add_event_handler("startup", var)
            elif var.__name__.startswith("event_shutdown_"):
                app.add_event_handler("shutdown", var)
    return app
