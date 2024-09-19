import os
import sys
from pprint import pprint

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger


class Deezer:
    def __init__(self) -> None:
        self.music_info = []

    def search_deez_songs(self, artist: str, song: str) -> dict | None:
        """Search Deezer's music catalogue.

        Args:
            artist (str): Artist(s) name.
            song (str): Song name.

        Returns:
            dict | None: If found, return dict containing song info else None.
        """
        self.music_info = []

        search_types = ["track", "album"]

        for search_type in search_types:

            if self.music_info:
                return self.music_info[0]

            url = f"https://api.deezer.com/search/{search_type}"
            query = f"?q=artist:\"{artist}\" {search_type}:\"{song}\"&limit=1"
            query_url = url + query

            logger.info(f"Deezer Search Query: `{query}`")

            response = requests.get(query_url)

            if response.status_code != 200:
                logger.error(f"Deezer returned with status code: {response.status_code}")
                return None

            response_json = response.json()["data"]

            for result in response_json:

                self.music_info.append(
                    {
                        "album_art": result["album"]["cover_xl"] if search_type == "track" else result["cover_xl"],
                        "artists": result["artist"]["name"],
                        "title": result["title"],
                        "album_type": result["type"] if search_type == "track" else result["record_type"],
                        "album_title": result["album"]["title"] if search_type == "track" else result["title"],
                        "url": result["link"],
                    }
                )

        if self.music_info:
            return self.music_info[0]
        else:
            return None


deezer = Deezer()

if __name__ == "__main__":

    artist = input("Artist Name: ")
    song = input("Song Name: ")

    pprint(deezer.search_deez_songs(artist, song))
