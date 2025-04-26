from dataclasses import asdict

import sqlalchemy as sa
from flask import flash, redirect, session, url_for
from flask_login import current_user
from yutipy.spotify import SpotifyAuth, SpotifyAuthException

from app import db
from app.models import Service, User, UserData, UserService


# Over-ride `save_access_token` and `load_access_token` methods ~
class MySpotifyAuth(SpotifyAuth):
    def __init__(self, user=None, *args, **kwargs):
        self.user = user  # Set user before calling super().__init__
        super().__init__(*args, **kwargs, defer_load=True)  # Defer token loading

    def save_access_token(self, token_info: dict) -> None:
        user = db.session.scalar(
            sa.select(User).where(User.username == self.user.username)
        )

        if user:
            # Fetch the service dynamically by name
            service = db.session.scalar(
                sa.select(Service).where(Service.service_name.ilike("spotify"))
            )
            if not service:
                raise ValueError("Service 'Spotify' not found in the database.")

            # Check if the UserService entry already exists
            user_service = db.session.scalar(
                sa.select(UserService)
                .where(UserService.user_id == user.user_id)
                .where(UserService.service_id == service.service_id)
            )

            if user_service:
                # Update the existing entry
                user_service.access_token = token_info.get("access_token")
                user_service.refresh_token = token_info.get("refresh_token")
                user_service.expires_in = token_info.get("expires_in")
                user_service.requested_at = token_info.get("requested_at")
            else:
                # Create a new entry if it doesn't exist
                user_service = UserService(
                    access_token=token_info.get("access_token"),
                    refresh_token=token_info.get("refresh_token"),
                    expires_in=token_info.get("expires_in"),
                    requested_at=token_info.get("requested_at"),
                )
                user_service.service = service
                user_service.user = user
                db.session.add(user_service)

            db.session.commit()

    def load_access_token(self) -> dict | None:
        user_service = db.session.scalar(
            sa.select(UserService).where(UserService.user_id == self.user.user_id)
        )

        if user_service:
            return {
                "access_token": user_service.access_token,
                "refresh_token": user_service.refresh_token,
                "expires_in": user_service.expires_in,
                "requested_at": user_service.requested_at,
            }


spotify_auth = MySpotifyAuth(scopes=["user-read-currently-playing"])


def handle_spotify_auth():
    spotify_auth.user = current_user
    spotify_auth.load_token_after_init()  # Explicitly load the token after initialization

    # Fetch the service dynamically by name
    service = db.session.scalar(
        sa.select(Service).where(Service.service_name.ilike("spotify"))
    )
    if not service:
        flash("Service 'Spotify' not found in the database.", "error")
        return redirect(url_for("user.user_settings", username=current_user.username))

    user_service = db.session.scalar(
        sa.select(UserService)
        .where(UserService.user_id == current_user.user_id)
        .where(UserService.service_id == service.service_id)
    )

    if user_service:
        flash("You have already linked Spotify.", "success")
        spotify_auth.close_session()
        return redirect(url_for("user.user_settings", username=current_user.username))

    state = spotify_auth.generate_state()
    session["state"] = state
    auth_url = spotify_auth.get_authorization_url(state=state, show_dialog=True)

    return redirect(auth_url)


def handle_spotify_callback(request):
    spotify_auth.user = current_user
    spotify_auth.load_token_after_init()  # Explicitly load the token after initialization

    code = request.args.get("code")
    state = request.args.get("state")
    expected_state = session.get("state")

    if not code or not state:
        flash(
            "Authorization canceled. It seems you chose not to grant access to your Spotify account.",
            "error",
        )
        session.pop("state")

        spotify_auth.close_session()
        return redirect(url_for("user.user_settings", username=current_user.username))

    try:
        spotify_auth.callback_handler(code, state, expected_state)
    except SpotifyAuthException:
        flash("Something went wrong while authenticating with Spotify.", "error")
        session.pop("state")

        spotify_auth.close_session()
        return redirect(url_for("user.user_settings", username=current_user.username))

    flash("Successfully linked Spotify!", "success")
    session.pop("state")

    return redirect(url_for("user.user_settings", username=current_user.username))


def get_spotify_activity():
    """Fetch the user's listening activity from Spotify."""
    spotify_service = db.session.scalar(
        sa.select(UserService)
        .join(Service)
        .where(
            UserService.user_id == current_user.user_id,
            Service.service_name.ilike("spotify"),
        )
    )

    if not spotify_service:
        return None

    spotify_auth.user = current_user
    spotify_auth.load_token_after_init()  # Explicitly load the token after initialization
    activity = spotify_auth.get_currently_playing()
    if activity:
        data = asdict(activity)
        activity.is_playing = False
        # Save the current activity to the database
        UserData.insert_or_update_user_data(
            spotify_service.user_services_id, asdict(activity)
        )
        return data
    else:
        # Fetch the last activity from the database if no current activity is found
        existing_data = db.session.scalar(
            sa.select(UserData).where(
                UserData.user_service_id == spotify_service.user_services_id
            )
        )
        if existing_data:
            return existing_data.data

    return None
