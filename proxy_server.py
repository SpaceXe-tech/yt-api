#!/usr/bin/python

from flask import request, Flask, Response, jsonify
from flask.views import MethodView
from requests import Session
from requests.exceptions import Timeout
from dataclasses import dataclass
from os import path
import logging
import typing as t

session = Session()
session.headers = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "X-Application": "y2mate-clone;proxy",
}

request_timeout = None

app = Flask(__name__)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s : %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S %d-%b-%Y",
)


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
                detail=f"Connect timeout while connecting to API after {request_timeout}",
                timeout=504,
            )
        except Exception as e:
            err = ErrorResponse(
                detail=e.args[1] if e.args and len(e.args) > 1 else str(e),
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

    def get_absolute_url(self, endpoint: str) -> str:
        return path.join(self.api_base_url, endpoint)

    @view_error_handler
    def get(self, api_endpoint: str):
        """Handles get requests"""
        resp = session.get(
            self.get_absolute_url(api_endpoint),
            params=self.request_params,
            timeout=request_timeout,
        )
        logging.debug(
            f"Serving {request.remote_addr} - {api_endpoint} - {resp.status_code}"
        )
        return Response(
            response=resp.content,
            status=resp.status_code,
            headers=dict(resp.headers),
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
        )
        logging.debug(
            f"Serving {request.remote_addr} - {api_endpoint} - {resp.status_code}"
        )
        return Response(
            response=resp.content,
            status=resp.status_code,
            headers=dict(resp.headers),
            content_type=resp.headers.get("content-type"),
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="y2mate-clone-proxy",
        description="Proxy for y2mate-clone, meant to bridge http and https accordingly",
        epilog="Not meant for production purposes.",
    )
    parser.add_argument("base_url", help="Y2mate API base url.")
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
    app.add_url_rule("/<path:api_endpoint>", view_func=ProxyView.as_view("proxy"))
    request_timeout = args.timeout * 60
    logging.info(
        f"Starting server at {args.host}:{args.port} - upstream : {args.base_url}"
    )
    app.run(host=args.host, port=args.port, debug=True)
