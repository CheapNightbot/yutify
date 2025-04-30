from datetime import datetime, timezone

import sqlalchemy as sa
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user

from app import db
from app.models import Service, User, UserService
from app.user import bp
from app.user.forms import (
    DeleteAccountForm,
    EditAccountForm,
    EditProfileForm,
    EmptyForm,
    LastfmLinkForm,
)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route("/<username>", methods=["GET", "POST"])
@login_required
def user_profile(username):
    """Render user profile page."""
    if username != current_user.username:
        abort(404)

    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        current_user.name = form.name.data.strip()
        current_user.about_me = " ".join(form.about_me.data.split())
        db.session.commit()
        flash("Your changes have been saved.", "success")
        return redirect(url_for("user.user_profile", username=current_user.username))

    return render_template(
        "user/user_profile.html",
        title="Profile",
        active_page="user_profile",
        year=datetime.today().year,
        user=user,
        form=form,
    )


@bp.route("/<username>/settings", methods=["GET", "POST"])
@login_required
def user_settings(username):
    """Render user settings page."""
    if username != current_user.username:
        abort(404)

    user = db.first_or_404(sa.select(User).where(User.username == username))
    # Query all services that are not private. Service marked as private assumed to not have user authorization.
    services = db.session.scalars(
        sa.select(Service).where(Service.is_private.is_(False))
    ).all()
    # Query user services for the current user
    user_services = db.session.scalars(
        sa.select(UserService.service_id).where(
            UserService.user_id == current_user.user_id
        )
    ).all()

    # Create a dictionary to mark connected services
    connected_services = {service_id for service_id in user_services}

    # Forms ~
    empty_form = EmptyForm()
    edit_account_form = EditAccountForm(current_user.username, current_user.email)
    delete_account_form = DeleteAccountForm()
    lastfm_link_form = None if "lastfm" in connected_services else LastfmLinkForm()

    # Check if the "Edit Account Details" button was clicked
    if (
        request.method == "POST"
        and "submit" in request.form
        and request.form["submit"] == "Edit Account Details"
    ):
        # Render the EditAccountForm when user clicks on "Edit Account Details" button
        return render_template(
            "user/user_settings.html",
            title="Edit Account",
            active_page="user_settings",
            year=datetime.today().year,
            user=user,
            form=edit_account_form,
        )

    # Check if user clicked on "Save Account Details" after filling `EditAccountForm` form
    elif (
        request.method == "POST"
        and "submit" in request.form
        and request.form["submit"] == "Save Account Details"
    ):
        if edit_account_form.validate_on_submit():
            current_user.username = edit_account_form.username.data
            current_user.email = edit_account_form.email.data
            db.session.commit()
            flash("Your changes have been saved.", "success")
            return redirect(
                url_for("user.user_settings", username=current_user.username)
            )
        # EditAccountForm with errors as above if statement was False
        else:
            flash(
                "Something went wrong while saving changes! Please try again.", "error"
            )
            return render_template(
                "user/user_settings.html",
                title="Edit Account",
                active_page="user_settings",
                year=datetime.today().year,
                user=user,
                form=edit_account_form,
            )

    # User clicked on "Delete Account" button
    elif (
        request.method == "POST"
        and "submit" in request.form
        and request.form["submit"] == "Delete Account"
    ):
        if delete_account_form.validate_on_submit():
            password = request.form.get("password")
            if not password or not user.check_password(password):
                flash("Invalid password. Please try again.", "error")
                return redirect(
                    url_for("user.user_settings", username=current_user.username)
                )

            logout_user()
            db.session.delete(user)
            db.session.commit()
            flash("Your account has been deleted.", "success")
            return redirect(url_for("main.index"))

    # Default: Render the empty form on "GET" request
    return render_template(
        "user/user_settings.html",
        title="Settings",
        active_page="user_settings",
        year=datetime.today().year,
        user=user,
        services=services,
        connected_services=connected_services,
        form=empty_form,
        delete_account_form=delete_account_form,
        lastfm_link_form=lastfm_link_form,
    )
