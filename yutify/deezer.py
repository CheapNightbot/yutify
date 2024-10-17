import os
import sys
from pprint import pprint
from datetime import datetime

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cheap_utils import cheap_compare
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
            query = f"?q=artist:\"{artist}\" {search_type}:\"{song}\"&limit=10"
            query_url = url + query

            logger.info(f"Deezer Search Query: `{query}`")

            response = requests.get(query_url)

            if response.status_code != 200:
                logger.error(f"Deezer returned with status code: {response.status_code}")
                return None

            try:
                result = response.json()["data"]
            except IndexError:
                logger.error(f"No result found in Deezer for search type: {search_type}.")
                continue

            self.parse_deez_results(artist, song, result)

        if self.music_info:
            return self.music_info[0]
        else:
            return None


    def parse_deez_results(self, artist: str, song: str, results: list[dict]):
        for result in results:
            if self.music_info:
                return self.music_info[0]

            if not (cheap_compare(result["title"], song) and cheap_compare(result["artist"]["name"], artist)):
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

            iso_date = release_date
            release_date = datetime.strptime(release_date, "%Y-%m-%d").strftime("%Y, %B %d")

            try:
                album_type = result["type"] if result["title"] == result["album"]["title"] else result["album"]["type"]
            except KeyError:
                album_type = result["record_type"]

            self.music_info.append(
                {
                    "album_art": result["album"]["cover_xl"] if result["type"] == "track" else result["cover_xl"],
                    "album_title": result["album"]["title"] if result["type"] == "track" else result["title"],
                    "album_type": album_type,
                    "artists": result["artist"]["name"],
                    "id": result["id"],
                    "isrc": isrc,
                    "release_date": [release_date, {"iso_format": iso_date}],
                    "title": result["title"],
                    "type": result["type"],
                    "upc": upc,
                    "url": result["link"],
                }
            )


    def get_upc_isrc(self, id: int, type: str) -> dict | None:
        """Return ISRC or UPC for a track or album respectively. Also date!

        Args:
            id (int): Deezer track or album ID.
            type (str): Whether it's a `track` or an `album`.

        Returns:
            str | None: Return ISRC or UPC if found, otherwise return None.
        """
        url = "https://api.deezer.com/"

        match type:
            case "track":
                query_url = url + f"track/{id}"
                logger.info("Get ISRC from Deezer.")

                response = requests.get(query_url)

                if response.status_code != 200:
                    logger.error(f"Failed to get ISRC. Deezer retuned with status code: {response.status_code}")
                    return None

                result = response.json()
                return {"isrc": result["isrc"], "release_date": result["release_date"]}

        match type:
            case "album":
                query_url = url + f"album/{id}"
                logger.info("Get UPC from Deezer.")

                response = requests.get(query_url)

                if response.status_code != 200:
                    logger.error(f"Failed to get UPC. Deezer retuned with status code: {response.status_code}")
                    return None

                result = response.json()
                return {"upc": result["upc"], "release_date": result["release_date"]}

        match type:
            case _:
                return None


if __name__ == "__main__":

    deezer = Deezer()

    artist = input("Artist Name: ")
    song = input("Song Name: ")

    pprint(deezer.search_deez_songs(artist, song))
