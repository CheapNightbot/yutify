import logging
import os
from collections import OrderedDict
from dataclasses import asdict
from typing import Union

import sqlalchemy as sa
from flask import request
from flask_restful import Resource
from yutipy import deezer, itunes, musicyt, yutipy_music
from yutipy.exceptions import KKBoxException, SpotifyException
from yutipy.kkbox import KKBox
from yutipy.logger import enable_logging
from yutipy.spotify import Spotify

from app import cache, db
from app.limiter import limiter
from app.models import Service
from app.resources.docs_demo import ALL, DEEZER, ITUNES, KKBOX, SPOTIFY, YTMUSIC

# Create a logger for this module
logger = logging.getLogger(__name__)
enable_logging(handler=logger)

RATELIMIT = os.environ.get("RATELIMIT")


class BaseOverride:
    """Custom Base class to override the `save_access_token` and `load_access_token` methods.

    Only works for Client Credential grant type/flow.
    """

    SERVICE_NAME: str
    SERVICE_URL: str
    IS_PRIVATE: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save_access_token(self, token_info: dict) -> None:
        service = db.session.scalar(
            sa.select(Service).where(Service.name.ilike(self.SERVICE_NAME.lower()))
        )
        if not service:
            service = Service(
                name=self.SERVICE_NAME,
                url=self.SERVICE_URL,
                is_private=self.IS_PRIVATE,
            )
            db.session.add(service)  # Add the new service to the session

        # Set the access token values
        service.access_token = token_info.get("access_token")
        service.expires_in = token_info.get("expires_in")
        service.requested_at = token_info.get("requested_at")

        # Commit the changes to the database
        db.session.commit()

    def load_access_token(self) -> Union[dict, None]:
        service = db.session.scalar(
            sa.select(Service).where(Service.name.ilike(self.SERVICE_NAME.lower()))
        )

        if service:
            return {
                "access_token": service.access_token,
                "expires_in": service.expires_in,
                "requested_at": service.requested_at,
            }

        return None


class MySpotify(Spotify, BaseOverride):
    """Custom Spotify class to override the `save_access_token` and `load_access_token` methods."""

    SERVICE_NAME = "Spotify"
    SERVICE_URL = "https://open.spotify.com"


class MyKKBox(KKBox, BaseOverride):
    """Custom KKBox class to override the `save_access_token` and `load_access_token` methods."""

    SERVICE_NAME = "KKBox"
    SERVICE_URL = "https://www.kkbox.com"
    IS_PRIVATE = True


class YutifySearch(Resource):
    """API resource to search & fetch the song details."""

    @limiter.limit(RATELIMIT if RATELIMIT else "")
    @cache.cached(
        timeout=3600,  # cache for 1 hour
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
        logger.info("Artist: `%s`, Song: `%s`, Platform: `%s`", artist, song, platform)

        if artist == "Artist" and song == "Song":
            if platform == "deezer":
                result = asdict(DEEZER)
            elif platform == "itunes" or platform == "apple-music":
                result = asdict(ITUNES)
            elif platform == "kkbox":
                result = asdict(KKBOX)
            elif platform == "spotify":
                result = asdict(SPOTIFY)
            elif platform == "ytmusic":
                result = asdict(YTMUSIC)
            else:
                result = asdict(ALL)
            return OrderedDict(sorted(result.items())), 200

        match platform:
            case "deezer":
                with deezer.Deezer() as deezer_music:
                    result = deezer_music.search(artist, song, limit=3)
            case "itunes" | "apple-music":
                with itunes.Itunes() as apple_music:
                    result = apple_music.search(artist, song, limit=3)
            case "kkbox":
                try:
                    with MyKKBox() as kkbox_music:
                        result = kkbox_music.search(artist, song, limit=3)
                except KKBoxException as e:
                    logger.warning(
                        f"KKBox Search is disabled due to following error:\n{e}"
                    )
                    result = None
            case "spotify":
                try:
                    with MySpotify() as spotify_music:
                        result = spotify_music.search(artist, song, limit=3)
                except SpotifyException as e:
                    logger.warning(
                        f"Spotify Search is disabled due to following error:\n{e}"
                    )
                    result = None
            case "ytmusic":
                with musicyt.MusicYT() as youtube_music:
                    result = youtube_music.search(artist, song, limit=3)
            case _:
                with yutipy_music.YutipyMusic(
                    custom_kkbox_class=MyKKBox, custom_spotify_class=MySpotify
                ) as py_music:
                    result = py_music.search(artist, song, limit=3)

        if not result:
            msg = (
                f"Couldn't find '{song}' by '{artist}'"
                if platform == "all"
                else f"Couldn't find '{song}' by '{artist}' on platform '{platform.title()}'"
            )
            result = {"error": msg}, 404
        else:
            result = OrderedDict(sorted(asdict(result).items())), 200

        return result
