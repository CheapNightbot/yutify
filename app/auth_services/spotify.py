import logging
from collections import OrderedDict
from dataclasses import asdict
from datetime import datetime, timezone

import requests
import sqlalchemy as sa
from flask import flash, redirect, session, url_for
from flask_security import current_user
from yutipy.exceptions import AuthenticationException
from yutipy.spotify import SpotifyAuth, SpotifyAuthException

from app import db
from app.models import Service, User, UserData, UserService

# Create a logger for this module
logger = logging.getLogger(__name__)


FRESHNESS_SECONDS = 60  # For user activity data

# Constants for repeated string literals
SPOTIFY_SERVICE_NOT_FOUND = "Service 'Spotify' not found in the database."
SPOTIFY_AUTH_NOT_AVAILABLE = (
    "Spotify Authentication is not available! You may contact the support team."
)
USER_SETTINGS_ENDPOINT = "user.user_settings"


class MySpotifyAuth(SpotifyAuth):
    """Custom class to ovver-ride the `save_access_token` and `load_access_token` methods ~"""

    def __init__(self, user=None, *args, **kwargs):
        self.user = user  # Set user before calling super().__init__
        super().__init__(*args, **kwargs, defer_load=True)  # Defer token loading

    def save_access_token(self, token_info: dict) -> None:
        user = db.session.scalar(
            sa.select(User).where(User.username == self.user.username)
        )

        if user:
            # Fetch the service dynamically by name
            spotify_service = db.session.scalar(
                sa.select(Service).where(Service.name.ilike("spotify"))
            )
            if not spotify_service:
                logger.warning(SPOTIFY_SERVICE_NOT_FOUND)
                return

            # Check if the UserService entry already exists for this user and service
            user_service = db.session.scalar(
                sa.select(UserService)
                .where(UserService.user_id == user.id)
                .where(UserService.service_id == spotify_service.id)
            )

            if user_service:
                # Update the existing entry
                user_service.access_token = token_info.get("access_token")
                user_service.refresh_token = token_info.get("refresh_token")
                user_service.expires_in = token_info.get("expires_in")
                user_service.requested_at = token_info.get("requested_at")
            else:
                result = self.get_user_profile()
                if not result:
                    logger.warning(
                        "Could not fetch Spotify user profile. Aborting UserService creation."
                    )
                    return
                username = result.get("display_name", None)
                profile_url = result.get("url", None)

                # Always set user_id and service_id explicitly
                user_service = UserService(
                    user_id=user.id,
                    service_id=spotify_service.id,
                    access_token=token_info.get("access_token"),
                    refresh_token=token_info.get("refresh_token"),
                    expires_in=token_info.get("expires_in"),
                    requested_at=token_info.get("requested_at"),
                    username=username,
                    profile_url=profile_url,
                )
                db.session.add(user_service)
            db.session.commit()

        return None

    def load_access_token(self) -> dict | None:
        user = db.session.scalar(
            sa.select(User).where(User.username == self.user.username)
        )

        if user:
            # Fetch the service dynamically by name
            spotify_service = db.session.scalar(
                sa.select(Service).where(Service.name.ilike("spotify"))
            )
            if not spotify_service:
                logger.warning(SPOTIFY_SERVICE_NOT_FOUND)
                return

            # Check if the UserService entry exists
            user_service = db.session.scalar(
                sa.select(UserService)
                .where(UserService.user_id == user.id)
                .where(UserService.service_id == spotify_service.id)
            )

            if user_service:
                return {
                    "access_token": user_service.access_token,
                    "refresh_token": user_service.refresh_token,
                    "expires_in": user_service.expires_in,
                    "requested_at": user_service.requested_at,
                }
        return None


def get_spotify_auth(user=None):
    """Get an instance of MySpotifyAuth for the current user."""
    user = user or current_user
    return MySpotifyAuth(user=user, scopes=["user-read-currently-playing"])


def handle_spotify_auth():
    try:
        with get_spotify_auth(user=current_user) as spotify_auth:
            spotify_auth.load_token_after_init()

            # Fetch the service dynamically by name
            service = db.session.scalar(
                sa.select(Service).where(Service.name.ilike("spotify"))
            )
            if not service:
                logger.warning(SPOTIFY_SERVICE_NOT_FOUND)
                flash(SPOTIFY_AUTH_NOT_AVAILABLE, "error")
                return redirect(
                    url_for(USER_SETTINGS_ENDPOINT, username=current_user.username)
                )

            user_service = db.session.scalar(
                sa.select(UserService)
                .where(UserService.user_id == current_user.id)
                .where(UserService.service_id == service.id)
            )

            if user_service:
                flash("You have already linked Spotify.", "success")
                return redirect(
                    url_for(USER_SETTINGS_ENDPOINT, username=current_user.username)
                )

            state = spotify_auth.generate_state()
            session["state"] = state
            auth_url = spotify_auth.get_authorization_url(state=state, show_dialog=True)

            return redirect(auth_url)
    except SpotifyAuthException:
        flash(SPOTIFY_AUTH_NOT_AVAILABLE, "error")
        return redirect(url_for(USER_SETTINGS_ENDPOINT, username=current_user.username))


