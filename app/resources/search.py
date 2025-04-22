import os

from flask import jsonify, request
from flask_limiter.util import get_remote_address
from flask_restful import Resource
from yutipy import deezer, itunes, kkbox, musicyt, spotify, yutipy_music
from yutipy.logger import disable_logging

from app.common.logger import logger
from app.common.utils import mask_string
from app.resources.limiter import limiter

# idk, was getting two logs for same messages from yutipy
# doing this, disables extra one from yutipy
# however, yutipy's log messages still gets logged via
# app.common.logger ~ _(:з)∠)_
disable_logging()

RATELIMIT = int(os.environ.get("RATELIMIT"))


class YutifySearch(Resource):
    """API resource to search & fetch the song details."""

    # @limiter.limit("20 per minute" if RATELIMIT else "")
    @limiter.limit("1 per minute" if RATELIMIT else "")
    def get(self, artist, song):
        artist = artist.strip()
        song = song.strip()

        # Rate-limiting is not working per user ~ it's always 127.0.0.1 !!! _(:з)∠)_
        logger.info(
            "Request came from: `%s`",
            mask_string(request.headers.get("True-Client-Ip", get_remote_address())),
        )
        logger.info("Artist: `%s` & Song: `%s`", artist, song)

        platform = list(request.args.keys())
        platform = "".join(platform).lower()

        match platform:
            case "deezer":
                with deezer.Deezer() as deezer_music:
                    result = deezer_music.search(artist, song)
            case "itunes" | "apple-music":
                with itunes.Itunes() as apple_music:
                    result = apple_music.search(artist, song)
            case "kkbox":
                with kkbox.KKBox() as kkbox_music:
                    result = kkbox_music.search(artist, song)
            case "spotify":
                with spotify.Spotify() as spotify_music:
                    result = spotify_music.search(artist, song)
            case "ytmusic":
                with musicyt.MusicYT() as yotube_music:
                    result = yotube_music.search(artist, song)
            case _:
                with yutipy_music.YutipyMusic() as py_music:
                    result = py_music.search(artist, song)

        if not result:
            result = {"error": f"Couldn't find '{song}' by '{artist}'"}

        return jsonify(result)
