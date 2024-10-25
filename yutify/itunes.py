import os
import sys
from pprint import pprint
from datetime import datetime

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cheap_utils import cheap_compare


class Itunes:
    def __init__(self) -> None:
        self.music_info = []
        self.api_url = "https://itunes.apple.com"

    def search(self, artist: str, song: str) -> dict | None:
        """Search for music in iTunes Store.

        Args:
            artist (str): Artist(s) Name
            song (str): Song Name

        Returns:
            dict | None: Dictionary contiaing music info or `None`.
        """
        self.music_info = []

        entities = ["song", "album"]
        for entity in entities:
            if self.music_info:
                return self.music_info[0]

            endpoint = f"{self.api_url}/search"
            query = f"?term={artist} - {song}&media=music&entity={entity}&limit=10"
            query_url = endpoint + query

            response = requests.get(query_url)
            if response.status_code != 200:
                return None

            try:
                result = response.json()["results"]
            except IndexError:
                return None

            self._parse_result(artist, song, result)

        if self.music_info:
            return self.music_info[0]
        else:
            return None

    def _parse_result(self, artist: str, song: str, results: list[dict]) -> None:
        """Helper function to parse results return by iTunes API.

        Args:
            artist (str): Artist name(s)
            song (str): Song name
            results (list[dict]): Retruned by `self.search()`

        Returns:
            None: Modify instance variable `self.music_info`.
        """
        for result in results:
            if self.music_info:
                return

            if not (
                cheap_compare(result.get("trackName", result["collectionName"]), song)
                and cheap_compare(result["artistName"], artist)
            ):
                continue

            try:
                album_title, album_type = result["collectionName"].split("-")
                album_title = album_title.strip()
                album_type = album_type.strip().lower()
            except ValueError:
                album_title = result["collectionName"]
                album_type = (
                    result["wrapperType"]
                    if result.get("trackName", "") == result["collectionName"]
                    else result.get("kind", result.get("collectionType", ""))
                )

            release_date = datetime.strptime(
                result["releaseDate"], "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%Y-%m-%d")

            self.music_info.append(
                {
                    "album_art": result["artworkUrl100"],
                    "album_title": album_title,
                    "album_type": album_type.lower(),
                    "artists": result["artistName"],
                    "genre": result["primaryGenreName"],
                    "release_date": release_date,
                    "title": result.get("trackName", album_title),
                    "type": result["wrapperType"],
                    "url": result.get("trackViewUrl", result["collectionViewUrl"]),
                }
            )


if __name__ == "__main__":

    itunes = Itunes()

    artist = input("Artist Name: ")
    song = input("Song Name: ")

    pprint(itunes.search(artist, song))
