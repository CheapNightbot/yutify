from flask import flash, redirect, url_for, current_app
from flask_security import current_user, url_for_security

from app.auth import bp


@bp.route("/login")
def login():
    """
    View to handle redirect to user's profile or admin page after successful login handled in `security.login` view.

    set this to `SECURITY_POST_LOGIN_VIEW` variable in config.py for Flask-Security.
    """
    if current_user.is_authenticated:
        security = current_app.security
        if "user" not in current_user.roles:
            security.datastore.add_role_to_user(current_user, "user")
        if not current_user.avatar:
            current_user.set_avatar()
        security.datastore.db.session.commit()

        flash(
            f"Welcome {current_user.name}, you've been logged in successfully!",
            "success",
        )
        if current_user.has_role("admin"):
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.user_profile", username=current_user.username))

    return redirect(url_for_security("login"))


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


@bp.route("/signup")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("user.user_profile", username=current_user.username))

    try:
        print(current_user.username)
    except Exception:
        print(current_user)

    return redirect(url_for("auth.login"))


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
