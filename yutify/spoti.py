import base64
import json
import os
import sys
import time
from datetime import datetime
from pprint import pprint

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cheap_utils import cheap_compare, sep_artists
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
        self.__header = self.__authenticate()
        self.__start_time = time.time()

    def __authenticate(self) -> dict:
        """Obtain Spotify access token and headers for requests."""
        token = self.__get_spotify_token()
        headers = {"Authorization": f"Bearer {token}"}
        return headers

    def __get_spotify_token(self) -> str:
        """Request Spotify access token."""
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        response = requests.post(url=url, headers=headers, data=data)
        token = response.json().get("access_token")

        if token:
            logger.info("Spotify access token request successful.")
        else:
            logger.warning("Spotify access token request unsuccessful!")

        return token

    def __refresh_token_if_expired(self):
        """Check if the token is expired and refresh it if necessary."""
        if time.time() - self.__start_time >= 3600:
            logger.info("Refreshing Spotify access token.")
            self.__header = self.__authenticate()
            self.__start_time = time.time()

    def search_music(self, artist: str, song: str) -> dict | None:
        """Search for a track or album by artist and song on Spotify."""
        self.__refresh_token_if_expired()

        query_url = f"{SEARCH_ENDPOINT}?q={artist} {song}&type=track,album&limit=10"
        logger.info(f"Spotify Search Query: `{query_url}`")
        response = requests.get(query_url, headers=self.__header)

        if response.status_code != 200:
            logger.error(f"Spotify returned with status code: {response.status_code}")
            return None

        response_json = response.json()
        artist_ids = self.get_artists_ids(artist)

        # Try finding track and album information
        music_info = self.find_music_info(song, artist, response_json, artist_ids)
        return music_info[0] if music_info else None

    def search_advance(
        self, artist: str, song: str, isrc: str = None, upc: str = None
    ) -> dict | None:
        """Search using ISRC or UPC for advanced search."""
        self.__refresh_token_if_expired()

        if isrc:
            query = f"?q={artist} {song} isrc:{isrc}&type=track&limit=1"
        elif upc:
            query = f"?q={artist} {song} upc:{upc}&type=album&limit=1"

        query_url = SEARCH_ENDPOINT + query
        logger.info(f"Spotify Search Query: `{query_url}`")
        response = requests.get(query_url, headers=self.__header)

        if response.status_code != 200:
            logger.error(f"Spotify returned with status code: {response.status_code}")
            return None

        return self.extract_music_info(response.json(), isrc=bool(isrc))

    def get_artists_ids(self, artist: str) -> list | None:
        """Return a list of artist IDs matching the artist's name."""
        artist_ids = []
        for name in sep_artists(artist):
            query_url = f"{SEARCH_ENDPOINT}?q={name}&type=artist&limit=5"
            logger.info(f"Spotify Search Query: `{query_url}`")
            response = requests.get(query_url, headers=self.__header)

            if response.status_code != 200:
                logger.error(
                    f"Spotify returned with status code: {response.status_code}"
                )
                return None

            for artist in response.json()["artists"]["items"]:
                artist_ids.append(artist["id"])

        return artist_ids

    def find_music_info(
        self, song: str, artist: str, response_json: dict, artist_ids: list
    ) -> list:
        """Helper to extract music info from the search response."""
        music_info = []

        # Process tracks
        for track in response_json["tracks"]["items"]:
            if music_info:
                return music_info
            self.find_tracks(song, artist, track, artist_ids, music_info)

        # Process albums if no track was found
        for album in response_json["albums"]["items"]:
            if music_info:
                return music_info
            self.find_album(song, artist, album, artist_ids, music_info)

        return music_info

    def find_tracks(self, song, artist, track, artist_ids, music_info) -> None:
        """Helper function to find track info and add to music_info."""
        if not cheap_compare(track["name"], song):
            return

        # Extract all artist names from the track
        artists_name = [x["name"] for x in track["artists"]]

        # Filter to match either artist name or artist ID
        matching_artists = [
            x["name"]
            for x in track["artists"]
            if cheap_compare(x["name"], artist) or x["id"] in artist_ids
        ]

        if matching_artists:
            release_date = self.format_release_date(
                track["album"]["release_date"], track["album"]["release_date_precision"]
            )
            music_info.append(
                {
                    "album_art": track["album"]["images"][0]["url"],
                    "artists": ", ".join(artists_name),  # Use full artist names
                    "title": track["name"],
                    "album_type": track["album"]["album_type"],
                    "album_title": track["album"]["name"],
                    "url": track["external_urls"]["spotify"],
                    "release_date": release_date,
                }
            )

    def find_album(self, song, artist, album, artist_ids, music_info) -> None:
        """Helper function to find album info and add to music_info."""
        if not cheap_compare(album["name"], song):
            return

        # Extract all artist names from the album
        artists_name = [x["name"] for x in album["artists"]]

        # Filter to match either artist name or artist ID
        matching_artists = [
            x["name"]
            for x in album["artists"]
            if cheap_compare(x["name"], artist) or x["id"] in artist_ids
        ]

        if matching_artists:
            release_date = self.format_release_date(
                album["release_date"], album["release_date_precision"]
            )
            music_info.append(
                {
                    "album_art": album["images"][0]["url"],
                    "artists": ", ".join(artists_name),  # Use full artist names
                    "title": album["name"],
                    "album_type": album["album_type"],
                    "album_title": album["name"],
                    "url": album["external_urls"]["spotify"],
                    "release_date": release_date,
                }
            )

    def extract_music_info(
        self, response_json: dict, isrc: bool = False
    ) -> dict | None:
        """Extracts music info from advanced search results."""
        try:
            result = (
                response_json["tracks"]["items"][0]
                if isrc
                else response_json["albums"]["items"][0]
            )
        except IndexError:
            logger.warning("Spotify returned empty result!")
            return None

        artists = ", ".join(artist["name"] for artist in result["artists"])
        try:
            release_date = self.format_release_date(
                result["release_date"], result["release_date_precision"]
            )
        except KeyError:
            release_date = self.format_release_date(
                result["album"]["release_date"],
                result["album"]["release_date_precision"],
            )

        return {
            "album_art": result["album"]["images"][0]["url"],
            "artists": artists,
            "title": result["name"],
            "album_type": result.get("album", {}).get("type", result["type"]),
            "album_title": result.get("album", {}).get("name", result["name"]),
            "release_date": release_date,
            "url": result["external_urls"]["spotify"],
        }

    def format_release_date(self, date_str: str, precision: str) -> str:
        """Helper function to format the release date."""
        if precision == "day":
            return datetime.strptime(date_str, "%Y-%m-%d").strftime(date_format)
        return datetime.strptime(date_str, "%Y-%m").strftime(date_format)


if __name__ == "__main__":
    spotipy = Spotipy(client_id, client_secret)

    artist = input("Artist Name: ")
    song = input("Song Name: ")

    pprint(spotipy.search_music(artist, song))