def handle_spotify_callback(request):
    """Handle the Spotify OAuth callback."""
    try:
        with get_spotify_auth(user=current_user) as spotify_auth:
            spotify_auth.load_token_after_init()

            code = request.args.get("code")
            state = request.args.get("state")
            expected_state = session.get("state")

            if not code or not state:
                flash(
                    "Authorization canceled. It seems you chose not to grant access to your Spotify account.",
                    "error",
                )
                session.pop("state")
                return redirect(
                    url_for(USER_SETTINGS_ENDPOINT, username=current_user.username)
                )

            try:
                spotify_auth.callback_handler(code, state, expected_state)
            except AuthenticationException:
                flash(
                    "Something went wrong while authenticating with Spotify.", "error"
                )
                session.pop("state")
                return redirect(
                    url_for(USER_SETTINGS_ENDPOINT, username=current_user.username)
                )

            flash("Successfully linked Spotify!", "success")
            session.pop("state")
            return redirect(
                url_for(USER_SETTINGS_ENDPOINT, username=current_user.username)
            )
    except SpotifyAuthException:
        flash(
            SPOTIFY_AUTH_NOT_AVAILABLE,
            "error",
        )
        return redirect(url_for(USER_SETTINGS_ENDPOINT, username=current_user.username))


def get_spotify_activity(user=None, platform="all", force_refresh=False):
    """Fetch the user's listening activity from Spotify."""
    user = user or current_user
    try:
        with get_spotify_auth(user=user) as spotify_auth:
            spotify_auth.load_token_after_init()
            spotify_service = db.session.scalar(
                sa.select(UserService)
                .join(Service)
                .where(
                    UserService.user_id == user.id,
                    Service.name.ilike("spotify"),
                )
            )

            if not spotify_service or not spotify_service.user_data:
                return None

            # Check for fresh data unless force_refresh is True
            activity_data = (
                spotify_service.user_data.data if spotify_service.user_data else None
            )
            if (
                not force_refresh
                and spotify_service.user_data
                and spotify_service.user_data.updated_at
            ):
                updated_at = spotify_service.user_data.updated_at
                try:
                    age = (datetime.now(timezone.utc) - updated_at).total_seconds()
                except TypeError:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)
                    age = (datetime.now(timezone.utc) - updated_at).total_seconds()
                if age < FRESHNESS_SECONDS:
                    if activity_data and not activity_data.get("activity_info", {}).get(
                        "is_playing", False
                    ):
                        if "activity_info" not in activity_data:
                            activity_data["activity_info"] = {}
                        activity_data["activity_info"]["is_playing"] = False
                    return activity_data

            fetched_activity = spotify_auth.get_currently_playing()
            if fetched_activity:
                fetched_dict = asdict(fetched_activity)
                title = fetched_dict.get("title")

                if (
                    activity_data
                    and activity_data.get("music_info", {}).get("title") == title
                ):
                    try:
                        if "activity_info" not in activity_data:
                            activity_data["activity_info"] = {}
                        activity_data["activity_info"]["is_playing"] = fetched_dict.get(
                            "is_playing", False
                        )
                        activity_data["activity_info"]["timestamp"] = fetched_dict.get(
                            "timestamp", datetime.now(timezone.utc).timestamp()
                        )
                    except KeyError:
                        activity_data = {
                            "music_info": activity_data.get("music_info", {}),
                            "activity_info": {
                                "is_playing": fetched_dict.get("is_playing", False),
                                "timestamp": fetched_dict.get(
                                    "timestamp", datetime.now(timezone.utc).timestamp()
                                ),
                            },
                        }
                    # This is just to update the `updated_at` field in database
                    UserData.insert_or_update_user_data(spotify_service, activity_data)
                    return activity_data

                is_playing = fetched_dict.pop("is_playing", False)
                timestamp = fetched_dict.pop("timestamp", None)
                spotify_url = fetched_dict.pop("url", None)
                activity = {"music_info": fetched_dict}
                if spotify_url:
                    activity["music_info"]["url"] = {"spotify": spotify_url}

                # Prepare activity_info with all required fields
                activity["activity_info"] = {
                    "is_playing": is_playing,
                    "service": "spotify",
                    "timestamp": timestamp,
                }

                if platform.lower() != "spotify":
                    # Dynamically determine the base URL for the /api/search endpoint
                    base_url = url_for("main.index", _external=True).rstrip("/")
                    search_query = f"{fetched_dict.get('artists', '')}:{fetched_dict.get('title', '')}"
                    from urllib.parse import quote

                    search_url = (
                        f"{base_url}/api/search/{quote(search_query)}?{platform}"
                    )

                    # Call the /api/search endpoint using requests
                    try:
                        response = requests.get(
                            search_url, params={"all": ""}, timeout=10
                        )
                        response.raise_for_status()
                        data = response.json()
                        if not data.get("error"):
                            # Preserve activity_info when replacing music_info
                            activity["music_info"] = data
                    except (requests.RequestException, ValueError) as e:
                        logger.warning(e)
                        # Keep original Spotify data on error

                # Sort the activity by keys
                activity = dict(sorted(activity.items()))

                # Save the current activity to the database
                UserData.insert_or_update_user_data(spotify_service, activity)
                return activity
            else:
                # Fetch the last activity from the database if no current activity is found
                existing_data = db.session.scalar(
                    sa.select(UserData).where(
                        UserData.user_service_id == spotify_service.id
                    )
                )
                if existing_data:
                    activity_data = existing_data.data or {}
                    if "activity_info" not in activity_data:
                        activity_data["activity_info"] = {}
                    activity_data["activity_info"]["is_playing"] = False
                    if not activity_data.get("activity_info", {}).get("timestamp"):
                        if "activity_info" not in activity_data:
                            activity_data["activity_info"] = {}
                        activity_data["activity_info"][
                            "timestamp"
                        ] = existing_data.updated_at.timestamp()
                        activity_data["activity_info"]["service"] = "spotify"

                    # Update the activity in the database
                    UserData.insert_or_update_user_data(spotify_service, activity_data)
                    return activity_data

            return None
    except SpotifyAuthException:
        flash(
            SPOTIFY_AUTH_NOT_AVAILABLE,
            "error",
        )
        return redirect(url_for(USER_SETTINGS_ENDPOINT, username=current_user.username))
