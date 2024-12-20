#!/usr/bin/python3

"""This module contains code for serving static contents using flask framework"""

from flask import Flask
from app.config import download_dir


application = Flask(__name__, static_folder=download_dir, static_url_path="/static")

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)
