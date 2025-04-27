import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from dotenv import load_dotenv
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from app.common.utils import mask_string
from config import Config

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message_category = "error"
mail = Mail()
api = Api()
cors = CORS()
cache = Cache()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set up global logging configuration
    logging.basicConfig(
        format="[{asctime}] [{levelname:<7}] {filename}: {message}",
        datefmt="%Y, %b %d ~ %I:%M:%S %p",
        style="{",
        level=logging.CRITICAL,
        encoding="utf-8",
    )
    root_logger = logging.getLogger()

    if not app.debug and not app.testing:
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr="no-reply@" + app.config["MAIL_SERVER"],
                toaddrs=app.config["ADMIN_EMAIL"],
                subject="yutify Failure",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config["LOG_TO_STDOUT"]:
            root_logger.setLevel(logging.INFO)
        else:
            # Remove default console handler if it exists
            for handler in root_logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    root_logger.removeHandler(handler)

            if not os.path.exists("logs"):
                os.mkdir("logs")
            file_handler = RotatingFileHandler(
                "logs/yutify.log", maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    fmt="[{asctime}] [{levelname:<7}] {filename}: {message}",
                    datefmt="%Y, %b %d ~ %I:%M:%S %p",
                    style="{",
                )
            )
            root_logger.addHandler(file_handler)

        root_logger.info("yutify startup")

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    api.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from app.resources import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.auth_services import bp as auth_services_bp
    app.register_blueprint(auth_services_bp, url_prefix="/auth_services")

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix="/u")

    app.jinja_env.filters["mask_string"] = mask_string

    # Configure caching
    redis_url = os.getenv("REDIS_URI")
    if not app.debug:
        if redis_url:
            app.config["CACHE_TYPE"] = "RedisCache"
            app.config["CACHE_REDIS_URL"] = redis_url
            app.logger.info("Caching is enabled. Using redis for cache.")
        else:
            app.config["CACHE_TYPE"] = "NullCache"
            app.config["CACHE_NO_NULL_WARNING"] = True
            app.logger.info("Redis URI was not set. Caching is disabled.")
    else:
        app.config["CACHE_TYPE"] = (
            "SimpleCache"  # Use in-memory cache for local development
        )
        app.logger.warning("Redis URI was not set. Using in-memory cache.")
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # Cache timeout in seconds (5 minutes)
    cache.init_app(app)

    # Configure Rate Limiting
    RATELIMIT = os.environ.get("RATELIMIT")
    if RATELIMIT:
        app.logger.info(f"Ratelimit set to {RATELIMIT}.")
    else:
        app.logger.info("Ratelimit is disabled.")

    from app.limiter import limiter
    limiter.init_app(app)

    return app


from app import models
