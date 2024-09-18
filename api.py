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

from yutify.musicyt import music_yt
from yutify.spoti import spotipy

try:
    redis_uri = os.environ["REDIS_URI"]
except KeyError:
    redis_uri = "memory:///"

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def default_error_responder(request_limit: RequestLimit):
    limit = str(request_limit.limit)
    limit = re.sub(r"(\d+)\s+per", r"\1 request(s) per", limit)
    return make_response(jsonify(error=f"ratelimit exceeded {limit}"), 429)


def is_valid_sting(string):
    return bool(string and (string.isalnum() or not string.isspace()))


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=redis_uri,
    strategy="fixed-window-elastic-expiry",
    on_breach=default_error_responder,
)


class Yutify(Resource):
    @limiter.limit("60 per minute")
    def get(self, artist, song):
        artist = artist.strip()
        song = song.strip()

        ytmusic = music_yt.search_musicyt(artist, song)
        spotify = spotipy.search_music(artist, song)

        if ytmusic and not spotify:
            spotify = spotipy.search_music(ytmusic["artists"], ytmusic["title"])

        elif not ytmusic and not spotify:
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


@app.route("/yutify")
def yutify_me():
    artist = request.args.get("artist").strip()
    song = request.args.get("song").strip()

    if not is_valid_sting(artist) and not is_valid_sting(song):
        return redirect(url_for(".index"))

    url = f"https://yutify.onrender.com/api/{artist}:{song}"
    response = requests.get(url)
    yutify = response.json()

    if response.status_code == 404:
        return render_template(
            "index.html",
            artist=artist,
            song=song,
            album_art="static/favicon.svg",
            title=f"{yutify['error']}",
        )

    album_art = yutify["album_art"]
    title = yutify["title"]
    album_type = yutify["album_type"]
    album_title = yutify["album_title"]
    artists = yutify["artists"]
    spotify = yutify["spotify"] if yutify["spotify"] != None else "#"
    yt_music = yutify["ytmusic"]["url"] if yutify["ytmusic"]["url"] != None else "#"

    return render_template(
        "index.html",
        artist=artist,
        song=song,
        album_art=f"{album_art}",
        title=f"{title}",
        album_type=f"{album_type}",
        album_title=f"{album_title}",
        artists=f"{artists}",
        spotify=f"{spotify}",
        yt_music=f"{yt_music}",
    )


@app.route("/docs")
def docs():
    return render_template("docs.html")


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
