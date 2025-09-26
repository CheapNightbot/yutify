import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from app import db
from app.auth_services.lastfm import get_lastfm_activity
from app.auth_services.spotify import get_spotify_activity
from app.models import UserService

logger = logging.getLogger(__name__)

ACTIVITY_UPDATE_INTERVAL = 5  # in minutes


def update_all_user_activities(app):
    with app.app_context():
        started = time.time()
        logger.info("[ActivityUpdater] Starting scheduled user activity update...")
        user_services = db.session.query(UserService).all()

        for user_service in user_services:
            user = user_service.user
            service = user_service.service.name.lower()
            try:
                if service == "spotify":
                    get_spotify_activity(user)
                elif service == "lastfm":
                    get_lastfm_activity(user)

                time.sleep(2)  # Stagger requests to avoid bursts
            except Exception as e:
                logger.error(
                    f"[ActivityUpdater] Error updating {service} for {user.username}: {e}"
                )

        total_time = time.time() - started
        minutes, seconds = divmod(total_time, 60)
        logger.info(
                f"Activity update took: {int(minutes)} minutes and {seconds:.2f} seconds."
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
    logger.info("[ActivityUpdater] Scheduler started.")
