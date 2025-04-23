import sqlalchemy as sa
from flask import flash, jsonify, redirect, session, url_for
from flask_login import current_user
from yutipy.spotify import SpotifyAuth, SpotifyAuthException

from app import db
from app.models import Service, User, UserService


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
            service = db.session.get(Service, 1)
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

    user_service = db.session.scalar(
        sa.select(UserService).where(UserService.user_id == current_user.user_id)
    )

    if user_service:
        flash(f"You have already linked Spotify.", "success")
        spotify_auth.close_session()
        return redirect(url_for("user.user_settings", username=current_user.username))

    state = spotify_auth.generate_state()
    session["state"] = state
    auth_url = spotify_auth.get_authorization_url(state=state)

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
