from flask import Flask, flash, redirect, url_for
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    current_user,
    url_for_security,
)
from flask_security.signals import user_authenticated, user_confirmed, user_registered

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


user_registered.connect(post_user_registration)
user_confirmed.connect(post_email_confirmed)
user_authenticated.connect(post_user_login)


@bp.route("/login")
def login():
    """
    View to handle redirect to user's profile or admin page after successful login handled in `security.login` view.

    set this to `SECURITY_POST_LOGIN_VIEW` variable in config.py for Flask-Security.
    """
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


# @bp.route("/signup")
# def signup():
#     if current_user.is_authenticated:
#         return redirect(url_for("user.user_profile", username=current_user.username))
#     return redirect(url_for("auth.login"))


@bp.route("/email-verified")
def email_verified():
    if current_user.is_authenticated:
        return redirect(url_for("user.user_profile", username=current_user.username))

    flash(
        "Thank you for verifying your email! You're all set, now login with your credentials!",
        "success",
    )
    print(current_user)
    return redirect(url_for_security("login"))


# @bp.route("/reset_password_request", methods=["GET", "POST"])
# def reset_password_request():
#     if current_user.is_authenticated:
#         return redirect(url_for("main.index"))
#     form = ResetPasswordRequestForm()
#     if form.validate_on_submit():
#         email_hash = User.hash_email(form.email.data)
#         user = db.session.scalar(sa.select(User).where(User._email_hash == email_hash))
#         if user:
#             send_password_reset_email(user)
#         flash("Check your email for the instructions to reset your password", "success")
#         return redirect(url_for("auth.login"))
#     return render_template(
#         "auth/reset_password_request.html",
#         title="Request Password Reset",
#         active_page="reset_password_request",
#         year=datetime.today().year,
#         form=form,
#     )


# @bp.route("/reset_password/<token>", methods=["GET", "POST"])
# def reset_password(token):
#     if current_user.is_authenticated:
#         return redirect(url_for("main.index"))
#     user = User.verify_reset_password_token(token)
#     if not user:
#         flash("The password reset link has expired.", "error")
#         return redirect(url_for("main.index"))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         user.set_password(form.password.data)
#         db.session.commit()
#         flash(
#             "Your password has been reset. You can now log in with your new password.",
#             "success",
#         )
#         return redirect(url_for("auth.login"))
#     return render_template(
#         "auth/reset_password.html",
#         title="Reset Your Password",
#         active_page="reset_password",
#         year=datetime.today().year,
#         form=form,
#     )
