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


class Spotipy:

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.__token = self.__get_spotify_token()
        self.__header = self.__get_auth_header(self.__token)

    def __get_spotify_token(self) -> str:
        """Request Spotify access token

        Returns:
            str: Spotify access token
        """
        auth_string = f"{self.client_id}:{self.client_secret}"
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

    def __get_auth_header(self, token: str) -> dict:
        """Header for sending request using access token.
        Will be used in every future requests made to web api.

        Args:
            token (str): Spotify access token returned by `get_spotify_token()` function.

        Returns:
            dict: header to be used with all requests made to spotify web api
        """
        return {"Authorization": f"Bearer {token}"}

    def search_music(self, artist: str, song: str) -> dict | None:
        """Return a dictionary containing Spotify music URL or None

        Args:
            artist (str): Artist Name of the song
            song (str): Song Name

        Returns:
            dict | None: If successful, a dictionary containing music URL, else None
        """
        music_info = []

        url = "https://api.spotify.com/v1/search"
        query = f"?q={artist} {song}&type=track,album&limit=10"
        query_url = url + query
        headers = self.__header

        response = requests.get(query_url, headers=headers)

        if response.status_code != 200:
            return None

        response_json = response.json()

        # Get artist ID for artists matching the `artist` string for later!
        artist_ids = self.get_artists_ids(artist)

        # Search `type` being "track" & "album", api will return two dictionaries,
        # one dictionary for "tracks" and one for "albums"

        for track in response_json["tracks"]["items"]:
            if music_info:
                return music_info[0]

            # Skip current track if it's name doesn't
            # match with `song` in any way..
            if (
                track["name"].lower() != song.lower()
                and track["name"].lower() not in song.lower()
                and song.lower() not in track["name"].lower()
            ):
                continue

            for artists in track["artists"]:

                if (
                    artists["name"].lower() != artist.lower()
                    and artists["name"].lower() not in artist.lower()
                    and artists["id"] not in artist_ids
                ):
                    continue

                track_url = track["external_urls"]["spotify"]
                album_art = track["album"]["images"][0]["url"]
                music_info.append({"url": track_url, "album_art": album_art})

        for album in response_json["albums"]["items"]:
            if music_info:
                return music_info[0]

            # Skip current album if it's name doesn't
            # match with `song` in any way..
            if (
                album["name"].lower() != song.lower()
                and album["name"].lower() not in song.lower()
                and song.lower() not in album["name"].lower()
            ):
                continue

            for artists in album["artists"]:

                if (
                    artists["name"].lower() != artist.lower()
                    and artists["name"].lower() not in artist.lower()
                    and artists["id"] not in artist_ids
                ):
                    continue

                album_url = album["external_urls"]["spotify"]
                album_art = album["images"][0]["url"]
                music_info.append({"url": album_url, "album_art": album_art})

        if music_info:
            return music_info[0]
        else:
            return None

    def get_artists_ids(self, artist: str) -> list | None:
        """Return a list of artists' Spotify Artist IDs matching `artist` string.

        Args:
            artist (str): Artist Name to search/get ID(s)

        Returns:
            list | None: List containg artists's IDs or None if couldn't find any.
        """
        url = "https://api.spotify.com/v1/search"
        query = f"?q={artist}&type=artist&limit=10"
        query_url = url + query
        headers = self.__header

        response = requests.get(query_url, headers=headers)
        response_json = response.json()["artists"]["items"]

        if len(response_json) == 0:
            return None

        artist_ids = []
        for artist in response_json:
            artist_ids.append(artist["id"])

        return artist_ids


spotipy = Spotipy(client_id, client_secret)


if __name__ == "__main__":

    spotipy = Spotipy(client_id, client_secret)

    artist = input("Artist Name: ")
    song = input("Song Name: ")

    pprint(spotipy.search_music(artist, song))
