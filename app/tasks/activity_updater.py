import time
from apscheduler.schedulers.background import BackgroundScheduler

from app import db
from app.auth_services.lastfm import get_lastfm_activity
from app.auth_services.spotify import get_spotify_activity
from app.models import UserService

ACTIVITY_UPDATE_INTERVAL = 2  # in minutes


def update_all_user_activities(app):
    with app.app_context():
        print("[ActivityUpdater] Starting scheduled user activity update...")
        user_services = db.session.query(UserService).all()
        for user_service in user_services:
            user = user_service.user
            service = user_service.service.name.lower()
            try:
                if service == "spotify":
                    get_spotify_activity(user, force_refresh=True)
                elif service == "lastfm":
                    get_lastfm_activity(user, force_refresh=True)
                time.sleep(2)  # Stagger requests to avoid bursts
            except Exception as e:
                print(
                    f"[ActivityUpdater] Error updating {service} for {user.username}: {e}"
                )


def start_activity_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_all_user_activities,
        "interval",
        minutes=ACTIVITY_UPDATE_INTERVAL,
        args=[app],
    )
    scheduler.start()
    print("[ActivityUpdater] Scheduler started.")
    # Run immediately on startup
    update_all_user_activities(app)
