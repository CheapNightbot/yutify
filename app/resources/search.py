import logging
import os
from dataclasses import asdict

from flask import request
from flask_restful import Resource
from yutipy import deezer, itunes, kkbox, musicyt, spotify, yutipy_music
from yutipy.exceptions import KKBoxException, SpotifyException
from yutipy.logger import enable_logging

from app import cache
from app.limiter import limiter

# Create a logger for this module
logger = logging.getLogger(__name__)
enable_logging(handler=logger)

RATELIMIT = os.environ.get("RATELIMIT")


class YutifySearch(Resource):
    """API resource to search & fetch the song details."""

    @limiter.limit(RATELIMIT if RATELIMIT else "")
    @cache.cached(
        timeout=300,
        key_prefix=lambda: f"search:{request.view_args['artist'].lower()}:{request.view_args['song'].lower()}:{list(request.args.keys())[0].lower() if request.args else 'all'}",
    )
    def get(self, artist, song):
        artist = artist.strip()
        song = song.strip()
        platform = "".join(list(request.args.keys())).lower() if request.args else "all"

        # Check if the result is in the cache
        cache_key = f"search:{artist}:{song}:{platform}"  # Construct the cache key
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for key: {cache_key}")
        else:
            logger.info(f"Cache miss for key: {cache_key}")

        result = self.__search_music(artist, song, platform)
        return result

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
                try:
                    with kkbox.KKBox() as kkbox_music:
                        result = kkbox_music.search(artist, song)
                except KKBoxException as e:
                    logger.warning(
                        f"KKBox Search is disabled due to following error:\n{e}"
                    )
                    result = None
            case "spotify":
                try:
                    with spotify.Spotify() as spotify_music:
                        result = spotify_music.search(artist, song)
                except SpotifyException as e:
                    logger.warning(
                        f"Spotify Search is disabled due to following error:\n{e}"
                    )
                    result = None
            case "ytmusic":
                with musicyt.MusicYT() as youtube_music:
                    result = youtube_music.search(artist, song)
            case _:
                with yutipy_music.YutipyMusic() as py_music:
                    result = py_music.search(artist, song)

        if not result:
            result = {
                "error": f"Couldn't find '{song}' by '{artist}' on platform '{platform}'"
            }, 404
        else:
            result = asdict(result), 200

        return result
