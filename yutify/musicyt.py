import os
from pprint import pprint

from yutify.cheap_utils import is_kinda_same
from dotenv import load_dotenv
from ytmusicapi import YTMusic

load_dotenv()

b_id = os.getenv("B_ID")


class MusicYT:

    def __init__(self) -> None:
        self.music_info = []
        self.ytmusic = YTMusic("oauth.json", b_id)

    def search_musicyt(self, artist: str, song: str) -> dict | None:
        """Return a dictionary containing YouTube Music ID and URL for a song or None.

        Args:
            artist (str): Artist Name of the song
            song (str): Song Name

        Returns:
            dict | None: If successful, a dictionary containing music ID and URL, else None
        """
        self.music_info = []

        query = f"{artist} - {song}"
        search = self.ytmusic.search(query=query)

        for result in search:
            if self.music_info:
                return self.music_info[0]

            elif self.skip_categories(result):
                continue

            elif not is_kinda_same(result["title"], song):
                continue

            for artists in result["artists"]:
                if not is_kinda_same(artists["name"], artist):
                    continue

                elif result["resultType"] == "song" or result["resultType"] == "video":
                    self.get_song(result)

                else:
                    self.get_album(result)

        if self.music_info:
            return self.music_info[0]
        else:
            return None

    def skip_categories(self, result: dict):
        """Skip these search categories in search results.
        In other words, only include "songs, videos, albums, playlists".

        Args:
            result (dict): Returned by `ytmusic.search()` method

        Returns:
            bool: Return `True` if `result` has following categories, else `False`
        """
        categories_skip = [
            "artists",
            "community playlists",
            "featured playlists",
            "podcasts",
            "profiles",
            "uploads",
            "episode",
            "episodes",
        ]

        if (
            result["category"].lower() in categories_skip
            or result["resultType"].lower() in categories_skip
        ):
            return True

        else:
            return False

    def get_song(self, result: dict):
        """Helper function to add song info to the `music_info` list.

        Args:
            result (dict): Returned by `musicyt.search()`.
        """
        title = result["title"]
        artist_name = " ".join([artists["name"] for artists in result["artists"]])
        video_id = result["videoId"]
        song_url = f"https://music.youtube.com/watch?v={video_id}"
        try:
            album_art = result["thumbnails"][-1]["url"]
        except KeyError:
            song_result = self.ytmusic.get_song(video_id)
            album_art = song_result["videoDetails"]["thumbnail"]["thumbnails"][-1][
                "url"
            ]
        self.music_info.append(
            {
                "artists": artist_name,
                "album_art": album_art,
                "album_type": "single",
                "album_title": None,
                "id": video_id,
                "title": title,
                "url": song_url,
            }
        )

    def get_album(self, result: dict):
        """Helper function to add album info to the `music_info` list.

        Args:
            result (dict): Returned by the `musicyt.search()`.
        """
        title = result["title"]
        artist_name = " ".join([artists["name"] for artists in result["artists"]])
        browse_id = result["browseId"]
        album_url = f"https://music.youtube.com/browse/{browse_id}"
        try:
            album_art = result["thumbnails"][-1]["url"]
            album_title = result["title"]
        except KeyError:
            album_result = self.ytmusic.get_album(browse_id)
            album_art = album_result["thumbnails"][-1]["url"]
            album_title = album_result["title"]
        self.music_info.append(
            {
                "artists": artist_name,
                "album_art": album_art,
                "album_type": "Album",
                "album_title": album_title,
                "id": browse_id,
                "title": title,
                "url": album_url,
            }
        )


music_yt = MusicYT()


if __name__ == "__main__":

    artist = input("Artist Name: ")
    song = input("Song Name: ")
    pprint(music_yt.search_musicyt(artist, song))
