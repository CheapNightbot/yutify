from datetime import datetime, timezone

from flask import render_template
from flask_login import current_user

from app import db
from app.main import bp
from app.main.forms import SearchForm
from app.resources.search import YutifySearch


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route("/", methods=["GET", "POST"])
def index():
    """Render the index/home page."""
    form = SearchForm()

    if form.validate_on_submit():
        # Create an instance of the Search resource
        search_resource = YutifySearch()
        artist = form.artist.data
        song = form.song.data

        # Call the get method directly with the artist and song parameters
        response = search_resource.get(artist, song)
        result = response.get_json()

        if result.get("error"):
            return render_template(
                "index.html",
                title="Home",
                active_page="home",
                artist=artist,
                song=song,
                album_art="static/favicon.svg",
                title_=result.get("error"),
                year=datetime.today().year,
                form=form,
            )

        return render_template(
            "index.html",
            title="Home",
            active_page="home",
            album_art=result.get("album_art"),
            album_title=result.get("album_title"),
            album_type=result.get("album_type"),
            artist=artist,
            artists=result.get("artists"),
            deezer=result.get("url").get("deezer"),
            genre=result.get("genre"),
            itunes=result.get("url").get("itunes"),
            kkbox=result.get("url").get("kkbox"),
            lyrics=(
                result.get("lyrics").replace("\r", "").replace("\n", "<br>")
                if result.get("lyrics")
                else None
            ),
            song=song,
            spotify=result.get("url").get("spotify"),
            title_=result.get("title"),
            yt_music=result.get("url").get("ytmusic"),
            year=datetime.today().year,
            form=form,
        )

    return render_template(
        "index.html",
        title="Home",
        active_page="home",
        year=datetime.today().year,
        form=form,
    )


@bp.route("/docs")
def docs():
    """Render the API documentation page."""
    return render_template(
        "docs.html", title="Docs", active_page="docs", year=datetime.today().year
    )
