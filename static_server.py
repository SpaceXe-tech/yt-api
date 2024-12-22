#!/usr/bin/python

"""This module contains code for serving static contents using flask framework"""

from flask import Flask, request, send_from_directory
from app.config import download_dir
from urllib.parse import unquote
from os import getcwd
from pathlib import Path

static_app = Flask(__name__, static_url_path="/xxxxxxxx")

ref_directory = (
    download_dir
    if download_dir.is_absolute()
    else Path(getcwd()).joinpath(download_dir)
)


@static_app.get("/file/<path:name>")
def send_static_file(name):
    download = request.args.get("download", "0") in ("1", "true")
    return send_from_directory(ref_directory, unquote(name), as_attachment=download)


if __name__ == "__main__":
    static_app.run(host="0.0.0.0", port=8080)
