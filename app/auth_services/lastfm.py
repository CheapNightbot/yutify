import logging
from collections import OrderedDict
from dataclasses import asdict
from datetime import datetime, timezone

import requests
import sqlalchemy as sa
from flask import flash, redirect, url_for
from flask_security import current_user
from yutipy.lastfm import LastFm, LastFmException

from app import db
from app.models import Service, User, UserData, UserService

# Create a logger for this module
logger = logging.getLogger(__name__)


FRESHNESS_SECONDS = 60  # For user activity data

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
        if not result:
            flash(
                "Failed to fetch Last.fm profile. Make sure the username is correct!",
                "error",
            )
            return redirect(
                url_for("user.user_settings", username=current_user.username)
            )
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


def get_lastfm_activity(user=None, force_refresh=False):
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

    # Check for fresh data unless force_refresh is True
    activity_data = lastfm_service.user_data.data
    if (
        not force_refresh
        and lastfm_service.user_data
        and lastfm_service.user_data.updated_at
    ):
        updated_at = lastfm_service.user_data.updated_at
        try:
            age = (datetime.now(timezone.utc) - updated_at).total_seconds()
        except TypeError:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - updated_at).total_seconds()
        if age < FRESHNESS_SECONDS:
            if not activity_data.get("activity_info", {}).get("is_playing", False):
                activity_data["activity_info"]["is_playing"] = False
            return activity_data

    fetched_activity = lastfm.get_currently_playing(username=lastfm_service.username)
    if fetched_activity:
        if fetched_activity.title == activity_data.get("music_info").get("title"):
            # For updating `updated_at` field in database
            UserData.insert_or_update_user_data(lastfm_service, activity_data)
            return activity_data

        fetched_activity = asdict(fetched_activity)
        is_playing = fetched_activity.pop("is_playing")
        timestamp = fetched_activity.pop("timestamp")

        # Dynamically determine the base URL for the /api/search endpoint
        base_url = url_for("main.index", _external=True).rstrip("/")
        search_url = f"{base_url}/api/search/{fetched_activity['artists']}:{fetched_activity['title']}"

        # Call the /api/search endpoint using requests
        try:
            response = requests.get(search_url, params={"all": ""})
            activity = {"music_info": response.json()}
        except requests.RequestException as e:
            logger.warning(e)
            activity = {"music_info": fetched_activity}

        if activity.get("music_info").get("error"):
            activity = {"music_info": fetched_activity}

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
            activity_data = existing_data.data
            activity_data["activity_info"]["is_playing"] = False
            if not activity_data.get("activity_info").get("timestamp"):
                activity_data["activity_info"][
                    "timestamp"
                ] = existing_data.updated_at.timestamp()

            # Update the activity in the database
            UserData.insert_or_update_user_data(lastfm_service, activity_data)
            return activity_data

    return None
