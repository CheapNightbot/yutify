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
# @app.after_request
# def set_security_headers(response):
#     response.headers["Strict-Transport-Security"] = "max-age=31536000"
#     response.headers["Content-Security-Policy"] = (
#         "script-src-attr 'none'; "
#         "style-src-attr 'none'; "
#         "style-src-elem 'self' https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.indigo.min.css "
#         "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css "
#         "https://fonts.googleapis.com/; "
#         "font-src 'self' https://fonts.gstatic.com/ https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/; "
#     )
#     response.headers["X-Content-Type-Options"] = "nosniff"
#     response.headers["X-Frame-Options"] = "SAMEORIGIN"

#     return response


if __name__ == "__main__":
    with app.app_context():
        create_users()
        create_services()

    serve(
        app,
        host="0.0.0.0",
        port=app.config["PORT"] or 5000,
        url_scheme="https",
        ident="yutify",
    )
