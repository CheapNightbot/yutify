from dataclasses import asdict

import sqlalchemy as sa
from flask import flash, redirect, url_for
from flask_login import current_user
from yutipy.lastfm import LastFm

from app import db
from app.models import Service, UserData, UserService


def handle_lastfm_auth(lastfm_username):
    """Handle linking Last.fm by saving the username."""
    if not lastfm_username:
        flash("Last.fm username is required.", "error")
        return redirect(url_for("user.user_settings", username=current_user.username))

    # Fetch the service dynamically by name
    service = db.session.scalar(
        sa.select(Service).where(Service.service_name.ilike("lastfm"))
    )
    if not service:
        flash("Service 'Last.fm' not found in the database.", "error")
        return redirect(url_for("user.user_settings", username=current_user.username))

    # Check if the UserService entry already exists
    user_service = db.session.scalar(
        sa.select(UserService)
        .where(UserService.user_id == current_user.user_id)
        .where(UserService.service_id == service.service_id)
    )

    if user_service:
        flash("You have already linked Last.fm.", "success")
    else:
        # Create a new entry for Last.fm
        user_service = UserService(
            user_id=current_user.user_id,
            service_id=service.service_id,
            username=lastfm_username,
        )
        db.session.add(user_service)
        db.session.commit()
        flash("Successfully linked Last.fm!", "success")

    return redirect(url_for("user.user_settings", username=current_user.username))


def get_lastfm_activity():
    """Fetch the user's listening activity from Last.fm."""
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

    lastfm = LastFm()
    activity = lastfm.get_currently_playing(username=lastfm_service.username)
    if activity:
        data = asdict(activity)
        activity.is_playing = False
        # Save the current activity to the database
        UserData.insert_or_update_user_data(
            lastfm_service.user_services_id, asdict(activity)
        )
        return data
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
