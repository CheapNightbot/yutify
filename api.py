from flask import Flask, render_template
from flask_restful import Api, Resource, abort

from yutify import musicyt
from yutify.spoti import spotipy

app = Flask(__name__)
api = Api(app)


class Yutify(Resource):
    def get(self, artist, song):
        ytmusic = musicyt.search_musicyt(artist, song)
        spotify = spotipy.search_music(artist, song)

        if not ytmusic and not spotify:
            abort(404, error=f"Couldn't find '{song}' by '{artist}'")

        elif ytmusic and not spotify:
            spotify = spotipy.search_music(ytmusic["artists"], ytmusic["title"])

        result = {
            "album_art": spotify["album_art"] if spotify else ytmusic["album_art"],
            "spotify": spotify["url"] if spotify else None,
            "ytmusic": {
                "id": ytmusic["id"],
                "url": ytmusic["url"],
            },
        }

        return result


api.add_resource(Yutify, "/api/<string:artist>:<string:song>")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
