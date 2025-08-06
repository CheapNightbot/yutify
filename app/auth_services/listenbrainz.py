import logging
from collections import OrderedDict
from dataclasses import asdict
from datetime import datetime, timezone

import requests
import sqlalchemy as sa
from flask import flash, redirect, url_for
from flask_security import current_user
from yutipy.listenbrainz import ListenBrainz

from app.extensions import db
from app.models import Service, User, UserData, UserService

logger = logging.getLogger(__name__)


FRESHNESS_SECONDS = 60  # For user activity data

LISTENBRAINZ_SERVICE_NOT_FOUND = "Service 'ListenBrainz not found in the database."
LISTENBRAINZ_SERVICE_NOT_AVAILABLE = (
    "ListenBrainz Authentication is not available! You may contact the support team."
)
USER_SETTINGS_ENDPOINT = "user.user_settings"


def handle_listenbrainz_auth(listenbrainz_username):
    """Handle linking ListenBrainz by saving the username."""

    listenbrainz_service = db.session.scalar(
        sa.select(Service).where(Service.name.ilike("listenbrainz"))
    )
    if not listenbrainz_service:
        logger.warning(LISTENBRAINZ_SERVICE_NOT_FOUND)
        flash(LISTENBRAINZ_SERVICE_NOT_FOUND, "error")
        return redirect(url_for(USER_SETTINGS_ENDPOINT, username=current_user.username))

    user = db.session.scalar(
        sa.select(User).where(User.username == current_user.username)
    )

    # Check if the UserService for ListenBrainz already exists for current user
    user_service = db.session.scalar(
        sa.select(UserService)
        .where(UserService.user_id == user.id)
        .where(UserService.id == listenbrainz_service.id)
    )

    if user_service:
        flash("You have already liked ListenBrainz.", "info")
        return redirect(url_for(USER_SETTINGS_ENDPOINT, username=current_user.username))

    with ListenBrainz() as listenbrainz:
        username = listenbrainz.find_user(listenbrainz_username)
        if not username:
            flash(
                "Failed to fetch ListenBrainz profile. Make sure the username is correct!",
                "error",
            )
            return redirect(
                url_for(USER_SETTINGS_ENDPOINT, username=current_user.username)
            )

        # Create a new entry to ListenBrainz
        user_service = UserService(
            user_id=user.id,
            service_id=listenbrainz_service.id,
            username=username,
            profile_url=f"https://listenbrainz.org/user/{username}",
        )
        user_service.user = user
        user_service.service = listenbrainz_service
        db.session.add(user_service)
        db.session.commit()
        flash("Successfully linked ListenBrainz!", "success")

    return redirect(url_for(USER_SETTINGS_ENDPOINT, username=current_user.username))


def get_listenbrainz_activity(user=None, platform="all", force_refresh=False):
    """Fetch the user's listening activity from ListenBrainz."""
    user = user or current_user
    listenbrainz_service = db.session.scalar(
        sa.select(UserService)
        .join(Service)
        .where(UserService.user_id == user.id, Service.name.ilike("listenbrainz"))
    )

    if not listenbrainz_service or not listenbrainz_service.user_data:
        return None

    activity_data = listenbrainz_service.user_data.data
    if (
        not force_refresh
        and listenbrainz_service.user_data
        and listenbrainz_service.user_data.updated_at
    ):
        updated_at = listenbrainz_service.user_data.updated_at
        try:
            age = (datetime.now(timezone.utc) - updated_at).total_seconds()
        except TypeError:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - updated_at).total_seconds()
        if age < FRESHNESS_SECONDS:
            if not activity_data.get("activity_info", {}).get("is_playing", False):
                activity_data["activity_info"]["is_playing"] = False
            return activity_data

    with ListenBrainz() as listenbrainz:
        fetched_activity = listenbrainz.get_currently_playing(
            listenbrainz_service.username
        )
        if fetched_activity:
            if fetched_activity.title == activity_data.get("music_info", {}).get(
                "title"
            ):
                activity_data["activity_info"]["is_playing"] = (
                    fetched_activity.is_playing or False
                )
                UserData.insert_or_update_user_data(listenbrainz_service, activity_data)
                return activity_data

            fetched_activity = asdict(fetched_activity)
            is_playing = fetched_activity.pop("is_playing")
            timestamp = fetched_activity.pop("timestamp")

            base_url = url_for("main.index", _external=True).rstrip("/")
            search_url = f"{base_url}/api/search/{fetched_activity['artists']}:{fetched_activity['title']}"

            try:
                response = requests.get(
                    search_url, params={"platform": platform}, timeout=30
                )
                activity = {"music_info": response.json()}
            except requests.RequestException as e:
                logger.warning(e)
                activity = {"music_info": fetched_activity}

            if activity.get("music_info").get("error"):
                activity = {"music_info": fetched_activity}

            activity["activity_info"] = {
                "is_playing": is_playing,
                "service": "listenbrainz",
                "timestamp": timestamp,
            }

            activity = OrderedDict(sorted(activity.items()))
            UserData.insert_or_update_user_data(listenbrainz_service, activity)
            return activity
        else:
            existing_data = db.session.scalar(
                sa.select(UserData).where(
                    UserData.user_service_id == listenbrainz_service.id
                )
            )
            if existing_data:
                activity_data = existing_data.data
                activity_data["activity_info"]["is_playing"] = False
                if not activity_data.get("activity_info").get("timestamp"):
                    activity_data["activity_info"][
                        "timestamp"
                    ] = existing_data.updated_at.timestamp()

                UserData.insert_or_update_user_data(listenbrainz_service, activity_data)
                return activity_data
        return None
