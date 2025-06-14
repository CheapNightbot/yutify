import sqlalchemy as sa
import sqlalchemy.orm as so
from waitress import serve

from app import create_app, create_services, create_users, db
from app.models import Role, Service, User, UserData, UserService, WebAuthn

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


# # https://flask.palletsprojects.com/en/stable/web-security/
@app.after_request
def set_security_headers(response):
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Content-Security-Policy"] = (
        "style-src-elem 'self' https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.indigo.min.css "
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
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    return response


if __name__ == "__main__":
    with app.app_context():
        create_users()
        create_services()

    serve(
        app,
        host="0.0.0.0",
        port=app.config["PORT"],
        threads=6,
        url_scheme="https" if app.config.get("HOST_URL") != "localhost" else "http",
        ident=app.config.get("SERVICE"),
    )
