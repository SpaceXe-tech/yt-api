#!/usr/bin/python

"""This script contains code for serving static contents using flask framework
The sole purpose of this is to reduce the work-load on youtube-downloader API.
Allows the API to only serve the dynamic contents as it focuses on static ones.
"""

from flask import Flask, request, send_from_directory
from app.config import download_dir
from urllib.parse import unquote
from os import getcwd
from pathlib import Path

app = Flask(__name__)
static_app = app
ref_directory = (
    download_dir
    if download_dir.is_absolute()
    else Path(getcwd()).joinpath(download_dir)
)


@app.get("/file/<path:name>")
def send_static_file(name):
    download = request.args.get("download", "0") in ("1", "true")
    response = send_from_directory(ref_directory, unquote(name), as_attachment=download)
    response.headers["Cache-Control"] = "public, max-age=7200"
    return response


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="youtube-downloader-static-server",
        description="Server for static contents ie. audio and video",
        epilog="For production environment use uwsgi.",
    )
    parser.add_argument(
        "-ho",
        "--host",
        help="Interface to bind to - %(default)s.",
        default="127.0.0.1",
    )
    parser.add_argument(
        "-p", "--port", help="Port to listen at - %(default)d", default=8888
    )
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=False)
