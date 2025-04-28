import logging
from dataclasses import asdict

import requests
import sqlalchemy as sa
from flask import flash, redirect, request, url_for
from flask_login import current_user
from yutipy.lastfm import LastFm, LastFmException

from app import db
from app.models import Service, UserData, UserService, User

# Create a logger for this module
logger = logging.getLogger(__name__)

try:
    lastfm = LastFm()
except LastFmException as e:
    logger.warning(
        f"Lastfm Authentication will be disabled due to the following error:\n{e}"
    )


def handle_lastfm_auth(lastfm_username):
    """Handle linking Last.fm by saving the username."""
    if not lastfm:
        flash(
            "Lastfm Authentication is not available! You may contact the admin(s).",
            "error",
        )
        return redirect(url_for("user.user_settings", username=current_user.username))

    if not lastfm_username:
        flash("Last.fm username is required.", "error")
        return redirect(url_for("user.user_settings", username=current_user.username))

    # Fetch the service dynamically by name
    lastfm_service = db.session.scalar(
        sa.select(Service).where(Service.service_name.ilike("lastfm"))
    )
    if not lastfm_service:
        flash("Service 'Last.fm' not found in the database.", "error")
        return redirect(url_for("user.user_settings", username=current_user.username))

    user = db.session.scalar(
        sa.select(User).where(User.username == current_user.username)
    )

    # Check if the UserService entry already exists
    user_service = db.session.scalar(
        sa.select(UserService)
        .where(UserService.user_id == user.user_id)
        .where(UserService.service_id == lastfm_service.service_id)
    )

    if user_service:
        flash("You have already linked Last.fm.", "success")
    else:
        # Create a new entry for Last.fm
        user_service = UserService(
            user_id=current_user.user_id,
            service_id=lastfm_service.service_id,
            username=lastfm_username,
        )
        user_service.user = user
        user_service.service = lastfm_service
        db.session.add(user_service)
        db.session.commit()
        flash("Successfully linked Last.fm!", "success")

    return redirect(url_for("user.user_settings", username=current_user.username))


def get_lastfm_activity():
    """Fetch the user's listening activity from Last.fm."""
    if not lastfm:
        flash(
            "Lastfm Authentication is not available! You may contact the admin(s).",
            "error",
        )
        return redirect(url_for("user.user_settings", username=current_user.username))

    lastfm_service = db.session.scalar(
        sa.select(UserService)
        .join(Service)
        .where(
            UserService.user_id == current_user.user_id,
            Service.service_name.ilike("lastfm"),
        )
    )

    if not lastfm_service:
        return None

    activity = lastfm.get_currently_playing(username=lastfm_service.username)
    if activity:
        is_playing = activity.is_playing
        # Dynamically determine the base URL for the /api/search endpoint
        base_url = request.host_url.rstrip("/")  # Remove trailing slash
        search_url = f"{base_url}/api/search/{activity.artists}:{activity.title}"

        # Call the /api/search endpoint using requests
        try:
            response = requests.get(search_url, params={"all": ""})
            activity = response.json()
            activity["is_playing"] = is_playing
        except requests.RequestException as e:
            logger.warning(e)
            activity = asdict(activity)

        # Save the current activity to the database
        UserData.insert_or_update_user_data(lastfm_service, activity)
        return activity
    else:
        # Fetch the last activity from the database if no current activity is found
        existing_data = db.session.scalar(
            sa.select(UserData).where(
                UserData.user_service_id == lastfm_service.user_services_id
            )
        )
        if existing_data:
            return existing_data.data

    return None
