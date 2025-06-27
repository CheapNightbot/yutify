from datetime import datetime

import requests
from flask import render_template, url_for

from app.main import bp
from app.main.forms import SearchForm


@bp.route("/", methods=["GET", "POST"])
def index():
    """Render the index/home page."""
    form = SearchForm()

    if form.validate_on_submit():
        artist = form.artist.data
        song = form.song.data

        # Dynamically determine the base URL for the /api/search endpoint
        base_url = url_for("main.index", _external=True).rstrip("/")
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


@bp.route("/faq")
def faq():
    """Render the FAQ page."""
    return render_template(
        "faq.html",
        title="FAQ",
        active_page="faq",
        year=datetime.today().year,
    )
