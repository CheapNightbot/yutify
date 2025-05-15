from datetime import datetime

from flask import render_template, request

from app.docs import bp


@bp.route("/")
@bp.route("")
def index():
    """Render the API documentation page."""
    base_url = request.host_url.rstrip("/")  # Remove trailing slash
    return render_template(
        "docs/index.html",
        title="Overview",
        active_page="docs",
        aside_active="Overview",
        base_url=base_url,
        year=datetime.today().year,
    )


@bp.route("/get-started")
def get_started():
    """Render the "Get Started" page in the API documentation page."""
    return render_template(
        "docs/get_started.html",
        title="Get Started",
        active_page="docs",
        aside_active="Get Started",
        year=datetime.today().year,
    )


@bp.route("/tutorials")
def tutorials():
    """Render the "Tutorials" page in the API documentation page."""
    return render_template(
        "docs/tutorials.html",
        title="Tutorials",
        active_page="docs",
        aside_active="Tutorials",
        year=datetime.today().year,
    )


@bp.route("/reference/search")
def reference_search():
    """Render the "Search" page in the API documentation page."""
    return render_template(
        "docs/reference_search.html",
        title="API Reference Search",
        active_page="docs",
        aside_active="Search",
        year=datetime.today().year,
    )


@bp.route("/reference/activity")
def reference_activity():
    """Render the "Activity" page in the API documentation page."""
    return render_template(
        "docs/reference_activity.html",
        title="API Reference Activity",
        active_page="docs",
        aside_active="Activity",
        year=datetime.today().year,
    )
