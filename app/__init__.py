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

from app.common.logger import logger
from app.common.utils import mask_string
from config import Config

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
mail = Mail()
api = Api()
cors = CORS()
cache = Cache()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure caching
    redis_url = os.getenv("REDIS_URI")
    if not app.debug:
        if redis_url:
            app.config["CACHE_TYPE"] = "RedisCache"
            app.config["CACHE_REDIS_URL"] = redis_url
            logger.info("Caching is enabled. Using redis for cache.")
        else:
            app.config["CACHE_TYPE"] = "null"
            logger.info("Redis URI was not set. Caching is disabled.")
    else:
        app.config["CACHE_TYPE"] = (
            "SimpleCache"  # Use in-memory cache for local development
        )
        logger.warning("Redis URI was not set. Using in-memory cache.")
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # Cache timeout in seconds (5 minutes)
    cache.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    api.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from app.resources.limiter import limiter
    limiter.init_app(app)

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

            if not os.path.exists("logs"):
                os.mkdir("logs")
            file_handler = RotatingFileHandler(
                "logs/yutify.log", maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info("yutify startup")

    return app


from app import models
