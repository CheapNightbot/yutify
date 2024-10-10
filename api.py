import os
import re

import requests
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_cors import CORS
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address
from flask_restful import Api, Resource, abort
from waitress import serve

from utils.logger import logger
from utils.replace import replace_after_half
from yutify.yutify import yutify_it

# Configuring Redis URI
redis_uri = os.getenv("REDIS_URI", "memory:///")

# Initialize Flask app and extensions
app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


# Helper Functions
def default_error_responder(request_limit: RequestLimit):
    """
    Default response for rate-limited requests.
    """
    limit = re.sub(r"(\d+)\s+per", r"\1 request(s) per", str(request_limit.limit))
    return make_response(jsonify(error=f"ratelimit exceeded {limit}"), 429)


def is_valid_string(string: str) -> bool:
    """
    Validate if a string is non-empty, alphanumeric, or contains non-whitespace characters.
    """
    return bool(string and (string.isalnum() or not string.isspace()))


def fetch_yutify_data(artist: str, song: str):
    """
    Fetch song details using the yutify_it function.
    """
    result = yutify_it(artist, song)
    if not result:
        abort(404, error=f"Couldn't find '{song}' by '{artist}'")
    return result


def build_response_template(response, artist, song):
    """
    Construct the response for rendering the HTML template.
    """
    if response.status_code == 404:
        return render_template(
            "index.html",
            artist=artist,
            song=song,
            album_art="static/favicon.svg",
            title=response.json().get("error"),
        )

    yutify_data = response.json()
    return render_template(
        "index.html",
        album_art=yutify_data.get("album_art"),
        album_title=yutify_data.get("album_title"),
        album_type=yutify_data.get("album_type"),
        artist=artist,
        artists=yutify_data.get("artists"),
        deezer=yutify_data.get("deezer"),
        itunes=yutify_data.get("itunes"),
        song=song,
        spotify=yutify_data.get("spotify"),
        title=yutify_data.get("title"),
        yt_music=yutify_data["ytmusic"].get("url") if yutify_data["ytmusic"] else None,
    )


# Flask Limiter Setup
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=redis_uri,
    strategy="fixed-window-elastic-expiry",
    on_breach=default_error_responder,
)


# API Resource for Yutify
class Yutify(Resource):
    @limiter.limit("60 per minute")
    def get(self, artist, song):
        """
        GET method to fetch song details from Deezer, Spotify, and YouTube Music.
        """
        artist = artist.strip()
        song = song.strip()

        logger.info(f"Request came from: `{replace_after_half(get_remote_address())}`")
        logger.info(f"Artist: `{artist}` & Song: `{song}`")

        result = fetch_yutify_data(artist, song)
        return jsonify(result)


api.add_resource(Yutify, "/api/<path:artist>:<path:song>")


@app.route("/")
def index():
    """
    Render the main index/home page.
    """
    return render_template("index.html")


@app.route("/yutify")
def yutify_me():
    """
    Handle the yutify search from the web form (@index.html).
    """
    artist = request.args.get("artist", "").strip()
    song = request.args.get("song", "").strip()

    logger.info("Request came from website / UI.")

    # Check for invalid input
    if not is_valid_string(artist) or not is_valid_string(song):
        return redirect(url_for(".index"))

    url = f"https://yutify.onrender.com/api/{artist}:{song}"
    response = requests.get(url)

    # Render the appropriate response based on the status code
    return build_response_template(response, artist, song)


@app.route("/docs")
def docs():
    """
    Render the API documentation page.
    """
    return render_template("docs.html")


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
