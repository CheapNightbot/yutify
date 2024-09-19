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
from yutify.musicyt import music_yt
from yutify.spoti import spotipy
from yutify.deezer import deezer

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

        logger.info(f"Request came from: `{replace_after_half(get_remote_address())}`") # Only for debugging !!
        logger.info(f"Artist: `{artist}` & Song: `{song}`")

        ytmusic = music_yt.search_musicyt(artist, song)
        spotify = spotipy.search_music(artist, song)
        deezzer = deezer.search_deez_songs(artist, song)

        if ytmusic and not spotify:
            logger.info("YouTube Music contains result, but Spotify is None.")
            logger.info("Searching Spotify again with the info from YouTube Music.")
            logger.info(f"From YTMusic ==> Artist: `{ytmusic['artists']}` & Song: `{ytmusic['title']}`")
            spotify = spotipy.search_music(ytmusic["artists"], ytmusic["title"])

        elif ytmusic and not deezzer:
            logger.info("YouTube Music contains result, but Deezer is None.")
            logger.info("Searching Deezer again with the info from YouTube Music.")
            logger.info(f"From YTMusic ==> Artist: `{ytmusic['artists']}` & Song: `{ytmusic['title']}`")
            deezzer = deezer.search_deez_songs(ytmusic["artists"], ytmusic["title"])

        elif not ytmusic and not spotify and not deezzer:
            abort(404, error=f"Couldn't find '{song}' by '{artist}'")


        result = {
            "album_art": spotify["album_art"] if spotify else deezzer["album_art"] if deezzer else ytmusic["album_art"],
            "album_type": spotify["album_type"] if spotify else deezzer["album_type"] if deezzer else ytmusic["album_type"],
            "album_title": spotify["album_title"] if spotify else ytmusic["album_title"],
            "artists": spotify["artists"] if spotify else ytmusic["artists"],
            "deezer": deezzer["url"] if deezzer else None,
            "spotify": spotify["url"] if spotify else None,
            "title": spotify["title"] if spotify else ytmusic["title"],
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
    album_title = yutify["album_title"]
    album_type = yutify["album_type"]
    artists = yutify["artists"]
    deezer = yutify["deezer"] if yutify["deezer"] != None else "#"
    spotify = yutify["spotify"] if yutify["spotify"] != None else "#"
    title = yutify["title"]
    yt_music = yutify["ytmusic"]["url"] if yutify["ytmusic"]["url"] != None else "#"

    return render_template(
        "index.html",
        album_art=f"{album_art}",
        album_title=f"{album_title}",
        album_type=f"{album_type}",
        artist=artist,
        artists=f"{artists}",
        deezer=f"{deezer}",
        song=song,
        spotify=f"{spotify}",
        title=f"{title}",
        yt_music=f"{yt_music}",
    )


@app.route("/docs")
def docs():
    return render_template("docs.html")


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
