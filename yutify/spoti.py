import base64
import json
import os
import sys
import time
from pprint import pprint
from datetime import datetime

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cheap_utils import is_kinda_same, sep_artists
from utils.logger import logger

load_dotenv()


client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

SEARCH_ENDPOINT = "https://api.spotify.com/v1/search"
date_format = "%Y, %B %d"


class Spotipy:

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.__start_time = time.time()
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

        if token:
            logger.info("Spotify access token request successful.")
        else:
            logger.warning("Spotify access token request unsuccessful!")

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
        """Return a dictionary containing Spotify music URL and other info or None

        Args:
            artist (str): Artist Name of the song
            song (str): Song Name

        Returns:
            dict | None: If successful, a dictionary containing music URL, else None
        """
        # If it's been 1 hour, the Spotify access token has expired..
        # Check and request new access token
        elapsed_time = time.time() - self.__start_time
        if elapsed_time >= 3600:
            logger.info("Requesting new Spotify access token.")
            self.__start_time = time.time()
            self.__token = self.__get_spotify_token()
            self.__header = self.__get_auth_header(self.__token)

        music_info = []

        url = SEARCH_ENDPOINT
        query = f"?q={artist} {song}&type=track,album&limit=10"
        query_url = url + query
        headers = self.__header

        logger.info(f"Spotify Search Query: `{query}`")

        response = requests.get(query_url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Spotify returned with status code: {response.status_code}")
            return None

        response_json = response.json()

        # Get artist ID for artists matching the `artist` string for later!
        artist_ids = self.get_artists_ids(artist)

        # Search `type` being "track" & "album", api will return two dictionaries,
        # one dictionary for "tracks" and one for "albums"
        tracks = response_json["tracks"]["items"]
        albums = response_json["albums"]["items"]

        if not tracks and not albums:
            logger.warning(f"Spotify returned with status code: {response.status_code}, BUT it's empty!")
            return None

        for track in tracks:
            if music_info:
                return music_info[0]

            self.find_tracks(song, artist, track, artist_ids, music_info)

        if music_info:
            return music_info[0]

        for album in albums:
            if music_info:
                return music_info[0]

            self.find_album(song, artist, album, artist_ids, music_info)

        if music_info:
            return music_info[0]
        else:
            return None

    def search_advance(self, artist: str, song: str, isrc: str, upc: str) -> dict | None:
        # If it's been 1 hour, the Spotify access token has expired..
        # Check and request new access token
        elapsed_time = time.time() - self.__start_time
        if elapsed_time >= 3600:
            logger.info("Requesting new Spotify access token.")
            self.__start_time = time.time()
            self.__token = self.__get_spotify_token()
            self.__header = self.__get_auth_header(self.__token)

        music_info = []

        url = SEARCH_ENDPOINT

        if isrc:
            query = f"?q={artist} {song} isrc:{isrc}&type=track&limit=1"
        elif upc:
            query = f"?q={artist} {song} upc:{upc}&type=album&limit=1"

        query_url = url + query
        headers = self.__header

        logger.info(f"Spotify Search Query: `{query}`")

        response = requests.get(query_url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Spotify returned with status code: {response.status_code}")
            return None

        response_json = response.json()

        if isrc:
            try:
                result = response_json["tracks"]["items"][0]
            except IndexError:
                logger.warning(f"Spotify returned with status code: {response.status_code}, BUT it's empty!")
                return None

            artists = []
            for artist in result["artists"]:
                artists.append(artist["name"])

            if result["album"]["release_date_precision"] == "day":
                release_date = datetime.strptime(result["album"]["release_date"], "%Y-%m-%d").strftime(date_format)
            else:
                release_date = datetime.strptime(result["album"]["release_date"], "%Y-%m").strftime(date_format)

            music_info.append(
                {
                    "album_art": result["album"]["images"][0]["url"],
                    "artists": ", ".join(artists),
                    "title": result["name"],
                    "album_type": result["album"]["album_type"],
                    "album_title": result["album"]["name"],
                    "release_date": release_date,
                    "url": result["external_urls"]["spotify"],
                }
            )

            return music_info[0]

        elif upc:
            try:
                result = response_json["albums"]["items"][0]
            except IndexError:
                logger.warning(f"Spotify returned with status code: {response.status_code}, BUT it's empty!")
                return None

            artists = []
            for artist in result["artists"]:
                artists.append(artist["name"])

            if result["release_date_precision"] == "day":
                release_date = datetime.strptime(result["release_date"], "%Y-%m-%d").strftime(date_format)
            else:
                release_date = datetime.strptime(result["release_date"], "%Y-%m").strftime(date_format)

            music_info.append(
                {
                    "album_art": result["images"][0]["url"],
                    "artists": ", ".join(artists),
                    "title": result["name"],
                    "album_type": result["album_type"],
                    "album_title": result["name"],
                    "release_date": release_date,
                    "url": result["external_urls"]["spotify"],
                }
            )

            return music_info[0]

    def get_artists_ids(self, artist: str) -> list | None:
        """Return a list of artists' Spotify Artist IDs matching `artist` string.

        Args:
            artist (str): Artist Name to search/get ID(s)

        Returns:
            list | None: List containg artists's IDs or None if couldn't find any.
        """
        artist_ids = []
        artists = sep_artists(artist)

        for name in artists:
            url = SEARCH_ENDPOINT
            query = f"?q={name}&type=artist&limit=5"
            query_url = url + query
            headers = self.__header

            logger.info(f"Spotify Search [@get_artists_id()] Query: `{query}`")

            response = requests.get(query_url, headers=headers)

            if response.status_code != 200:
                logger.error(f"Spotify [@get_artists_id()] returned with status code: {response.status_code}")
                return None

            response_json = response.json()["artists"]["items"]

            if not response_json:
                logger.warning(f"Spotify [@get_artists_id()] returned with status code: {response.status_code}, BUT it's empty!")

            for artist in response_json:
                artist_ids.append(artist["id"])

        return artist_ids

    def find_tracks(self, song, artist, track, artist_ids, music_info) -> None:
        """Helper function to find and add song info to `music_info` list if found.

        Args:
            song (str): Song name provided by the user.
            artist (str): Artist name provided by the user.
            track (dict): Single track, returned by Spotify search endpoint.
            artist_ids (list): List of artist ids, return by `get_artists_ids()` function.
            music_info (list): List to add music info to, if found.
        """
        # Skip current track if it's name doesn't
        # match with `song` in any way..

        if not is_kinda_same(track["name"], song):
            return

        temp = []
        for x in track["artists"]:
            temp.append(x["name"])

        artists_name = []
        for artists in track["artists"]:
            if (
                not is_kinda_same(artists["name"], artist)
                and artists["id"] not in artist_ids
                and artists["name"] not in temp
                and not artists_name
            ):
                continue

            artists_name.append(artists["name"])

        if artist in artists_name:
            track_url = track["external_urls"]["spotify"]
            album_art = track["album"]["images"][0]["url"]
            title = track["name"]
            artists_ = ", ".join(artists_name)
            album_type = track["album"]["album_type"]
            album_title = track["album"]["name"]

            if track["album"]["release_date_precision"] == "day":
                release_date = datetime.strptime(track["album"]["release_date"], "%Y-%m-%d").strftime(date_format)
            else:
                release_date = datetime.strptime(track["album"]["release_date"], "%Y-%m").strftime(date_format)


            music_info.append(
                {
                    "album_art": album_art,
                    "artists": artists_,
                    "title": title,
                    "album_type": album_type,
                    "album_title": album_title,
                    "url": track_url,
                    "release_date": release_date,
                }
            )

    def find_album(self, song, artist, album, artist_ids, music_info) -> None:
        """Helper function to find and add album info to `music_info` list if found.

        Args:
            song (str): Song name provided by the user.
            artist (str): Artist name provided by the user.
            album (dict): Single album, returned by Spotify search endpoint.
            artist_ids (list): List of artist ids, return by `get_artists_ids()` function.
            music_info (list): List to add music info to, if found.
        """
        # Skip current album if it's name doesn't
        # match with `song` in any way..

        if not is_kinda_same(album["name"], song):
            return

        temp = []
        for x in album["artists"]:
            temp.append(x["name"])

        artists_name = []
        for artists in album["artists"]:
            if (
                not is_kinda_same(artists["name"], artist)
                and artists["id"] not in artist_ids
                and artists["name"] not in temp
                and not artists_name
            ):
                continue

            artists_name.append(artists["name"])

        if artist in artists_name:
            album_url = album["external_urls"]["spotify"]
            album_art = album["images"][0]["url"]
            title = album["name"]
            artists_ = ", ".join(artists_name)
            album_type = album["album_type"]
            album_title = album["name"]

            if album["release_date_precision"] == "day":
                release_date = datetime.strptime(album["release_date"], "%Y-%m-%d").strftime(date_format)
            else:
                release_date = datetime.strptime(album["release_date"], "%Y-%m").strftime(date_format)

            music_info.append(
                {
                    "album_art": album_art,
                    "artists": artists_,
                    "title": title,
                    "album_type": album_type,
                    "album_title": album_title,
                    "url": album_url,
                    "release_date": release_date,
                }
            )


if __name__ == "__main__":

    spotipy = Spotipy(client_id, client_secret)

    artist = input("Artist Name: ")
    song = input("Song Name: ")

    pprint(spotipy.search_music(artist, song))
