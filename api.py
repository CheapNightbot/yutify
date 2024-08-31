import os
import re

from flask import Flask, jsonify, make_response, render_template
from flask_cors import CORS
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address
from flask_restful import Api, Resource, abort
from waitress import serve

from yutify import musicyt
from yutify.spoti import spotipy

redis_uri = os.environ["REDIS_URI"]

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def default_error_responder(request_limit: RequestLimit):
    limit = str(request_limit.limit)
    limit = re.sub(r"(\d+)\s+per", r"\1 request(s) per", limit)
    return make_response(jsonify(error=f"ratelimit exceeded {limit}"), 429)


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=redis_uri,
    strategy="fixed-window",
    on_breach=default_error_responder,
)


class Yutify(Resource):
    @limiter.limit("60 per minute")
    def get(self, artist, song):
        ytmusic = musicyt.search_musicyt(artist, song)
        spotify = spotipy.search_music(artist, song)

        if not ytmusic and not spotify:
            abort(404, error=f"Couldn't find '{song}' by '{artist}'")

        elif ytmusic and not spotify:
            spotify = spotipy.search_music(ytmusic["artists"], ytmusic["title"])

        elif not ytmusic or not spotify:
            abort(404, error=f"Couldn't find '{song}' by '{artist}'")

        result = {
            "album_art": spotify["album_art"] if spotify else ytmusic["album_art"],
            "spotify": spotify["url"] if spotify else None,
            "title": spotify["title"] if spotify else ytmusic["title"],
            "album_title": (
                spotify["album_title"] if spotify else ytmusic["album_title"]
            ),
            "album_type": spotify["album_type"] if spotify else ytmusic["album_type"],
            "artists": (spotify["artists"] if spotify else ytmusic["artists"]),
            "ytmusic": {
                "id": ytmusic["id"] if ytmusic else None,
                "url": ytmusic["url"] if ytmusic else None,
            },
        }

        return jsonify(result)


api.add_resource(Yutify, "/api/<path:artist>:<path:song>")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
