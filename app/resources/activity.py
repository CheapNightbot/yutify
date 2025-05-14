import os
import random

import sqlalchemy as sa
from flask import abort, make_response, render_template, request
from flask_restful import Resource
from flask_security import current_user

from app import db
from app.auth_services.lastfm import get_lastfm_activity
from app.auth_services.spotify import get_spotify_activity
from app.limiter import limiter
from app.models import UserService

RATELIMIT = os.environ.get("RATELIMIT")


class UserActivityResource(Resource):

    @limiter.limit(RATELIMIT if RATELIMIT else "")
    def get(self):
        """Fetch the currently playing music for the authenticated user."""
        response_type = request.args.get("type", "json").lower()
        service = "".join(list(request.args.keys())).lower() if request.args else "all"

        # Fetch user services from the database
        user_services = db.session.scalars(
            sa.select(UserService).where(UserService.user_id == current_user.id)
        ).all()

        if not user_services:
            return {
                "error": "No service is linked. Please link one in your settings."
            }, 404

        # Determine which services are linked
        linked_services = {
            service.service.name.lower(): service for service in user_services
        }

        # Fetch activity from each service
        spotify_activity = (
            get_spotify_activity if "spotify" in linked_services else None
        )
        lastfm_activity = get_lastfm_activity if "lastfm" in linked_services else None

        # Determine which activity to return
        activity = None
        # Prioritize Spotify or Last.fm based on query parameter
        match service:
            case "spotify":
                activity = spotify_activity() if spotify_activity else None
            case "lastfm":
                activity = lastfm_activity() if lastfm_activity else None
            case _:
                activity = self._fetch_activity(spotify_activity, lastfm_activity)

        if not activity:
            return {
                "error": "No activity found. Listen to music on your linked service to see it here."
            }, 404

        return self._format_response(activity, response_type)

    def _format_response(self, activity, response_type):
        """Format the response based on the requested type."""

        # Handle different response types
        if response_type == "html":
            if not current_user.is_authenticated:
                abort(400)
            html = render_template("user/activity_embed.html", activity=activity)
            return make_response(html, 200, {"Content-Type": "text/html"})

        return activity  # defualt // json

    def _fetch_activity(self, spotify_activity_func, lastfm_activity_func):
        """
        Fetch and prioritize activity from Spotify and Last.fm.

        Parameters
        ----------
        spotify_activity_func (callable)
            Function to fetch Spotify activity.
        lastfm_activity_func (callable)
            Function to fetch Last.fm activity.

        Returns
        -------
        dict
            The selected activity or None if no activity is found.
        """

        spotify_activity = spotify_activity_func() if spotify_activity_func else None
        lastfm_activity = lastfm_activity_func() if lastfm_activity_func else None

        if spotify_activity and lastfm_activity:
            return random.choice([spotify_activity, lastfm_activity])
        elif spotify_activity:
            return spotify_activity
        elif lastfm_activity:
            return lastfm_activity

        return None
