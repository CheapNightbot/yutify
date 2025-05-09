import os
import re

from flask import jsonify, make_response, request
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address


def default_error_responder(request_limit: RequestLimit):
    """Default response for rate-limited requests."""
    limit = re.sub(r"(\d+)\s+per", r"\1 request(s) per", str(request_limit.limit))
    return make_response(
        jsonify(error=f"ratelimit exceeded! you are allowed to make {limit}."), 429
    )


limiter = Limiter(
    key_func=lambda: request.headers.get("True-Client-Ip", get_remote_address()),
    strategy="fixed-window",
    on_breach=default_error_responder,
    storage_uri=os.environ.get("REDIS_URI", "memory:///"),
)
