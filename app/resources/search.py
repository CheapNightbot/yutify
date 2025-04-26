import os

from flask import jsonify, request
from flask_limiter.util import get_remote_address
from flask_restful import Resource
from yutipy import deezer, itunes, kkbox, musicyt, spotify, yutipy_music
from yutipy.logger import disable_logging

from app import cache
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

    @limiter.limit("20 per minute" if RATELIMIT else "")
    @cache.cached(
        timeout=300,
        key_prefix=lambda: f"search:{request.view_args['artist'].lower()}:{request.view_args['song'].lower()}:{list(request.args.keys())[0].lower() if request.args else 'all'}",
    )
    def get(self, artist, song):
        artist = artist.strip()
        song = song.strip()

        # Rate-limiting is not working per user ~ it's always 127.0.0.1 !!! _(:з)∠)_
        logger.info(
            "Request came from: `%s`",
            mask_string(request.headers.get("True-Client-Ip", get_remote_address())),
        )

        platform = "".join(list(request.args.keys())).lower() if request.args else "all"

        # Check if the result is in the cache
        cache_key = f"search:{artist}:{song}:{platform}"  # Construct the cache key
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for key: {cache_key}")
        else:
            logger.info(f"Cache miss for key: {cache_key}")

        result = self.__search_music(artist, song, platform)
        return jsonify(result)

    def __search_music(self, artist, song, platform="all"):
        """Search for music information based on artist, song, and platform."""
        artist = artist.strip()
        song = song.strip()

        logger.info("Artist: `%s`, Song: `%s`, Platform: `%s`", artist, song, platform)

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
                with musicyt.MusicYT() as youtube_music:
                    result = youtube_music.search(artist, song)
            case _:
                with yutipy_music.YutipyMusic() as py_music:
                    result = py_music.search(artist, song)

        if not result:
            result = {
                "error": f"Couldn't find '{song}' by '{artist}' on platform '{platform}'"
            }

        return result
