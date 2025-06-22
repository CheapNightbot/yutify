from flask import Flask, flash, redirect, url_for, abort
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    current_user,
    url_for_security,
)
from flask_security.signals import (
    user_authenticated,
    user_confirmed,
    user_registered,
    tf_profile_changed,
    tf_disabled,
)

from app.auth import bp
from app.models import User


def post_user_registration(app: Flask, user: User, **extra_args):
    """
    Function to call on/after `user_registered` signal emitted by Flask-Security.

    This handles (for now) setting the user avatar, otherwise the `user_profile.html`
    template will raise exception as there is no fallback value for user avatar.
    """
    security: Security = app.security
    datastore: SQLAlchemyUserDatastore = security.datastore
    user.set_avatar()
    datastore.db.session.commit()

    if not app.config.get("SECURITY_CONFIRMABLE"):
        datastore.add_role_to_user(user, "user")


def post_email_confirmed(app: Flask, user: User, **extra_args):
    """
    Function to call on/after `user_confirmed` signal emitted by Flask-Security.

    This handles assigning the user a "user" role.
    """
    security: Security = app.security
    datastore: SQLAlchemyUserDatastore = security.datastore
    datastore.add_role_to_user(user, "user")


def post_user_login(app: Flask, user: User, **extra_args):
    """
    Function to call on/after `user_authenticated` signal emitted by Flask-Security.

    This handles flashing a message and redirecting user to the profile page.
    """
    flash(
        f"Welcome {current_user.name}, you've been logged in successfully!",
        "success",
    )


def user_tf_enabled(app: Flask, user: User, **extra_argss):
    """
    Function to call on/after `tf_profile_changed` signal emitted by Flask-Security.

    This handles flashing a message for the user.
    """
    flash("Make sure to generate and save recovery codes.", "success")


def user_tf_disabled(app: Flask, user: User, **extra_args):
    """
    Function to call on/after `tf_disabled` signal emitted by Flask-Security.

    This handles deleting mf recovery codes for the user in the database.
    Flask-Security doesn't do that as it is for multi-factor recovery codes, means
    other 2fa relies on it and not just 2fa code thingy.. (as far me can understand).
    """
    security: Security = app.security
    datastore: SQLAlchemyUserDatastore = security.datastore
    user.mf_recovery_codes = None
    datastore.db.session.commit()


user_registered.connect(post_user_registration)
user_confirmed.connect(post_email_confirmed)
user_authenticated.connect(post_user_login)
tf_profile_changed.connect(user_tf_enabled)
tf_disabled.connect(user_tf_disabled)


@bp.route("/login")
def login():
    """
    View to handle redirect to user's profile or admin page after successful login handled in `security.login` view.

    set this to `SECURITY_POST_LOGIN_VIEW` variable in config.py for Flask-Security.
    """
    if not current_user.is_authenticated:
        return redirect(url_for_security("login"))

    if current_user.has_role("admin"):
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("user.user_profile", username=current_user.username))


@bp.route("/logout")
def logout():
    """
    View to handle redirect to home page after user logout handled in `security.logout` view with custom flash message.

    If user is logged in, it will redirect back to `security.logout`.

    set this to `SECURITY_POST_LOGOUT_VIEW` variable in config.py for Flask-Security.
    """
    if current_user.is_authenticated:
        return redirect(url_for_security("logout"))
    flash("You've been logged out successfully!", "success")
    return redirect(url_for("main.index"))
