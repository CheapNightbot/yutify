import os
from pprint import pprint

from dotenv import load_dotenv
from ytmusicapi import YTMusic

load_dotenv()

b_id = os.getenv("B_ID")


def search_musicyt(artist: str, song: str) -> dict | None:
    """Return a dictionary containing YouTube Music ID and URL for a song or None.

    Args:
        artist (str): Artist Name of the song
        song (str): Song Name

    Returns:
        dict | None: If successful, a dictionary containing music ID and URL, else None
    """
    music_info = []

    # Skip these search categories in search results.
    # In other words, only include "songs, videos, albums, playlists"
    categories_skip = [
        "artists",
        "community playlists",
        "featured playlists",
        "podcasts",
        "profiles",
        "uploads",
    ]

    ytmusic = YTMusic("oauth.json", b_id)

    query = f"{artist} - {song}"
    search = ytmusic.search(query=query)

    for result in search:
        if music_info:
            return music_info[0]

        elif result["category"].lower() in categories_skip:
            continue

        elif (
            result["title"].lower() != song.lower()
            and result["title"].lower() not in song.lower()
            and song.lower() not in result["title"].lower()
        ):
            continue

        for artists in result["artists"]:
            if (
                artists["name"].lower() != artist.lower()
                and artists["name"].lower() not in artist.lower()
                and artist.lower() not in artists["name"].lower()
            ):
                continue

            elif result["resultType"] == "song" or result["resultType"] == "video":
                title = result["title"]
                artist_name = " ".join(
                    [artists["name"] for artists in result["artists"]]
                )
                video_id = result["videoId"]
                song_url = f"https://music.youtube.com/watch?v={video_id}"
                song_result = ytmusic.get_song(video_id)
                try:
                    album_art = song_result["videoDetails"]["thumbnail"]["thumbnails"][-1]["url"]
                except KeyError:
                    album_art = None
                music_info.append(
                    {
                        "artists": artist_name,
                        "album_art": album_art,
                        "id": video_id,
                        "title": title,
                        "url": song_url,
                    }
                )

            else:
                title = result["title"]
                artist_name = " ".join(
                    [artists["name"] for artists in result["artists"]]
                )
                browse_id = result["browseId"]
                album_url = f"https://music.youtube.com/browse/{browse_id}"
                album_result = ytmusic.get_album(browse_id)
                try:
                    album_art = album_result["thumbnails"][-1]["url"]
                except KeyError:
                    album_art = None
                music_info.append(
                    {
                        "artists": artist_name,
                        "album_art": album_art,
                        "id": browse_id,
                        "title": title,
                        "url": album_url,
                    }
                )

    if music_info:
        return music_info[0]
    else:
        return None


if __name__ == "__main__":

    artist = input("Artist Name: ")
    song = input("Song Name: ")
    pprint(search_musicyt(artist, song))
