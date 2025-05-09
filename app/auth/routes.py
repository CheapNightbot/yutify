from flask import flash, redirect, url_for
from flask_security import current_user

from app.auth import bp


@bp.route("/login")  # , methods=["GET", "POST"]
def login():
    """
    View to handle redirect to user's profile after successful login handled in `security.login` view.

    set this to `SECURITY_POST_LOGIN_VIEW` variable in config.py for Flask-Security.
    """
    if current_user.is_authenticated:
        flash("You've logged in successfully!", "success")
        return redirect(url_for("user.user_profile", username=current_user.username))


@bp.route("/logout")
def logout():
    """
    View to handle redirect to home page after user logout handled in `security.logout` view with custom flash message.

    If user is logged in, it will redirect back to `security.logout`.

    set this to `SECURITY_POST_LOGOUT_VIEW` variable in config.py for Flask-Security.
    """
    if current_user.is_authenticated:
        return redirect(url_for("security.logout"))
    flash("You have been logged out successfully!", "success")
    return redirect(url_for("main.index"))


# @bp.route("/signup", methods=["GET", "POST"])
# def signup():
#     if current_user.is_authenticated:
#         return redirect(url_for("user.user_profile", username=current_user.username))

#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(
#             name=form.name.data, username=form.username.data, email=form.email.data
#         )
#         user.set_password(form.password.data)
#         user.set_avatar()
#         db.session.add(user)
#         db.session.commit()
#         flash(
#             "You're all set! Your account has been created. Log in now with your credentials",
#             "success",
#         )
#         return redirect(url_for("auth.login"))
#     return render_template(
#         "auth/signup.html",
#         title="Sign Up",
#         active_page="signup",
#         year=datetime.today().year,
#         form=form,
#     )


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
