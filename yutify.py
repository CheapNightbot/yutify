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


# Content Security Policy (CSP)
# https://flask.palletsprojects.com/en/stable/web-security/#content-security-policy-csp
@app.after_request
def set_csp_header(response):
    response.headers["Content-Security-Policy"] = (
        "script-src-attr 'none'; "
        "style-src-attr 'none'; "
        "style-src-elem 'self' https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.indigo.min.css "
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css "
        "https://fonts.googleapis.com/; "
        "font-src 'self' https://fonts.gstatic.com/ https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/webfonts/; "
    )
    return response


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=app.config["PORT"] or 5000)
