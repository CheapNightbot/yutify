import os
import sys
from datetime import datetime
from pprint import pprint

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ytmusicapi import YTMusic, exceptions
from utils.cheap_utils import cheap_compare


class MusicYT:
    def __init__(self) -> None:
        self.music_info = []
        self.ytmusic = YTMusic()

    def search(self, artist: str, song: str) -> dict | None:
        """Search for music YouTube Music.

        Args:
            artist (str): Artist Name(s)
            song (str): Song Name

        Returns:
            dict | None: Dictionary containing music info or `None`.
        """
        self.music_info = []
        query = f"{artist} - {song}"

        try:
            results = self.ytmusic.search(query=query)
        except exceptions.YTMusicServerError:
            return None

        for result in results:
            if self._is_relevent_result(artist, song, result):
                self._process_result(result)
                return self.music_info[0] if self.music_info else None

        return None

    def _is_relevent_result(self, artist: str, song: str, result: dict) -> bool:
        """Helper function to determine if a search result is relevent.

        Args:
            artist (str): Artist name(s)
            song (str): Song name
            results (dict): Retruned by `self.search()`

        Returns:
            bool: Whether any result is relevent.
        """
        if self._skip_categories(result):
            return False

        return any(
            cheap_compare(result.get("title"), song)
            and cheap_compare(_artist.get("name"), artist)
            for _artist in result.get("artists", [])
        )

    def _skip_categories(self, result: dict):
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
            result.get("category", "").lower() in categories_skip
            or result.get("resultType", "").lower() in categories_skip
        ):
            return True

        else:
            return False

    def _get_song(self, result: dict) -> None:
        """Helper function to add song info to the `music_info` list."""
        title = result["title"]
        artist_names = ", ".join([artists["name"] for artists in result["artists"]])
        video_id = result["videoId"]
        song_url = f"https://music.youtube.com/watch?v={video_id}"
        lyrics_id = self.ytmusic.get_watch_playlist(video_id)

        try:
            song_data = self.ytmusic.get_song(video_id)
        except (exceptions.YTMusicServerError, exceptions.YTMusicError):
            song_data = {}
        else:
            song_data = song_data if song_data else {}
            release_date = (
                song_data.get("microformat", {})
                .get("microformatDataRenderer", {})
                .get("uploadDate")
            )
            # Get the index of "T" and slice the string after that or only get string before "T".
            # For example, "2016-10-18T11:00:03-07:00" will become "2016-10-18"
            release_date = release_date[: release_date.index("T")] if release_date else None

        try:
            lyrics = self.ytmusic.get_lyrics(lyrics_id.get("lyrics"))
        except exceptions.YTMusicUserError:
            lyrics = {}

        try:
            album_art = result["thumbnails"][-1]["url"]
        except KeyError:
            album_art = (
                song_data.get("videoDetails", {})
                .get("thumbnail", {})
                .get("thumbnails", {"x", "y"})[-1]
                .get("url")
            )
        self.music_info.append(
            {
                "album_art": album_art,
                "album_title": None,
                "album_type": "single",
                "artists": artist_names,
                "genre": None,
                "id": video_id,
                "isrc": None,
                "lyrics": lyrics.get("lyrics"),
                "release_date": release_date,
                "tempo": None,
                "title": title,
                "upc": None,
                "url": song_url,
            }
        )

    def _get_album(self, result: dict) -> None:
        """Helper function to add album info to the `music_info` list."""
        title = result["title"]
        artist_names = ", ".join([artists["name"] for artists in result["artists"]])
        browse_id = result["browseId"]
        album_url = f"https://music.youtube.com/browse/{browse_id}"

        album_data = self.ytmusic.get_album(browse_id)
        release_date = album_data["year"]

        try:
            lyrics_id = self.ytmusic.get_watch_playlist(browse_id)
        except exceptions.YTMusicServerError:
            lyrics_id = {}
        try:
            if not lyrics_id:
                raise exceptions.YTMusicUserError
            lyrics = self.ytmusic.get_lyrics(lyrics_id.get("lyrics"))
        except exceptions.YTMusicUserError:
            lyrics = {}
        try:
            album_art = result["thumbnails"][-1]["url"]
            album_title = result["title"]
        except KeyError:
            album_art = album_data["thumbnails"][-1]["url"]
            album_title = album_data["title"]
        self.music_info.append(
            {
                "album_art": album_art,
                "album_title": album_title,
                "album_type": "Album",
                "artists": artist_names,
                "genre": None,
                "id": browse_id,
                "isrc": None,
                "lyrics": lyrics.get("lyrics"),
                "release_date": release_date,
                "tempo": None,
                "title": title,
                "upc": None,
                "url": album_url,
            }
        )

    def _process_result(self, result: dict) -> None:
        """Helper function to process results return my YTMusic."""
        if result["resultType"] in ["song", "video"]:
            self._get_song(result)

        else:
            self._get_album(result)


if __name__ == "__main__":
    music_yt = MusicYT()

    artist_name = input("Artist Name: ")
    song_name = input("Song Name: ")
    pprint(music_yt.search(artist_name, song_name))
