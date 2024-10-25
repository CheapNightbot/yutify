import os
import sys
from pprint import pprint

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cheap_utils import cheap_compare


class Deezer:
    def __init__(self) -> None:
        self.music_info = []
        self.api_url = "https://api.deezer.com"

    def search(self, artist: str, song: str) -> dict | None:
        """Search Deezer's music catalogue.

        Args:
            artist (str): Artist(s) name.
            song (str): Song name.

        Returns:
            dict | None: Dictionary containing music info or `None`.
        """
        self.music_info = []

        search_types = ["track", "album"]
        for search_type in search_types:
            if self.music_info:
                return self.music_info[0]

            endpoint = f"{self.api_url}/search/{search_type}"
            query = f'?q=artist:"{artist}" {search_type}:"{song}"&limit=10'
            query_url = endpoint + query

            response = requests.get(query_url)
            if response.status_code != 200:
                return None

            try:
                result = response.json()["data"]
            except IndexError:
                continue

            self._parse_results(artist, song, result)

        if self.music_info:
            return self.music_info[0]
        else:
            return None

    def get_upc_isrc(self, id: int, type: str) -> dict | None:
        """Return ISRC or UPC for a track or album respectively and release date!

        Args:
            id (int): Deezer track or album ID.
            type (str): Whether it's a `track` or an `album`.

        Returns:
            str | None: Return ISRC or UPC if found, otherwise return None.
        """
        match type:
            case "track":
                query_url = f"{self.api_url}/track/{id}"
                response = requests.get(query_url)
                if response.status_code != 200:
                    return None

                result = response.json()
                return {"isrc": result["isrc"], "release_date": result["release_date"]}

        match type:
            case "album":
                query_url = f"{self.api_url}/album/{id}"
                response = requests.get(query_url)

                if response.status_code != 200:
                    return None

                result = response.json()
                return {"upc": result["upc"], "release_date": result["release_date"]}

        match type:
            case _:
                return None

    def _parse_results(self, artist: str, song: str, results: list[dict]) -> None:
        """Helper function to parse results returned by Deezer API.

        Args:
            artist (str): Artist name(s)
            song (str): Song name
            results (list[dict]): Returned by `self.search()`.

        Returns:
            None: Modify instance variable `self.music_info`.
        """
        for result in results:
            if self.music_info:
                return self.music_info[0]

            if not (
                cheap_compare(result["title"], song)
                and cheap_compare(result["artist"]["name"], artist)
            ):
                continue

            match result["type"]:
                case "track":
                    track_info = self.get_upc_isrc(result["id"], result["type"])
                    isrc = track_info["isrc"]
                    release_date = track_info["release_date"]
                    upc = None

                case "album":
                    album_info = self.get_upc_isrc(result["id"], result["type"])
                    upc = album_info["upc"]
                    release_date = album_info["release_date"]
                    isrc = None

            try:
                album_type = (
                    result["type"]
                    if result["title"] == result["album"]["title"]
                    else result["album"]["type"]
                )
            except KeyError:
                album_type = result["record_type"]

            self.music_info.append(
                {
                    "album_art": (
                        result["album"]["cover_xl"]
                        if result["type"] == "track"
                        else result["cover_xl"]
                    ),
                    "album_title": (
                        result["album"]["title"]
                        if result["type"] == "track"
                        else result["title"]
                    ),
                    "album_type": album_type,
                    "artists": result["artist"]["name"],
                    "id": result["id"],
                    "isrc": isrc,
                    "release_date": release_date,
                    "title": result["title"],
                    "type": result["type"],
                    "upc": upc,
                    "url": result["link"],
                }
            )


if __name__ == "__main__":

    deezer = Deezer()

    artist = input("Artist Name: ")
    song = input("Song Name: ")

    pprint(deezer.search(artist, song))
