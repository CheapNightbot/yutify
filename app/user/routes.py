from datetime import datetime

import sqlalchemy as sa
from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_security import (
    auth_required,
    current_user,
    logout_user,
    permissions_accepted,
    send_mail,
    url_for_security,
)
from flask_security.utils import verify_password

from app import db
from app.models import OAuth2Client, OAuth2Token, Service, User, UserService
from app.user import bp
from app.user.forms import (
    DeleteAccountForm,
    EditProfileForm,
    EmptyForm,
    LastfmLinkForm,
    ProfileVisibilityForm,
)


@bp.route("/<username>", methods=["GET", "POST"])
def user_profile(username):
    """Render user profile page."""
    user = db.first_or_404(sa.select(User).where(User.username == username))

    # Restrict access if profile is private and not the owner
    if not current_user.is_authenticated and not user.is_profile_public:
        abort(404)
    if not user.is_profile_public and current_user.username != user.username:
        abort(404)

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
@permissions_accepted("user-read", "user-write")
def user_settings(username):
    """Render user settings page."""
    if username != current_user.username:
        abort(404)

    security = current_app.security
    user = db.first_or_404(sa.select(User).where(User.username == username))
    # Only count unique clients for authorized apps
    authorized_apps = (
        db.session.query(OAuth2Client)
        .join(OAuth2Token, OAuth2Token.client_id == OAuth2Client.client_id)
        .filter(OAuth2Token.user_id == user.id)
        .distinct(OAuth2Client.client_id)
        .all()
    )

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
    username_form = EmptyForm()
    delete_account_form = DeleteAccountForm()
    service_action_form = EmptyForm()
    lastfm_link_form = None if "lastfm" in connected_services else LastfmLinkForm()
    profile_visibility_form = ProfileVisibilityForm()

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
        password = security.password_util.normalize(request.form.get("password"))
        if not password or not verify_password(password, user.password):
            flash("Invalid password. Please try again.", "error")
            return redirect(
                url_for("user.user_settings", username=current_user.username)
            )

        if current_app.config.get("YUTIFY_ACCOUNT_DELETE_EMAIL"):
            send_mail(
                subject=f"[{current_app.config['SERVICE']}] Account Deletion Notice!",
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

    if profile_visibility_form.validate_on_submit():
        user.is_profile_public = bool(profile_visibility_form.is_profile_public.data)
        db.session.commit()
        if user.is_profile_public:
            flash(
                "Your profile is now public. Anyone with your profile link can view your information.",
                "success",
            )
        else:
            flash(
                "Your profile is now private. Only you can view your profile page.",
                "success",
            )
        return redirect(url_for("user.user_settings", username=user.username))

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
        profile_visibility_form=profile_visibility_form,
        authorized_apps=authorized_apps,
    )


@bp.route("/<username>/authorized-apps", methods=["GET"])
@auth_required()
@permissions_accepted("user-read", "user-write")
def authorized_apps_overview(username):
    """Show all authorized OAuth2 apps for the user with revoke option."""
    if username != current_user.username:
        abort(404)
    user = db.first_or_404(sa.select(User).where(User.username == username))
    # Get all tokens for this user, join with client
    tokens = (
        db.session.query(OAuth2Token, OAuth2Client)
        .join(OAuth2Client, OAuth2Token.client_id == OAuth2Client.client_id)
        .filter(OAuth2Token.user_id == user.id)
        .all()
    )
    # Remvove duplicates by client_id
    unique_clients = {}
    for token, client in tokens:
        if client.client_id not in unique_clients:
            unique_clients[client.client_id] = (token, client)
    tokens = list(unique_clients.values())
    from app.user.forms import RevokeAppForm

    revoke_forms = {
        client.client_id: RevokeAppForm(prefix=f"revoke_{client.client_id}")
        for token, client in tokens
    }
    return render_template(
        "user/authorized_apps.html",
        title="Authorized Apps",
        active_page="user_settings",
        year=datetime.today().year,
        user=user,
        tokens=tokens,
        revoke_forms=revoke_forms,
    )


@bp.route("/<username>/authorized-apps/revoke/<client_id>", methods=["POST"])
@auth_required()
@permissions_accepted("user-read", "user-write")
def revoke_authorized_app(username, client_id):
    if username != current_user.username:
        abort(404)
    user = db.first_or_404(sa.select(User).where(User.username == username))
    # Delete all tokens for this user and client
    deleted = OAuth2Token.query.filter_by(user_id=user.id, client_id=client_id).delete()
    db.session.commit()
    if deleted:
        flash("Access revoked for this app.", "success")
    else:
        flash("No access found for this app.", "error")
    return redirect(url_for("user.authorized_apps_overview", username=username))


@bp.route("/username-changed")
@auth_required()
@permissions_accepted("user-read", "user-write")
def username_changed():
    """Handle redirect back to user settings page on successful username change."""
    return redirect(url_for("user.user_settings", username=current_user.username))


@bp.route("/email-changed")
@auth_required()
@permissions_accepted("user-read", "user-write")
def email_changed():
    """Handle redirect back to user settings page on successful email change."""
    return redirect(url_for("user.user_settings", username=current_user.username))
