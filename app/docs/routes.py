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
    base_url = request.host_url.rstrip("/")  # Remove trailing slash
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
                "docs/concepts_apps.html",
                title="Concepts - Apps",
                active_page="docs",
                aside_active="Concepts",
                year=datetime.today().year,
            )
        case "tokens":
            return render_template(
                "docs/concepts_tokens.html",
                title="Concepts - Tokens",
                active_page="docs",
                aside_active="Concepts",
                year=datetime.today().year,
            )
        case "activity":
            return render_template(
                "docs/concepts_activity.html",
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


@bp.route("/authorization")
def authorization():
    """Render the Authorization Guide page in the API documentation."""
    base_url = request.host_url.rstrip("/")
    return render_template(
        "docs/authorization.html",
        title="Authorization Guide",
        active_page="docs",
        aside_active="Get Started",
        base_url=base_url,
        year=datetime.today().year,
    )


@bp.route("/token-guide")
def token_guide():
    """Render the Token Guide page in the API documentation."""
    base_url = request.host_url.rstrip("/")
    return render_template(
        "docs/token_guide.html",
        title="Token Guide",
        active_page="docs",
        aside_active="Get Started",
        base_url=base_url,
        year=datetime.today().year,
    )
