import base64
import json
import os
import sys
import time
from pprint import pprint

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cheap_utils import cheap_compare, sep_artists

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

date_format = "%Y, %B %d"


class Spotipy:
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.api_url = "https://api.spotify.com/v1"
        self.client_id = client_id
        self.client_secret = client_secret
        self.__header = self.__authenticate()
        self.__start_time = time.time()
        self.music_info = []

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
        return response.json().get("access_token")

    def __refresh_token_if_expired(self):
        """Check if the token is expired and refresh it if necessary."""
        if time.time() - self.__start_time >= 3600:
            self.__header = self.__authenticate()
            self.__start_time = time.time()

    def search(self, artist: str, song: str) -> dict | None:
        """Search for music in Spotify Music.

        Args:
            artist (str): Artist name(s)
            song (str): Song name

        Returns:
            dict | None: Dictionary containing music info or `None`.
        """
        self.__refresh_token_if_expired()
        self.music_info = []

        query_url = f"{self.api_url}/search?q={artist} {song}&type=track,album&limit=10"
        response = requests.get(query_url, headers=self.__header)

        if response.status_code != 200:
            return None

        artist_ids = self.get_artists_ids(artist)
        artist_ids = artist_ids if artist_ids else []

        self.find_music_info(artist, song, response.json(), artist_ids)
        return self.music_info[0] if self.music_info else None

    def search_advanced(
        self, artist: str, song: str, isrc: str = None, upc: str = None
    ) -> dict | None:
        """Search music in Spotify Music using ISRC or UPC.

        Args:
            artist (str): Artist name(s)
            song (str): Song name
            isrc (str, optional): ISRC of a track. Defaults to None.
            upc (str, optional): UPC of an album. Defaults to None.

        Returns:
            dict | None: Dictionary containing music info or `None`.
        """
        self.__refresh_token_if_expired()
        self.music_info = []

        if isrc:
            query = f"?q={artist} {song} isrc:{isrc}&type=track&limit=1"
        elif upc:
            query = f"?q={artist} {song} upc:{upc}&type=album&limit=1"

        query_url = f"{self.api_url}/search{query}"
        response = requests.get(query_url, headers=self.__header)

        if response.status_code != 200:
            return None

        artist_ids = self.get_artists_ids(artist)
        artist_ids = artist_ids if artist_ids else []

        self.find_music_info(artist, song, response.json(), artist_ids)

    def get_artists_ids(self, artist: str) -> list | None:
        """Return a list of artist IDs matching the artist's name."""
        artist_ids = []
        for name in sep_artists(artist):
            query_url = f"{self.api_url}/search?q={name}&type=artist&limit=5"
            response = requests.get(query_url, headers=self.__header)

            if response.status_code != 200:
                return None

            for artist in response.json()["artists"]["items"]:
                artist_ids.append(artist["id"])

        return artist_ids

    def get_tempo(self, spotify_id: str) -> float | None:
        """Return tempo in beats per minute (BPM) of a track."""
        query_url = f"{self.api_url}/audio-features/{spotify_id}"
        response = requests.get(query_url, headers=self.__header)

        if response.status_code != 200:
            return None

        return response.json()["tempo"]

    def find_music_info(
        self, artist: str, song: str, response_json: dict, artist_ids: list
    ) -> None:
        """Helper to extract music info from the search response."""
        # Process tracks
        try:
            for track in response_json["tracks"]["items"]:
                if self.music_info:
                    return
                self.find_tracks(song, artist, track, artist_ids)
        except KeyError:
            pass

        try:
            # Process albums if no track was found
            for album in response_json["albums"]["items"]:
                if self.music_info:
                    return
                self.find_album(song, artist, album, artist_ids)
        except KeyError:
            pass

    def find_tracks(self, song, artist, track, artist_ids) -> None:
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
            release_date = track["album"]["release_date"]
            tempo = round(self.get_tempo(track["id"]))

            self.music_info.append(
                {
                    "album_art": track["album"]["images"][0]["url"],
                    "album_title": track["album"]["name"],
                    "album_type": track["album"]["album_type"],
                    "artists": ", ".join(artists_name),
                    "release_date": release_date,
                    "tempo": tempo,
                    "title": track["name"],
                    "url": track["external_urls"]["spotify"],
                }
            )

    def find_album(self, song, artist, album, artist_ids) -> None:
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
            release_date = album["release_date"]
            self.music_info.append(
                {
                    "album_art": album["images"][0]["url"],
                    "album_title": album["name"],
                    "album_type": album["album_type"],
                    "artists": ", ".join(artists_name),  # Use full artist names
                    "release_date": release_date,
                    "tempo": None,
                    "title": album["name"],
                    "url": album["external_urls"]["spotify"],
                }
            )


if __name__ == "__main__":
    spotipy = Spotipy(client_id, client_secret)

    artist = input("Artist Name: ")
    song = input("Song Name: ")

    pprint(spotipy.search(artist, song))
