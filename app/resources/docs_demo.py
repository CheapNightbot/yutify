"""
API responses to showcase in Documentation. Just to avoid calling real third-party APIs in documentation.
"""

from yutipy.models import MusicInfo, MusicInfos
from config import Config

ALL = MusicInfos(
    album_art="https://" + Config.HOST_URL + "/static/favicon.svg",
    album_art_source="deezer",
    album_title="Song",
    album_type="single",
    artists="Artist",
    genre="Electronic",
    id={
        "deezer": 6663629,
        "itunes": 6663629,
        "kkbox": "Dx6duYxp9UagGhiqwq",
        "spotify": "6rqhFgbbKwnb9MLmUQDhG6",
        "ytmusic": "xD69iRAEiu0",
    },
    isrc="US1234567890",
    lyrics="These are the lyrics of the song...",
    release_date="2025-10-25",
    tempo=None,
    title="Song",
    type="track",
    upc=None,
    url={
        "deezer": "https://www.deezer.com/track/6663629",
        "itunes": "https://music.apple.com/track/6663629",
        "kkbox": "https://www.kkbox.com/tw/tc/song/Dx6duYxp9UagGhiqwq",
        "spotify": "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
        "ytmusic": "https://music.youtube.com/watch?v=xD69iRAEiu0",
    },
)

DEEZER = MusicInfo(
    album_art="https://deezer.com/6663629/album_art.jpg",
    album_title="Song",
    album_type="single",
    artists="Artist",
    genre=None,
    id=6663629,
    isrc="US1234567890",
    lyrics=None,
    release_date="2025-10-25",
    tempo=0,
    title="Song",
    type="track",
    upc=None,
    url="https://www.deezer.com/track/6663629",
)

ITUNES = MusicInfo(
    album_art="https://music.apple.com/6663629/album_art.jpg",
    album_title="Song",
    album_type="single",
    artists="Artist",
    genre="Electronic",
    id=6663629,
    isrc=None,
    lyrics=None,
    release_date="2025-10-25",
    tempo=None,
    title="Song",
    type="track",
    upc=None,
    url="https://music.apple.com/track/6663629",
)

KKBOX = MusicInfo(
    album_art="https://www.kkbox.com/6663629/album_art.jpg",
    album_title="Song",
    album_type="single",
    artists="Artist",
    genre=None,
    id="Dx6duYxp9UagGhiqwq",
    isrc="US1234567890",
    lyrics=None,
    release_date="2025-10-25",
    tempo=None,
    title="Song",
    type="track",
    upc=None,
    url="https://www.kkbox.com/tw/tc/song/Dx6duYxp9UagGhiqwq",
)

SPOTIFY = MusicInfo(
    album_art="https://open.spotify.com/6663629/album_art.jpg",
    album_title="Song",
    album_type="single",
    artists="Artist",
    genre=None,
    id="6rqhFgbbKwnb9MLmUQDhG6",
    isrc="US1234567890",
    lyrics=None,
    release_date="2025-10-25",
    tempo=None,
    title="Song",
    type="track",
    upc=None,
    url="https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
)

YTMUSIC = MusicInfo(
    album_art="https://open.spotify.com/6663629/album_art.jpg",
    album_title=None,
    album_type="single",
    artists="Artist",
    genre=None,
    id="xD69iRAEiu0",
    isrc=None,
    lyrics="These are the lyrics of the song...",
    release_date="2025-10-25",
    tempo=None,
    title="Song",
    type="track",
    upc=None,
    url="https://music.youtube.com/watch?v=xD69iRAEiu0",
)
