import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from dotenv import load_dotenv
from flask import Flask, current_app
from flask_caching import Cache
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_security import hash_password
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_mailman import Mail

from app.common.utils import mask_string, relative_timestamp
from config import Config

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
api = Api()
cors = CORS()
cache = Cache()
csrf = CSRFProtect()
mail = Mail()


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
        if app.config.get("MAIL_SERVER"):
            auth = None
            if app.config.get("MAIL_USERNAME") or app.config.get("MAIL_PASSWORD"):
                auth = (app.config.get("MAIL_USERNAME"), app.config.get("MAIL_PASSWORD"))
            secure = None
            if app.config.get("MAIL_USE_TLS"):
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config.get("MAIL_SERVER"), app.config.get("MAIL_PORT")),
                fromaddr="no-reply@" + app.config.get("MAIL_SERVER"),
                toaddrs=app.config.get("ADMIN_EMAIL"),
                subject="yutify Failure",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config.get("LOG_TO_STDOUT"):
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
    mail.init_app(app)
    # csrf.init_app(app)
    api.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.resources import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # from app.auth import bp as auth_bp
    # app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.auth_services import bp as auth_services_bp
    app.register_blueprint(auth_services_bp, url_prefix="/auth_services")

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.docs import bp as docs_bp
    app.register_blueprint(docs_bp, url_prefix="/docs")

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix="/u")

    app.jinja_env.filters["mask_string"] = mask_string
    app.jinja_env.filters["relative_timestamp"] = relative_timestamp

    # Configure caching
    if not app.debug:
        if app.config.get("REDIS_URI"):
            app.config["CACHE_TYPE"] = "RedisCache"
            app.config["CACHE_REDIS_URL"] = app.config.get("REDIS_URI")
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
    if app.config.get("RATELIMIT"):
        app.logger.info(f"Ratelimit set to {app.config["RATELIMIT"]}.")
    else:
        app.logger.info("Ratelimit is disabled.")

    from app.limiter import limiter

    limiter.init_app(app)

    return app


# Create users and roles (and first blog!)
def create_users():
    if current_app.testing:
        return
    with current_app.app_context():
        security = current_app.security
        security.datastore.db.create_all()

        # Create default roles and permissions
        security.datastore.find_or_create_role(
            name="admin",
            permissions=sorted({"admin-read", "admin-write", "user-read", "user-write"}),
        )
        security.datastore.find_or_create_role(
            name="user", permissions=sorted({"user-read", "user-write"})
        )

        # Create default admin user
        admin_user = security.datastore.find_user(
            username="admin"
        ) or security.datastore.find_user(email=current_app.config.get("ADMIN_EMAIL"))
        if not admin_user:
            admin_user = security.datastore.create_user(
                name="Admin",
                username="admin",
                email=current_app.config["ADMIN_EMAIL"],
                password=hash_password("password"),
                roles=["admin"],
            )
        admin_user.set_avatar()

        security.datastore.db.session.commit()


from app import models
