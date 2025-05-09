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
        title="Docs - Overview",
        active_page="docs",
        aside_active="overview",
        base_url=base_url,
        year=datetime.today().year,
    )


@bp.route("/get-started")
def get_started():
    """Render the "Get Started" page in the API documentation page."""
    return render_template(
        "docs/get_started.html",
        title="Docs - Get Started",
        active_page="docs",
        aside_active="get-started",
        year=datetime.today().year,
    )


@bp.route("/tutorials")
def tutorials():
    """Render the "Tutorials" page in the API documentation page."""
    return render_template(
        "docs/tutorials.html",
        title="Docs - Tutorials",
        active_page="docs",
        aside_active="tutorials",
        year=datetime.today().year,
    )


@bp.route("/reference/search")
def reference_search():
    """Render the "Search" page in the API documentation page."""
    return render_template(
        "docs/reference_search.html",
        title="Docs - API Reference Search",
        active_page="docs",
        aside_active="search",
        year=datetime.today().year,
    )


@bp.route("/reference/activity")
def reference_activity():
    """Render the "Activity" page in the API documentation page."""
    return render_template(
        "docs/reference_activity.html",
        title="Docs - API Reference Activity",
        active_page="docs",
        aside_active="activity",
        year=datetime.today().year,
    )
