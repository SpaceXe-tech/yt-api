#!/usr/bin/python
"""Hosting web-interface over https makes http (insecure) API calls to fail except to localhost.
So this script links the two; a youtube-downloader API accessible over http and a web-interface that's
accessible securely (https).

# Steps

1. Host youtube-downloader over http (insecure)
2. Start this proxy (locally) and point base_url to the address of youtube-downloader
3. Point API-BASE-URL in web-interface to proxy's address.
"""
from flask import request, Flask, Response, jsonify
from flask.views import MethodView
from flask_cors import CORS
from requests import Session
from requests.exceptions import Timeout
from dataclasses import dataclass
from os import path
import logging
import typing as t
from app.config import loaded_config

session = Session()
session.headers = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "X-Application": "y2mate-clone;proxy",
}

request_timeout = None

app = Flask(__name__)


cors = CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*",
            "allow_headers": ["Content-Type", "Authorization", "X-Application"],
            "expose_headers": ["Location"],
            "methods": ["GET", "POST"],
        }
    },
)


logging.basicConfig(
    format="%(asctime)s - %(levelname)s : %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S %d-%b-%Y",
)

get_exception_string = lambda e: e.args[1] if e.args and len(e.args) > 1 else str(e)


@dataclass
class ErrorResponse:
    detail: str
    """Error message in detail"""
    status_code: int = 500
    """Error status code"""

    def respond(self) -> dict:
        """complete app-compatible response"""
        return (jsonify(dict(detail=self.detail)), self.status_code)


def view_error_handler(func: t.Callable):
    """Silence view exceptions and respond accordingly"""

    def decorator(*args, **kwargs):
        try:
            err = None
            return func(*args, **kwargs)
        except Timeout:
            err = ErrorResponse(
                detail=f"Connection timed out while connecting to API after {request_timeout}",
                timeout=504,
            )
        except Exception as e:
            err = ErrorResponse(
                detail=get_exception_string(e),
                status_code=500,
            )
        finally:
            if err:
                return err.respond()

    return decorator


class ProxyView(MethodView):
    """Does the whole handling of both GET and POST requests"""

    init_every_request = False
    api_base_url: str = None
    methods = ["GET", "POST"]

    @property
    def request_params(self) -> dict:
        """Extracts current request parameters"""
        return dict(request.args)

    @property
    def request_headers(self) -> dict:
        """Updated upstream request headers"""
        return {"X-Real-Ip": request.remote_addr}

    def get_absolute_url(self, endpoint: str) -> str:
        return path.join(self.api_base_url, endpoint)

    def process_resp_headers(self, request_headers) -> dict:
        x_date = request_headers.get("Date")
        x_server = request_headers.get("server")
        request_headers.pop("Date")
        request_headers.pop("Server")
        response_headers = dict(request_headers)
        response_headers["X-Date"] = x_date
        response_headers["X-Server"] = x_server
        return response_headers

    @view_error_handler
    def get(self, api_endpoint: str):
        """Handles get requests"""
        resp = session.get(
            self.get_absolute_url(api_endpoint),
            params=self.request_params,
            timeout=request_timeout,
            headers=self.request_headers,
        )
        logging.debug(
            f"Serving {request.remote_addr} - {api_endpoint} - {resp.status_code}"
        )
        return Response(
            response=resp.content,
            status=resp.status_code,
            headers=self.process_resp_headers(resp.headers),
            content_type=resp.headers.get("content-type"),
        )

    @view_error_handler
    def post(self, api_endpoint: str):
        """Handles get requests"""
        resp = session.post(
            self.get_absolute_url(api_endpoint),
            params=self.request_params,
            json=request.json,
            timeout=request_timeout,
            headers=self.request_headers,
        )
        logging.debug(
            f"Serving {request.remote_addr} - {api_endpoint} - {resp.status_code}"
        )
        return Response(
            response=resp.content,
            status=resp.status_code,
            headers=self.process_resp_headers(resp.headers),
            content_type=resp.headers.get("content-type"),
        )


app.add_url_rule("/<path:api_endpoint>", view_func=ProxyView.as_view("proxy"))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="youtube-downloader--proxy",
        description=(
            "Meant to forward request to and fro"
            " youtube-downloader API serving on http"
        ),
        epilog="Not meant for production purposes.",
    )
    parser.add_argument("base_url", help="Youtube-Downloader API base url.")
    parser.add_argument(
        "-ho",
        "--host",
        help="Interface to bind to - %(default)s.",
        default="127.0.0.1",
    )
    parser.add_argument(
        "-p", "--port", help="Port to listen at - %(default)d", default=8080
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        help="API request call timeout in minutest - %(default)d",
        default=30,
    )
    args = parser.parse_args()
    if not args.base_url.startswith("http"):
        print(
            f"Error : Upstream proxy must have protocol [http|http] - {args.base_url}"
        )
        exit(1)
    ProxyView.api_base_url = args.base_url
    request_timeout = args.timeout * 60
    logging.info(
        f"Starting server at {args.host}:{args.port} - upstream : {args.base_url}"
    )
    try:
        test_resp = session.get(
            path.join(ProxyView.api_base_url, "api/live-check"), timeout=20
        )
        if not test_resp.ok:
            print(
                f"Error : API failed to pass live-status check - ({test_resp.status_code}, {test_resp.reason}, {test_resp.text}) "
            )
            exit(1)
    except Exception as e:
        print(
            f"Error : Unable to reach API at - {ProxyView.api_base_url} due to : {get_exception_string(e)}"
        )
        exit(1)
    app.run(host=args.host, port=args.port, debug=False)


else:
    ProxyView.api_base_url = loaded_config.api_base_url_validated
