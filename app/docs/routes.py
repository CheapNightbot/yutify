from datetime import datetime

from flask import render_template, request, url_for

from app.docs import bp


@bp.route("/")
@bp.route("")
def index():
    """Render the API documentation page."""
    base_url = url_for("main.index", _external=True).rstrip("/")
    if "localhost" not in base_url or "127.0.0.1" not in base_url:
        base_url = base_url.replace("http://", "https://")
    return render_template(
        "docs/overview.html",
        title="Overview",
        active_page="docs",
        aside_active="Overview",
        base_url=base_url,
        year=datetime.today().year,
    )


@bp.route("/get-started")
def get_started():
    """Render the "Get Started" page in the API documentation page."""
    base_url = url_for("main.index", _external=True).rstrip("/")
    if "localhost" not in base_url or "127.0.0.1" not in base_url:
        base_url = base_url.replace("http://", "https://")
    return render_template(
        "docs/get_started.html",
        title="Get Started",
        active_page="docs",
        aside_active="Get Started",
        base_url=base_url,
        year=datetime.today().year,
    )


@bp.route("/concepts/<concept>")
@bp.route("/concepts")
def concepts(concept=None):
    """Render the "Concepts" page in the API documentation page."""
    match concept:
        case "apps":
            return render_template(
                "docs/concepts/apps.html",
                title="Concepts - Apps",
                active_page="docs",
                aside_active="Concepts",
                year=datetime.today().year,
            )
        case "tokens":
            return render_template(
                "docs/concepts/tokens.html",
                title="Concepts - Tokens",
                active_page="docs",
                aside_active="Concepts",
                year=datetime.today().year,
            )
        case "activity":
            return render_template(
                "docs/concepts/activity.html",
                title="Concepts - Activity",
                active_page="docs",
                aside_active="Concepts",
                year=datetime.today().year,
            )
        case _:
            # Default case for the main concepts page
            return render_template(
                "docs/concepts.html",
                title="Concepts",
                active_page="docs",
                aside_active="Concepts",
                year=datetime.today().year,
            )


@bp.route("/tutorials/<tutorial>")
@bp.route("/tutorials")
def tutorials(tutorial=None):
    """Render the "Tutorials" page in the API documentation page."""
    base_url = url_for("main.index", _external=True).rstrip("/")
    if "localhost" not in base_url or "127.0.0.1" not in base_url:
        base_url = base_url.replace("http://", "https://")
    match tutorial:
        case "authorization-guide":
            return render_template(
                "docs/tutorials/authorization_guide.html",
                title="Tutorials - Authorization Guide",
                active_page="docs",
                aside_active="Tutorials",
                base_url=base_url,
                year=datetime.today().year,
            )
        case _:
            return render_template(
                "docs/tutorials.html",
                title="Tutorials",
                active_page="docs",
                aside_active="Tutorials",
                year=datetime.today().year,
            )


@bp.route("/references/<reference>")
def references(reference):
    """Render the API reference pages based on the provided reference type."""
    match reference:
        case "activity":
            return render_template(
                "docs/references/activity.html",
                title="API Reference Activity",
                active_page="docs",
                aside_active="Activity",
                year=datetime.today().year,
            )
        case "search":
            return render_template(
                "docs/references/search.html",
                title="API Reference Search",
                active_page="docs",
                aside_active="Search",
                year=datetime.today().year,
            )
        case _:
            # Return a 404 page if the reference is not found
            return render_template("404.html"), 404
