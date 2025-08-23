import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import redirect, request
from waitress import serve

from app import create_app, create_services, create_users, db
from app.models import Role, Service, User, UserData, UserService, WebAuthn
from app.tasks.activity_updater import start_activity_scheduler

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "sa": sa,
        "so": so,
        "db": db,
        "Role": Role,
        "User": User,
        "Service": Service,
        "UserData": UserData,
        "UserService": UserService,
        "WebAuthn": WebAuthn,
    }


@app.before_request
def redirect_onrender_to_custom_domain():
    """
    Right now my deployment is on Render and I have a custom domain set up.
    But yutify is accessible via the default Render domain as well.
    Unfortunately, Render does not allow disabling the default (.onrender.com) domain
    or redirecting it to a custom domain.
    """
    if request.host == "yutify.onrender.com":
        url = f"https://{app.config.get('HOST_URL')}"
        return redirect(url, code=301)


# https://flask.palletsprojects.com/en/stable/web-security/
@app.after_request
def set_security_headers(response):
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Content-Security-Policy"] = (
        "style-src-elem 'self' 'unsafe-inline' https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.indigo.min.css "
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css "
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/tokyo-night-dark.min.css "
        "https://fonts.googleapis.com/ "
        "https://hcaptcha.com https://*.hcaptcha.com;"
        "font-src 'self' https://fonts.gstatic.com/ https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/; "
        "script-src-elem 'self' https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js "
        "https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.2.5/purify.min.js "
        "https://hcaptcha.com https://*.hcaptcha.com;"
        "frame-src https://hcaptcha.com https://*.hcaptcha.com;"
        "connect-src 'self' https://hcaptcha.com https://*.hcaptcha.com;"
        "frame-ancestors 'self' https://cheapnightbot.me"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    # Allow embedding for the search endpoiont
    if (
        request.path.startswith("/api/search") or request.path.startswith("/api/me")
    ) and "embed" in request.args:
        response.headers.pop("X-Frame-Options", None)

    # Disable caching for user profile page (excluding "Settings page") & activity API endpoints
    is_profile = request.path.startswith("/u/") and "settings" not in request.path
    is_activity = request.path.startswith("/api/me") or request.path.startswith("/api/activity.png")

    if is_profile or is_activity:
        response.headers["Cache-Control"] = "no-store"

    return response


if __name__ == "__main__":
    with app.app_context():
        create_users()
        create_services()
        start_activity_scheduler(app)

    serve(
        app,
        host="0.0.0.0",
        port=app.config["PORT"],
        threads=6,
        url_scheme="https" if app.config.get("HOST_URL") != "localhost" else "http",
        ident=app.config.get("SERVICE"),
    )
