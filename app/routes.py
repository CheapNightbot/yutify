from datetime import datetime, timezone
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_restful import Resource, abort

from app import api, app, db
from app.common.logger import logger
from app.email import send_password_reset_email
from app.forms import (
    EditAccountForm,
    EditProfileForm,
    EmptyForm,
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
    SearchForm,
)
from app.models import User
from app.resources.search import YutifySearch


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the index/home page."""
    form = SearchForm()

    if form.validate_on_submit():
        # Create an instance of the Search resource
        search_resource = YutifySearch()
        artist = form.artist.data
        song = form.song.data

        # Call the get method directly with the artist and song parameters
        response = search_resource.get(artist, song)
        result = response.get_json()

        if result.get("error"):
            return render_template(
                "index.html",
                title="Home",
                active_page="home",
                artist=artist,
                song=song,
                album_art="static/favicon.svg",
                title_=result.get("error"),
                year=datetime.today().year,
                form=form,
            )

        return render_template(
            "index.html",
            title="Home",
            active_page="home",
            album_art=result.get("album_art"),
            album_title=result.get("album_title"),
            album_type=result.get("album_type"),
            artist=artist,
            artists=result.get("artists"),
            deezer=result.get("url").get("deezer"),
            genre=result.get("genre"),
            itunes=result.get("url").get("itunes"),
            kkbox=result.get("url").get("kkbox"),
            lyrics=(
                result.get("lyrics").replace("\r", "").replace("\n", "<br>")
                if result.get("lyrics")
                else None
            ),
            song=song,
            spotify=result.get("url").get("spotify"),
            title_=result.get("title"),
            yt_music=result.get("url").get("ytmusic"),
            year=datetime.today().year,
            form=form,
        )

    return render_template(
        "index.html", title="Home", active_page="home", year=datetime.today().year, form=form
    )


@app.route("/docs")
def docs():
    """Render the API documentation page."""
    return render_template(
        "docs.html", title="Docs", active_page="docs", year=datetime.today().year
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Render the login page."""
    if current_user.is_authenticated:
        return redirect(url_for("user_profile", username=current_user.username))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("user_profile", username=current_user.username)
        return redirect(next_page)
    return render_template(
        "login.html",
        title="Login",
        active_page="login",
        year=datetime.today().year,
        form=form,
    )


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out successfully!", "success")
    return redirect(url_for("index"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("user_profile", username=current_user.username))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data, username=form.username.data, email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(
            "You're all set! Your account has been created. Log in now with your credentials",
            "success",
        )
        return redirect(url_for("login"))
    return render_template(
        "signup.html",
        title="Sign Up",
        active_page="signup",
        year=datetime.today().year,
        form=form,
    )


@app.route("/u/<username>", methods=["GET", "POST"])
@login_required
def user_profile(username):
    """Render user profile page."""
    if username != current_user.username:
        abort(404)

    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        current_user.name = form.name.data.strip()
        current_user.about_me = form.about_me.data.strip()
        db.session.commit()
        flash("Your changes have been saved.", "success")
        return redirect(url_for("user_profile", username=current_user.username))

    return render_template(
        "user_profile.html",
        title="Profile",
        active_page="user_profile",
        year=datetime.today().year,
        user=user,
        form=form,
    )


@app.route("/u/<username>/settings", methods=["GET", "POST"])
@login_required
def user_settings(username):
    """Render user settings page."""
    if username != current_user.username:
        abort(404)

    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EditAccountForm(current_user.username, current_user.email)

    # Check if the "Edit Account Details button was clicked"
    if (
        request.method == "POST"
        and "submit" in request.form
        and request.form["submit"] == "Edit Account Details"
    ):
        # Render the EditAccountForm when user clicks on "Edit Account Details" button
        return render_template(
            "user_settings.html",
            title="Edit Account",
            active_page="user_settings",
            year=datetime.today().year,
            user=user,
            form=form,
        )

    elif (
        request.method == "POST"
        and "submit" in request.form
        and request.form["submit"] == "Save Account Details"
    ):

        # User clicked on "Save Account Details" after filling form
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Your changes have been saved.", "success")
            return redirect(url_for("user_settings", username=current_user.username))
        else:
            # EditAccountForm with errors as above if statement was False
            flash(
                "Something went wrong while saving changes! Please try again.", "error"
            )
            return render_template(
                "user_settings.html",
                title="Edit Account",
                active_page="user_settings",
                year=datetime.today().year,
                user=user,
                form=form,
            )

    # Default: Render the empty form on "GET" request
    form = EmptyForm()
    return render_template(
        "user_settings.html",
        title="Settings",
        active_page="user_settings",
        year=datetime.today().year,
        user=user,
        form=form,
    )


@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email_hash = User.hash_email(form.email.data)
        user = db.session.scalar(sa.select(User).where(User._email_hash == email_hash))
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instructions to reset your password", "success")
        return redirect(url_for("login"))
    return render_template(
        "reset_password_request.html",
        title="Request Password Reset",
        active_page="reset_password_request",
        year=datetime.today().year,
        form=form,
    )


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_password_token(token)
    if not user:
        flash("The password reset link has expired.", "error")
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(
            "Your password has been reset. You can now log in with your new password.",
            "success",
        )
        return redirect(url_for("login"))
    return render_template(
        "reset_password.html",
        title="Reset Your Password",
        active_page="reset_password",
        year=datetime.today().year,
        form=form,
    )


########## API ENDPOINTS ##########

api.add_resource(YutifySearch, "/api/search/<path:artist>:<path:song>")

########## END API ENDPOINTS ##########
