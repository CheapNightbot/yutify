import base64
import json
import os
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()


client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def spotipy(artist: str, song: str) -> list[dict] | None:
    music_info = []
    url = "https://api.spotify.com/v1/search"
    token = get_spotify_token()
    headers = get_auth_header(token)

    artist_ = requests.utils.quote(artist)
    song_ = requests.utils.quote(song)

    query = f"?q=remaster%2520track%3A{song_}%2520artist%3A{artist_}&type=track%2Calbum&limit=10"
    query_backup = f"?q={song_}%20{artist_}&type=track%2Calbum&limit=5"
    query_urls = [url + query, url + query_backup]

    for query_url in query_urls:
        if music_info:
            return music_info

        response = requests.get(url=query_url, headers=headers)
        if response.status_code != 200:
            return None

        response_json = json.loads(response.content)

        # Search `type` being "track" & "album", api will return two dictionaries,
        # one dictionary for "tracks" and one for "albums"

        for track in response_json["tracks"]["items"]:
            if music_info:
                return music_info
            get_track_info(track, music_info)

        for album in response_json["albums"]["items"]:
            if music_info:
                return music_info
            get_album_info(album, music_info)


def get_track_info(track: dict, music_info: list):
    if track["name"].lower() != song.lower():
        return

    for artists in track["artists"]:
        if artists["name"].lower() != artist.lower():
            continue

        track_url = track["external_urls"]["spotify"]
        album_art = track["album"]["images"][0]["url"]
        music_info.append({"url": track_url, "album_art": album_art})


def get_album_info(album: dict, music_info: list):
    if album["name"].lower() != song.lower():
        return

    for artists in album["artists"]:
        if artists["name"].lower() != artist.lower():
            continue

        album_url = album["external_urls"]["spotify"]
        album_art = album["images"][0]["url"]
        music_info.append({"url": album_url, "album_art": album_art})


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
