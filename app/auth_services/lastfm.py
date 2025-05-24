import logging
from dataclasses import asdict
from collections import OrderedDict

import requests
import sqlalchemy as sa
from flask import flash, redirect, request, url_for
from flask_security import current_user
from authlib.integrations.flask_oauth2 import current_token
from yutipy.lastfm import LastFm, LastFmException

from app import db
from app.models import Service, User, UserData, UserService

# Create a logger for this module
logger = logging.getLogger(__name__)

try:
    lastfm = LastFm()
except LastFmException as e:
    logger.warning(
        f"Lastfm Authentication will be disabled due to the following error:\n{e}"
    )
    lastfm = None


def handle_lastfm_auth(lastfm_username):
    """Handle linking Last.fm by saving the username."""
    if not lastfm:
        flash(
            "Lastfm Authentication is not available! You may contact the admin(s).",
            "error",
        )
        return redirect(url_for("user.user_settings", username=current_user.username))

    # Fetch the service dynamically by name
    lastfm_service = db.session.scalar(
        sa.select(Service).where(Service.name.ilike("lastfm"))
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
        .where(UserService.user_id == user.id)
        .where(UserService.id == lastfm_service.id)
    )

    if user_service:
        flash("You have already linked Last.fm.", "success")
    else:
        # Try to fetch the user profile with provided username in the form
        result = lastfm.get_user_profile(lastfm_username)
        if "error" in result:
            flash(result.get("error") + " Make sure the username is correct!", "error")
            return redirect(
                url_for("user.user_settings", username=current_user.username)
            )

        # Create a new entry for Last.fm
        user_service = UserService(
            user_id=user.id,
            service_id=lastfm_service.id,
            username=result.get("username"),
            profile_url=result.get("url"),
        )
        user_service.user = user
        user_service.service = lastfm_service
        db.session.add(user_service)
        db.session.commit()
        flash("Successfully linked Last.fm!", "success")

    return redirect(url_for("user.user_settings", username=current_user.username))


def get_lastfm_activity(user=None):
    """Fetch the user's listening activity from Last.fm."""
    if not lastfm:
        flash(
            "Lastfm Authentication is not available! You may contact the admin(s).",
            "error",
        )
        return redirect(
            url_for(
                "user.user_settings",
                username=(user.username if user else current_user.username),
            )
        )

    user = user or current_user
    lastfm_service = db.session.scalar(
        sa.select(UserService)
        .join(Service)
        .where(
            UserService.user_id == user.id,
            Service.name.ilike("lastfm"),
        )
    )

    if not lastfm_service:
        return None

    activity = lastfm.get_currently_playing(username=lastfm_service.username)
    if activity:
        activity = asdict(activity)
        is_playing = activity.pop("is_playing")
        timestamp = activity.pop("timestamp")

        # Dynamically determine the base URL for the /api/search endpoint
        base_url = request.host_url.rstrip("/")  # Remove trailing slash
        search_url = f"{base_url}/api/search/{activity['artists']}:{activity['title']}"

        # Call the /api/search endpoint using requests
        try:
            response = requests.get(search_url, params={"all": ""})
            activity = {"music_info": response.json()}
        except requests.RequestException as e:
            logger.warning(e)
            activity = {"music_info": activity}

        # Add activity info
        activity["activity_info"] = {
            "is_playing": is_playing,
            "service": "lastfm",
            "timestamp": timestamp,
        }

        # Sort the activity by keys
        activity = OrderedDict(sorted(activity.items()))

        # Save the current activity to the database
        UserData.insert_or_update_user_data(lastfm_service, activity)
        return activity
    else:
        # Fetch the last activity from the database if no current activity is found
        existing_data = db.session.scalar(
            sa.select(UserData).where(UserData.user_service_id == lastfm_service.id)
        )
        if existing_data:
            data = existing_data.data
            data["activity_info"]["is_playing"] = False
            if not data.get("activity_info").get("timestamp"):
                data["activity_info"][
                    "timestamp"
                ] = existing_data.updated_at.timestamp()

            # Update the activity in the database
            UserData.insert_or_update_user_data(lastfm_service, data)
            return data

    return None
