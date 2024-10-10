import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger
from yutify.deezer import Deezer
from yutify.itunes import Itunes
from yutify.musicyt import MusicYT
from yutify.spoti import Spotipy, client_id, client_secret

# Initialize services
deezer = Deezer()
spotipy = Spotipy(client_id, client_secret)
yt_music = MusicYT()
itunes = Itunes()


def build_result(ytmusic_data=None, deezer_data=None, spotify_data=None, itunes_result=None):
    """Construct the final result using available data from YouTube Music, Deezer, and Spotify."""
    return {
        "album_art": (spotify_data or deezer_data or ytmusic_data).get("album_art"),
        "album_type": (spotify_data or ytmusic_data or deezer_data).get("album_type"),
        "album_title": (spotify_data or deezer_data or ytmusic_data).get("album_title"),
        "artists": (spotify_data or deezer_data or ytmusic_data).get("artists"),
        "deezer": deezer_data.get("url") if deezer_data else None,
        "itunes": itunes_result.get("url") if itunes_result else None,
        "release_date": (spotify_data or deezer_data or {}).get("release_date"),
        "spotify": spotify_data.get("url") if spotify_data else None,
        "title": (spotify_data or deezer_data or ytmusic_data).get("title"),
        "ytmusic": (
            {
                "id": ytmusic_data.get("id"),
                "url": ytmusic_data.get("url"),
            }
            if ytmusic_data
            else None
        ),
    }


def get_deezer_result(artist: str, song: str):
    """Search for the song in Deezer."""
    result = deezer.search_deez_songs(artist, song)
    if result:
        logger.info("Got result from Deezer.")
    else:
        logger.error("No result from Deezer.")
    return result


def get_itunes_result(artist: str, song: str):
    """Search for the song in iTunes Store"""
    result = itunes.search_itunes(artist, song)
    if result:
        logger.info("Got result from iTunes.")
    else:
        logger.error("No result from iTunes.")
    return result


def get_spotify_result(artist: str, song: str, deezer_data=None):
    """Search for the song in Spotify using Deezer data or fallback to user input."""
    if deezer_data:
        logger.info("Search Spotify with Deezer results.")
        result = spotipy.search_advance(
            deezer_data["artists"],
            deezer_data["title"],
            isrc=deezer_data.get("isrc"),
            upc=deezer_data.get("upc"),
        )
    else:
        logger.info("Search Spotify with user-provided data.")
        result = spotipy.search_music(artist, song)

    if result:
        logger.info("Got result from Spotify.")
    else:
        logger.info("Search Spotify with user-provided data.")
        result = spotipy.search_music(artist, song)

    return result


def get_ytmusic_result(artist: str, song: str):
    """Search for the song in YouTube Music."""
    result = yt_music.search_musicyt(artist, song)
    if result:
        logger.info("Got result from YouTube Music.")
    else:
        logger.error("No result from YouTube Music.")
    return result


def yutify_it(artist: str, song: str):
    """
    Search for a song on Deezer, Spotify, and YouTube Music,
    and return consolidated results if found on any platform.
    """
    deezer_result = get_deezer_result(artist, song)
    itunes_result = get_itunes_result(artist, song)
    spotify_result = get_spotify_result(artist, song, deezer_data=deezer_result)
    ytmusic_result = get_ytmusic_result(artist, song)

    # If no results found on any platform, return None
    if not (ytmusic_result or deezer_result or spotify_result or itunes_result):
        logger.error("NO RESULTS FOUND.")
        return None

    return build_result(ytmusic_result, deezer_result, spotify_result, itunes_result)
