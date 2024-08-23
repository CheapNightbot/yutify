from flask import Flask, abort, render_template

from yutify import musicyt, spoti

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/<artist>:<song>")
def get_musicyt(artist, song):
    ytmusic = musicyt.musicyt(artist, song)
    spotify = spoti.spotipy(artist, song)

    if not ytmusic and not spotify:
        abort(404)

    elif ytmusic and not spotify:
        spotify = spoti.spotipy(ytmusic["artists"], ytmusic["title"])

    result = {
        "album_art": spotify["album_art"] if spotify else ytmusic["album_art"],
        "spotify": spotify["url"] if spotify else None,
        "ytmusic": {
            "id": ytmusic["id"],
            "url": ytmusic["url"],
        },
    }

    return result
