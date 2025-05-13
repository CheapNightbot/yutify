from datetime import datetime

import sqlalchemy as sa
from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_security import (
    auth_required,
    current_user,
    logout_user,
    roles_required,
    send_mail,
    url_for_security,
)
from flask_security.utils import verify_password

from app import db
from app.models import Service, User, UserService
from app.user import bp
from app.user.forms import DeleteAccountForm, EditProfileForm, EmptyForm, LastfmLinkForm


@bp.route("/<username>", methods=["GET", "POST"])
@auth_required()
@roles_required("user")
def user_profile(username):
    """Render user profile page."""
    if username != current_user.username and not current_user.has_role("admin"):
        abort(404)

    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data.strip()
        user.about_me = " ".join(form.about_me.data.split())
        db.session.commit()
        flash("Your changes have been saved.", "success")
        return redirect(url_for("user.user_profile", username=user.username))

    return render_template(
        "user/user_profile.html",
        title="Profile",
        active_page="user_profile",
        year=datetime.today().year,
        user=user,
        form=form,
    )


@bp.route("/<username>/settings", methods=["GET", "POST"])
@auth_required()
@roles_required("user")
def user_settings(username):
    """Render user settings page."""
    if username != current_user.username:
        abort(404)

    security = current_app.security
    user = db.first_or_404(sa.select(User).where(User.username == username))
    # Query all services that are not private.
    # Service marked as private assumed to not have user authorization.
    services = db.session.scalars(
        sa.select(Service).where(Service.is_private.is_(False))
    ).all()
    # Query user services for the current user
    user_services = db.session.scalars(
        sa.select(UserService.service_id).where(UserService.user_id == current_user.id)
    ).all()

    # Create a dictionary to mark connected services
    connected_services = {service_id for service_id in user_services}

    # Forms ~
    email_form = EmptyForm()
    email_form.form_name.id = "change_email"
    email_form.form_name.name = "change_email"
    email_form.form_name.render_kw = {"value": "change_email"}
    username_form = EmptyForm()
    username_form.form_name.id = "change_username"
    username_form.form_name.name = "change_username"
    username_form.form_name.render_kw = {"value": "change_username"}
    delete_account_form = DeleteAccountForm()
    service_action_form = EmptyForm()
    lastfm_link_form = None if "lastfm" in connected_services else LastfmLinkForm()

    # User clicked on "Change" button for username
    if (
        username_form.validate_on_submit()
        and username_form.form_name.data == "change_username"
    ):
        return redirect(url_for_security("change_username"))

    # User clicked on "Change" button for email
    if email_form.validate_on_submit() and email_form.form_name.data == "change_email":
        return redirect(url_for_security("change_email"))

    # User clicked on "Delete Account" button
    if delete_account_form.validate_on_submit():
        if delete_account_form.validate_on_submit():
            password = security.password_util.normalize(request.form.get("password"))
            if not password or not verify_password(password, user.password):
                flash("Invalid password. Please try again.", "error")
                return redirect(
                    url_for("user.user_settings", username=current_user.username)
                )

            if current_app.config.get("YUTIFY_ACCOUNT_DELETE_EMAIL"):
                send_mail(
                    subject="[yutify] Account Deletion Notice!",
                    recipient=user.email,
                    template="notify_account_delete",
                    user=user,
                    admin_delete=False,
                    reason_for_deletion=None,
                )
            logout_user()
            security.datastore.delete_user(user)
            security.datastore.db.session.commit()
            flash("Your account has been deleted successfully!", "success")
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
        email_form=email_form,
        username_form=username_form,
        delete_account_form=delete_account_form,
        service_action_form=service_action_form,
        lastfm_link_form=lastfm_link_form,
    )


@bp.route("/username-changed")
@auth_required()
@roles_required("user")
def username_changed():
    """Handle redirect back to user settings page on successful username change."""
    return redirect(url_for("user.user_settings", username=current_user.username))


@bp.route("/email-changed")
@auth_required()
@roles_required("user")
def email_changed():
    """Handle redirect back to user settings page on successful email change."""
    return redirect(url_for("user.user_settings", username=current_user.username))
