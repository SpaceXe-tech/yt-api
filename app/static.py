"""This module contains code for serving static contents using flask framework"""

from flask import Flask
from app.config import download_dir

static_app = Flask(
    __name__, static_folder=download_dir, static_url_path="/"
)

if __name__ == "__main__":
    static_app.run()
