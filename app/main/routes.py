from datetime import datetime, timezone

import requests
from flask import render_template, request
from flask_login import current_user

from app import db
from app.main import bp
from app.main.forms import SearchForm


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
        artist = form.artist.data
        song = form.song.data

        # Dynamically determine the base URL for the /api/search endpoint
        base_url = request.host_url.rstrip("/")  # Remove trailing slash
        search_url = f"{base_url}/api/search/{artist}:{song}"

        # Call the /api/search endpoint using requests
        response = requests.get(search_url, params={"all": ""})
        result = response.json()

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


@bp.route("/privacy-policy")
def privacy_policy():
    """Render the privacy policy page."""
    return render_template(
        "privacy_policy.html",
        title="Privacy Policy",
        active_page="privacy_policy",
        year=datetime.today().year,
    )

@bp.route("/terms-of-service")
def terms_of_service():
    """Render the terms of service page."""
    return render_template(
        "terms_of_service.html",
        title="Terms of Service",
        active_page="terms_of_service",
        year=datetime.today().year,
    )
