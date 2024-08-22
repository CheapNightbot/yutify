from pprint import pprint

from ytmusicapi import YTMusic


def musicyt(artist: str, song: str) -> list[dict] | None:
    """Return list of dictionary containing YouTube Music ID and URL for a song or None.

    Args:
        artist (str): Artist Name of the song
        song (str): Song Name

    Returns:
        list[dict] | None: If successful, list of dictionary containing music ID and URL, else None
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

    # Search query patterns
    patterns = [
        f"{artist} - {song}",
        f"{artist} {song}",
        f"{song} {artist}",
        f'"{artist}" "{song}"',
    ]

    ytmusic = YTMusic()

    for query in patterns:
        # If we couldn't find song with first query pattern,
        # use the second one and so on.. otherwise break
        if music_info:
            break

        search = ytmusic.search(query=query)
        get_music_info(search, music_info, categories_skip)

    if music_info:
        return music_info
    else:
        return None


def get_music_info(search: dict, music_info: list, categories_skip: list):
    for result in search:
        if (
            result["category"].lower() in categories_skip
            or result["title"].lower() != song.lower()
        ):
            continue

        for artists in result["artists"]:
            if artists["name"].lower() != artist.lower():
                continue

            elif result["resultType"] == "song" or result["resultType"] == "video":
                video_id = result["videoId"]
                song_url = f"https://music.youtube.com/watch?v={video_id}"
                music_info.append({"id": video_id, "url": song_url})

            else:
                browse_id = result["browseId"]
                album_url = f"https://music.youtube.com/browse/{browse_id}"
                music_info.append({"id": browse_id, "url": album_url})


if __name__ == "__main__":
    artist = input("Artist Name: ")
    song = input("Song Name: ")
    pprint(musicyt(artist, song))
