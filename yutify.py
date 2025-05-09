import unicodedata

import sqlalchemy as sa
import sqlalchemy.orm as so
from celery import Celery
from flask_mailman import EmailMultiAlternatives
from flask_security import MailUtil, Security, SQLAlchemyUserDatastore, UsernameUtil
from flask_security.utils import config_value as cv
from flask_security.utils import get_message
from waitress import serve

from app import create_app, create_users, db, mail
from app.auth.forms import RegistrationForm
from app.models import Role, Service, User, UserData, UserService, WebAuthn

app = create_app()
celery = Celery()


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


@celery.task
def send_flask_mail(**kwargs):
    with app.app_context():
        with mail.get_connection() as connection:
            html = kwargs.pop("html", None)
            msg = EmailMultiAlternatives(**kwargs, connection=connection)
            if html:
                msg.attach_alternative(html, "text/html")
            msg.send()


class MyMailUtil(MailUtil):
    def __init__(self, app):
        super().__init__(app)

    def send_mail(self, template, subject, recipient, sender, body, html, **kwargs):
        send_flask_mail.delay(
            subject=subject,
            from_email=sender,
            to=[recipient],
            body=body,
            html=html,
        )


class MyUsernameUtil(UsernameUtil):
    def __init__(self, app):
        super().__init__(app)

    def check_username(self, username: str) -> str | None:
        """
        Given a username - check for allowable character categories.

        Allow letters, numbers, hyphens and underscores (using unicodedata.category).

        Returns None if allowed, error message if not allowed.
        """
        cats = [
            (
                unicodedata.category(c)
                if unicodedata.category(c).startswith("P")
                else unicodedata.category(c)[0]
            )
            for c in username
        ]
        if any([cat not in ["L", "N", "Pd", "Pc"] for cat in cats]):
            return get_message("USERNAME_DISALLOWED_CHARACTERS")[0]
        return None

    def normalize(self, username: str) -> str:
        """
        Given an input username - return a clean (using bleach) and normalized
        (using Python's unicodedata.normalize()) version.
        Must be called in app context and uses
        :py:data:`SECURITY_USERNAME_NORMALIZE_FORM` config variable.
        """
        import bleach

        if not username:
            return ""

        username = bleach.clean(username.strip(), strip=True)
        if not username:
            return ""
        cf = cv("USERNAME_NORMALIZE_FORM")
        if cf:
            return unicodedata.normalize(cf, username.lower())
        return username.lower()

user_datastore = SQLAlchemyUserDatastore(db, User, Role, WebAuthn)
app.security = Security(
    app,
    user_datastore,
    mail_util_cls=MyMailUtil,
    username_util_cls=MyUsernameUtil,
    register_form=RegistrationForm,
)

if __name__ == "__main__":
    with app.app_context():
        create_users()

    serve(
        app,
        host="0.0.0.0",
        port=app.config["PORT"] or 5000,
        url_scheme="https",
        ident="yutify",
    )
