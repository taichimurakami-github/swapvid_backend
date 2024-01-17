import json
from typing import Any
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


class ResponseBodyContent(ABC):
    """A response body content class that can be converted to a JSON serializable object."""

    @abstractmethod
    def to_json_serializable(self) -> Any:
        ...


class HttpPostHandlerBase(
    BaseHTTPRequestHandler,
):
    """Base class for HTTP POST request handlers."""

    def get_parsed_queries(self):
        """Parse the query string in the request path and return the result."""

        parsed_path = urlparse(self.path)
        parsed_queries = parse_qs(parsed_path.query)
        return parsed_queries

    def get_body_content_str(self):
        """Get the body content of the request as a string."""

        content_length = int(self.headers["content-length"])
        return self.rfile.read(content_length).decode("utf-8")

    def get_body_content_raw(self):
        """Get the body content of the request as a raw byte string."""

        content_length = int(self.headers["content-length"])
        return self.rfile.read(content_length)

    def send_ok_res(self, body_content_to_json, host_root_url: str):
        """Send success response with the given body content."""

        # create response header
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        # self.send_header("Access-Control-Allow-Origin", Config().frontend_url)
        self.send_header(
            "Access-Control-Allow-Origin",
            host_root_url,  # Allow CORS request from client
        )
        self.end_headers()

        # create response body
        self.wfile.write(json.dumps(body_content_to_json).encode("utf-8"))

    def send_error_res(self, status_code: int, error_type: str, error_content: str):
        """Send error response with the given error type and message."""

        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

        body_content = {"error_type": error_type, "error_content": error_content}
        self.wfile.write(json.dumps(body_content).encode("utf-8"))

    def terminate(self):
        """Terminate the connection."""
        self.close_connection = True

    @abstractmethod
    def do_POST(self):
        pass

    @abstractmethod
    def do_OPTIONS(self):
        pass
