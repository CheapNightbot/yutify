import os
import sys
from pprint import pprint
from datetime import datetime

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import logger
from utils.cheap_utils import cheap_compare


class Itunes:
    def __init__(self) -> None:
        self.music_info = []
        self.endpoint = "https://itunes.apple.com/search"

    def search_itunes(self, artist: str, song: str) -> dict | None:
        """Search for music in iTunes Store

        Args:
            artist (str): Artist(s) Name
            song (str): Song Name

        Returns:
            dict | None: If found, return dict containing song info else None.
        """
        self.music_info = []

        entities = ["song", "album"]
        for entity in entities:
            if self.music_info:
                return self.music_info[0]

            query = f"?term={artist} - {song}&media=music&entity={entity}&limit=1"
            query_url = self.endpoint + query

            logger.info(f"iTunes Search Query: `{query}")

            response = requests.get(query_url)

            if response.status_code != 200:
                logger.error(f"iTunes returned with status code: {response.status_code}")
                return None

            try:
                result = response.json()["results"][0]
            except IndexError:
                logger.error("iTunes returned with empty result.")
                return None
            release_date = datetime.strptime(result["releaseDate"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y, %B %d")

            match entity:
                case "song":
                    if not cheap_compare(result["trackName"], song):
                        logger.error(f"No result found in iTunes for search type: {entity}.")
                        continue

            try:
                album_title, album_type = result["collectionName"].split("-")
                album_title = album_title.strip()
                album_type = album_type.strip().lower()
            except ValueError:
                album_title = result["collectionName"]
                album_type = result.get("collectionType", result["wrapperType"]).lower()

            self.music_info.append(
                {
                    "album_art": result["artworkUrl100"],
                    "album_title": album_title,
                    "album_type": album_type,
                    "artists": result["artistName"],
                    "genre": result["primaryGenreName"],
                    "release_date": release_date,
                    "title": result.get("trackName", result["collectionName"]),
                    "type": result["wrapperType"],
                    "url": result.get("trackViewUrl", result["collectionViewUrl"]),
                }
            )

        if self.music_info:
            return self.music_info[0]
        else:
            return None


if __name__ == "__main__":

    itunes = Itunes()

    artist = input("Artist Name: ")
    song = input("Song Name: ")

    pprint(itunes.search_itunes(artist, song))
