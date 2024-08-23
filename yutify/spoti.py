import base64
import json
import os
from pprint import pprint
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()


client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def spotipy(artist: str, song: str) -> dict | None:
    """Return a dictionary containing Spotify music URL or None

    Args:
        artist (str): Artist Name of the song
        song (str): Song Name

    Returns:
        dict | None: If successful, a dictionary containing music URL, else None
    """
    music_info = []

    url = "https://api.spotify.com/v1/search"
    token = get_spotify_token()
    headers = get_auth_header(token)

    query = f"?q={artist} - {song}&type=track,album"
    query_url = url + query

    response = requests.get(query_url, headers=headers)

    if response.status_code != 200:
        return None

    response_json = response.json()

    # Search `type` being "track" & "album", api will return two dictionaries,
    # one dictionary for "tracks" and one for "albums"
    try:
        for track in response_json["tracks"]["items"]:
            if music_info:
                return music_info[0]

            if (
                track["name"].lower() != song.lower()
                and track["name"].lower() not in song.lower()
                and song.lower() not in track["name"].lower()
            ):
                continue

            for artists in track["artists"]:
                artist_ids = search_artist(artist, token, headers)

                if (
                    artists["name"].lower() != artist.lower()
                    and artists["name"].lower() not in artist.lower()
                    and artists["id"] not in artist_ids
                ):
                    continue

                track_url = track["external_urls"]["spotify"]
                album_art = track["album"]["images"][0]["url"]
                music_info.append({"url": track_url, "album_art": album_art})

    except KeyError:
        pass

    try:
        for album in response_json["albums"]["items"]:
            if music_info:
                return music_info[0]
            if (
                album["name"].lower() != song.lower()
                and album["name"].lower() not in song.lower()
                and song.lower() not in album["name"].lower()
                ):
                continue

            for artists in album["artists"]:
                artist_ids = search_artist(artist, token, headers)

                if (
                    artists["name"].lower() != artist.lower()
                    and artists["name"].lower() not in artist.lower()
                    and artists["id"] not in artist_ids
                ):
                    continue

                album_url = album["external_urls"]["spotify"]
                album_art = album["images"][0]["url"]
                music_info.append({"url": album_url, "album_art": album_art})

    except KeyError:
        pass

    if music_info:
        return music_info[0]
    else:
        return None


def search_artist(artist, token, headers):
    url = "https://api.spotify.com/v1/search"
    query = f"?q={artist}&type=artist"

    query_url = url + query

    response = requests.get(query_url, headers=headers)
    response_json = response.json()["artists"]["items"]

    if len(response_json) == 0:
        return None

    artist_ids = []
    for artist in response_json:
        artist_ids.append(artist["id"])

    return artist_ids


def get_spotify_token() -> str:
    """Request Spotify access token

    Returns:
        str: Spotify access token
    """
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url=url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]

    return token


def get_auth_header(token: str) -> dict:
    """Header for sending request using access token.
    Will be used in every future requests made to web api.

    Args:
        token (str): Spotify access token returned by `get_spotify_token()` function.

    Returns:
        dict: header to be used with all requests made to spotify web api
    """
    return {"Authorization": f"Bearer {token}"}


if __name__ == "__main__":
    artist = input("Artist Name: ")
    song = input("Song Name: ")
    pprint(spotipy(artist, song))
