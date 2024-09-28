import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger
from yutify.deezer import Deezer
from yutify.musicyt import MusicYT
from yutify.spoti import Spotipy, client_id, client_secret

deezer = Deezer()
spotipy = Spotipy(client_id, client_secret)
yt_music = MusicYT()


def yutify_it(artist: str, song: str):

    deez_result = deezer.search_deez_songs(artist, song)
    spotify_result = None
    ytmusic_result = yt_music.search_musicyt(artist, song)

    # YES!
    album_art = None
    album_type = None
    album_title = None
    artists = None
    release_date = None
    title = None

    if ytmusic_result:
        logger.info("Got result from YouTube Music.")
    else:
        logger.error("No result from YouTube Music.")
        ytmusic_result = None

    if deez_result:
        logger.info("Got result from Deezer.")

        album_art = deez_result["album_art"]
        album_type = deez_result["album_type"]
        album_title = deez_result["album_title"]
        artists = deez_result["artists"]
        release_date = deez_result["release_date"]
        title = deez_result["title"]

        logger.info("Search Spotify with Deezer results.")
        spotify_result = spotipy.search_advance(
            artists, title, isrc=deez_result["isrc"], upc=deez_result["upc"]
        )

    if not spotify_result:
        logger.info("Search Spotify with user provided data.")
        spotify_result = spotipy.search_music(artist, song)

    if spotify_result:
        logger.info("Got result from Spotify.")
        album_art = spotify_result["album_art"]
        album_type = spotify_result["album_type"]
        album_title = spotify_result["album_title"]
        artists = spotify_result["artists"]
        release_date = spotify_result["release_date"]
        title = spotify_result["title"]

    if (
        not deez_result
        and not spotify_result
        and not ytmusic_result
    ):
        logger.error("NO RESULTS FOUND.")
        return None

    result = {
        "album_art": album_art if album_art else ytmusic_result["album_art"],
        "album_type": album_type if album_type else ytmusic_result["album_type"],
        "album_title": album_title if album_title else ytmusic_result["album_title"],
        "artists": artists if artists else ytmusic_result["artists"],
        "deezer": deez_result["url"] if deez_result else None,
        "release_date": release_date,
        "spotify": spotify_result["url"] if spotify_result else None,
        "title": title if title else ytmusic_result["title"],
        "ytmusic": {
            "id": ytmusic_result["id"] if ytmusic_result else None,
            "url": ytmusic_result["url"] if ytmusic_result else None,
        },
    }

    return result
