import os
import random

import sqlalchemy as sa
from authlib.integrations.flask_oauth2 import current_token
from flask import current_app, make_response, render_template, request
from flask_restful import Resource
from flask_security import Security, SQLAlchemyUserDatastore, current_user

from app import db
from app.auth_services.lastfm import get_lastfm_activity
from app.auth_services.spotify import get_spotify_activity
from app.common.helpers import get_album_art_data_uri, get_static_file_data_uri
from app.limiter import limiter
from app.models import UserService
import cairosvg
import io

RATELIMIT = os.environ.get("RATELIMIT")


class UserActivityResource(Resource):

    @limiter.limit(RATELIMIT if RATELIMIT else "")
    def get(self):
        """Fetch the currently playing music for the authenticated user."""
        username = request.args.get("username", "").strip().lower()
        security: Security = current_app.security
        datastore: SQLAlchemyUserDatastore = security.datastore

        if username:
            # If a username is provided, fetch the user by username
            user = datastore.find_user(username=username)
            # If user not found or profile is private
            if not user or not user.is_profile_public:
                if current_user.is_authenticated or current_token:
                    # If the user is authenticated or has a valid OAuth token, allow access
                    return {"error": "User not found or profile is private."}, 404
                else:
                    # User must be authenticated or OAuth token must be valid
                    return {
                        "error": "Authentication required. Please log in or provide a valid OAuth token."
                    }, 401
        else:
            # Otherwise, use the current user or the user from the OAuth token
            user = (
                current_user
                if current_user.is_authenticated
                else current_token.user if current_token else None
            )
            if not user:
                # User must be authenticated or OAuth token must be valid
                return {
                    "error": "Authentication required. Please log in or provide a valid OAuth token."
                }, 401

        response_type = request.args.get("type", "json").lower()
        service = "".join(list(request.args.keys())).lower() if request.args else "all"
        is_embed = "embed" in request.args
        is_svg = "svg" in request.args
        is_png = request.path.endswith(".png")

        favicon_data_uri = get_static_file_data_uri("favicon.svg", "image/svg+xml")
        no_gif_data_uri = get_static_file_data_uri("errors/no.gif", "image/gif")
        no_png_data_uri = get_static_file_data_uri("errors/no.png", "image/png")

        # Fetch user services from the database
        user_services = db.session.scalars(
            sa.select(UserService).where(UserService.user_id == user.id)
        ).all()

        if not user_services:
            error_msg = (
                "No service is linked. Please link one in your settings."
                if user == current_user
                else f"{user.name} is not listening to anything right now..."
            )
            if is_embed:
                return make_response(
                    render_template(
                        "embed/activity_card.html", error=error_msg, user=user
                    ),
                    200,
                    {"Content-Type": "text/html"},
                )
            if is_svg:
                return make_response(
                    render_template(
                        "embed/activity_card.svg.j2",
                        error=error_msg,
                        user=user,
                        no_gif_data_uri=no_gif_data_uri,
                    ),
                    200,
                    {"Content-Type": "image/svg+xml"},
                )
            if is_png:
                # Render SVG first
                svg_str = render_template(
                    "embed/activity_card.svg.j2",
                    error=error_msg,
                    user=user,
                    no_gif_data_uri=no_png_data_uri,
                )
                # Convert SVG to PNG
                png_bytes = cairosvg.svg2png(bytestring=svg_str.encode("utf-8"))
                return make_response(
                    png_bytes,
                    200,
                    {"Content-Type": "image/png"},
                )

            return {"error": error_msg}, 404

        # Determine which services are linked
        linked_services = {
            service.service.name.lower(): service for service in user_services
        }

        # Fetch activity from each service
        spotify_activity = (
            (lambda: get_spotify_activity(user))
            if "spotify" in linked_services
            else None
        )
        lastfm_activity = (
            (lambda: get_lastfm_activity(user)) if "lastfm" in linked_services else None
        )

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
            error_msg = (
                "No activity found. Listen to music on your linked service to see it here."
                if user == current_user
                else f"{user.name} is not listening to anything right now..."
            )
            if is_embed:
                return make_response(
                    render_template(
                        "embed/activity_card.html", error=error_msg, user=user
                    ),
                    200,
                    {"Content-Type": "text/html"},
                )
            if is_svg:
                return make_response(
                    render_template(
                        "embed/activity_card.svg.j2",
                        error=error_msg,
                        user=user,
                        no_gif_data_uri=no_gif_data_uri,
                    ),
                    200,
                    {"Content-Type": "image/svg+xml"},
                )
            if is_png:
                # Render SVG first
                svg_str = render_template(
                    "embed/activity_card.svg.j2",
                    error=error_msg,
                    user=user,
                    no_gif_data_uri=no_png_data_uri,
                )
                # Convert SVG to PNG
                png_bytes = cairosvg.svg2png(bytestring=svg_str.encode("utf-8"))
                return make_response(
                    png_bytes,
                    200,
                    {"Content-Type": "image/png"},
                )

            return {"error": error_msg}, 404

        if is_embed:
            return make_response(
                render_template(
                    "embed/activity_card.html", activity=activity, user=user
                ),
                200,
                {"Content-Type": "text/html"},
            )

        if is_svg:
            album_art_data_uri = None
            if activity and "album_art" in activity.get("music_info", {}):
                album_art_data_uri = get_album_art_data_uri(
                    activity["music_info"]["album_art"]
                )
            return make_response(
                render_template(
                    "embed/activity_card.svg.j2",
                    activity=activity,
                    user=user,
                    album_art_data_uri=album_art_data_uri,
                    favicon_data_uri=favicon_data_uri,
                ),
                200,
                {"Content-Type": "image/svg+xml"},
            )

        if is_png:
            # Render SVG first
            album_art_data_uri = None
            if activity and "album_art" in activity.get("music_info", {}):
                album_art_data_uri = get_album_art_data_uri(
                    activity["music_info"]["album_art"]
                )
            svg_str = render_template(
                "embed/activity_card.svg.j2",
                activity=activity,
                user=user,
                album_art_data_uri=album_art_data_uri,
                favicon_data_uri=favicon_data_uri,
            )
            # Convert SVG to PNG
            png_bytes = cairosvg.svg2png(bytestring=svg_str.encode("utf-8"))
            return make_response(
                png_bytes,
                200,
                {"Content-Type": "image/png"},
            )

        return self._format_response(activity, response_type)

    def _get_static_file_bytes(self, rel_path):
        """Helper to load a static file as bytes from the static folder."""
        static_folder = os.path.join(current_app.root_path, "static")
        file_path = os.path.join(static_folder, rel_path)
        with open(file_path, "rb") as f:
            return f.read()

    def _format_response(self, activity, response_type):
        """Format the response based on the requested type."""
        # Only allow HTML response for authenticated users (not OAuth2) and AJAX requests
        if response_type == "html":
            if request.headers.get("X-Requested-With") != "XMLHttpRequest":
                # Fallback to default JSON response if not allowed
                return activity
            html = render_template("user/activity_embed.html", activity=activity)
            return make_response(html, 200, {"Content-Type": "text/html"})
        return activity  # default // json

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
