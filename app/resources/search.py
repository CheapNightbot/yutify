from flask import jsonify, request
from flask_limiter.util import get_remote_address
from flask_restful import Resource
from yutipy import Deezer, Itunes, KKBox, MusicYT, Spotify, YutipyMusic
from yutipy.logging import enable_logging

from app.common.logger import logger
from app.common.utils import mask_string
from app.resources.limiter import limiter

enable_logging()


class YutifySearch(Resource):
    """API resource to search & fetch the song details."""

    # @limiter.limit("20 per minute")
    @limiter.limit("1 per minute")
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
                with Deezer() as deezer:
                    result = deezer.search(artist, song)
            case "itunes" | "apple-music":
                with Itunes() as itunes:
                    result = itunes.search(artist, song)
            case "kkbox":
                with KKBox() as kkbox:
                    result = kkbox.search(artist, song)
            case "spotify":
                with Spotify() as spotify:
                    result = spotify.search(artist, song)
            case "ytmusic":
                with MusicYT() as ytmusic:
                    result = ytmusic.search(artist, song)
            case _:
                with YutipyMusic() as yutipy_music:
                    result = yutipy_music.search(artist, song)

        if not result:
            result = {"error": f"Couldn't find '{song}' by '{artist}'"}

        return jsonify(result)
