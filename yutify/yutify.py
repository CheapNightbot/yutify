import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger
from utils.cheap_utils import cheap_compare
from yutify.deezer import Deezer
from yutify.itunes import Itunes
from yutify.musicyt import MusicYT
from yutify.spoti import Spotipy, client_id, client_secret

# Initialize services
deezer = Deezer()
spotipy = Spotipy(client_id, client_secret)
yt_music = MusicYT()
itunes = Itunes()

# Global Variable
priority = None


def build_result(
    ytmusic_data=None, deezer_data=None, spotify_data=None, itunes_result=None
):
    """Construct the final result using available data from YouTube Music, Deezer, and Spotify."""
    global priority
    match priority:
        case "spotify":
            result = spotify_data
        case "deezer":
            result = deezer_data
        case "itunes":
            result = ytmusic_data
        case _:
            result = ytmusic_data
    return {
        "album_art": result.get("album_art"),
        "album_type": result.get("album_type"),
        "album_title": result.get("album_title"),
        "artists": result.get("artists"),
        "deezer": deezer_data.get("url") if deezer_data else None,
        "itunes": itunes_result.get("url") if itunes_result else None,
        "release_date": (spotify_data or deezer_data or {}).get("release_date"),
        "spotify": spotify_data.get("url") if spotify_data else None,
        "title": result.get("title"),
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


def get_spotify_result(
    artist: str, song: str, deezer_data=None, itunes_data=None, ytmusic_data=None
):
    global priority
    result = None
    if deezer_data and cheap_compare(deezer_data["title"], song):
        priority = "deezer"
        logger.info("Search Spotify with Deezer results.")
        result = spotipy.search_advance(
            deezer_data["artists"],
            deezer_data["title"],
            isrc=deezer_data.get("isrc"),
            upc=deezer_data.get("upc"),
        )

    elif itunes_data and cheap_compare(itunes_data["title"], song):
        logger.info("Search Spotify with iTunes results.")
        result = spotipy.search_music(itunes_data["artists"], itunes_data["title"])

    elif ytmusic_data and cheap_compare(ytmusic_data["title"], song):
        priority = "ytmusic"
        logger.info("Search Spotify with YouTube Music results.")
        result = spotipy.search_music(ytmusic_data["title"], ytmusic_data["artists"])

    if result:
        priority = "spotify"
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
    ytmusic_result = get_ytmusic_result(artist, song)
    spotify_result = get_spotify_result(
        artist,
        song,
        deezer_data=deezer_result,
        itunes_data=itunes_result,
        ytmusic_data=ytmusic_result,
    )

    # If no results found on any platform, return None
    if not (ytmusic_result or deezer_result or spotify_result or itunes_result):
        logger.error("NO RESULTS FOUND.")
        return None

    return build_result(ytmusic_result, deezer_result, spotify_result, itunes_result)
