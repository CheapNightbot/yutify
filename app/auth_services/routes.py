import sqlalchemy as sa
from flask import abort, flash, redirect, request, url_for
from flask_security import auth_required, current_user

from app import db
from app.auth_services import bp
from app.auth_services.lastfm import handle_lastfm_auth
from app.auth_services.spotify import handle_spotify_auth, handle_spotify_callback
from app.models import Service, UserService
from app.user.forms import LastfmLinkForm


@bp.route("/<service>", methods=["POST"])
@auth_required()
def service(service):
    match service:
        case "spotify":
            return handle_spotify_auth()
        case "lastfm":
            form = LastfmLinkForm()
            if form.validate_on_submit():
                lastfm_username = form.lastfm_username.data.strip()
                return handle_lastfm_auth(lastfm_username)
            flash("Last.fm username is required.", "error")
            return redirect(
                url_for("user.user_settings", username=current_user.username)
            )
        case _:
            abort(404, description="Service not supported.")


@bp.route("/<service>/callback")
@auth_required()
def callback(service):
    match service:
        case "spotify":
            return handle_spotify_callback(request)
        case "lastfm":
            return redirect(
                url_for("user.user_settings", username=current_user.username)
            )
        case _:
            abort(404, description="Service not supported.")


@bp.route("/<service>/unlink", methods=["POST"])
@auth_required()
def unlink(service):
    # Fetch the service dynamically by name
    service_obj = db.session.scalar(
        sa.select(Service).where(Service.name.ilike(service))
    )
    if not service_obj:
        abort(404, description="Service not found.")

    # Fetch the UserService entry for the current user and the service
    user_service = db.session.scalar(
        sa.select(UserService)
        .where(UserService.user_id == current_user.id)
        .where(UserService.service_id == service_obj.id)
    )
    if not user_service:
        flash(f"You have not linked {service.capitalize()}.", "error")
        return redirect(url_for("user.user_settings", username=current_user.username))

    # Delete the UserService entry
    db.session.delete(user_service)
    db.session.commit()

    flash(f"Successfully unlinked {service.capitalize()}!", "success")
    return redirect(url_for("user.user_settings", username=current_user.username))
