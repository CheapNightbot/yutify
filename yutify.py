import sqlalchemy as sa
import sqlalchemy.orm as so
from waitress import serve

from app import create_app, db
from app.models import Service, User, UserData, UserService

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "sa": sa,
        "so": so,
        "db": db,
        "User": User,
        "Service": Service,
        "UserData": UserData,
        "UserService": UserService,
    }


# https://flask.palletsprojects.com/en/stable/web-security/
@app.after_request
def set_security_headers(response):
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Content-Security-Policy"] = (
        "script-src-attr 'none'; "
        "style-src-attr 'none'; "
        "style-src-elem 'self' https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.indigo.min.css "
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css "
        "https://fonts.googleapis.com/; "
        "font-src 'self' https://fonts.gstatic.com/ https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/; "
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    return response


app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

if __name__ == "__main__":
    serve(
        app,
        host="0.0.0.0",
        port=app.config["PORT"] or 5000,
        url_scheme="https",
        ident="yutify",
    )
