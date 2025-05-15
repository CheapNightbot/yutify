import os
from datetime import timedelta
from dotenv import load_dotenv
from flask_security.utils import uia_username_mapper

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SERVICE = os.getenv("SERVICE", "yutify")
    HOST_URL = os.getenv("HOST_URL", "localhost")
    REDIS_URI = os.getenv("REDIS_URI")
    RATELIMIT = os.getenv("RATELIMIT")
    YUTIFY_MAIL_ERROR_LOGS = bool(int(os.getenv("YUTIFY_MAIL_ERROR_LOGS", False)))
    YUTIFY_ACCOUNT_DELETE_EMAIL = bool(
        int(os.getenv("YUTIFY_ACCOUNT_DELETE_EMAIL", True))
    )

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "strict"
    REMEMBER_COOKIE_SAMESITE = "strict"

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///" + os.path.join(
        basedir, "app.db"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_DEBUG = False
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT") or 25)
    MAIL_USE_TLS = bool(os.getenv("MAIL_USE_TLS", True))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    PORT = os.getenv("PORT", 5000)
    LOG_TO_STDOUT = bool(int(os.getenv("LOG_TO_STDOUT", True)))

    # Flask-Security specific (and not specific as well) configs ~
    # https://flask-security.readthedocs.io/en/stable/configuration.html
    # ### Core ###
    SECRET_KEY = os.getenv("SECRET_KEY")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
    SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": True}
    SECURITY_USER_IDENTITY_ATTRIBUTES = [
        {"username": {"mapper": uia_username_mapper, "case_insensitive": True}},
    ]
    SECURITY_RETURN_GENERIC_RESPONSES = True
    SECURITY_FRESHNESS = timedelta(minutes=10)
    SECURITY_FRESHNESS_GRACE_PERIOD = timedelta(minutes=5)

    # ### Core - Passwords and Tokens ###
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    SECURITY_PASSWORD_LENGTH_MIN = 16
    SECURITY_PASSWORD_COMPLEXITY_CHECKER = "zxcvbn"
    SECURITY_PASSWORD_CONFIRM_REQUIRED = True

    # ### Core - Multi-factor ###
    SECURITY_TOTP_SECRETS = {1: os.getenv("SECURITY_TOTP_SECRETS")}
    SECURITY_TOTP_ISSUER = SERVICE

    # ### Core - rarely need changing ###
    SECURITY_CLI_USERS_NAME = False
    SECURITY_CLI_ROLES_NAME = False

    # ### Login/Logout ###
    SECURITY_POST_LOGIN_VIEW = "auth.login"
    SECURITY_POST_LOGOUT_VIEW = "auth.logout"

    # ### Registerable ###
    SECURITY_REGISTERABLE = bool(int(os.getenv("SECURITY_REGISTERABLE", False)))
    print(SECURITY_REGISTERABLE)
    SECURITY_EMAIL_SUBJECT_REGISTER = f"[{SERVICE}] Verify Email Address!"
    SECURITY_POST_REGISTER_VIEW = "main.index"
    SECURITY_REGISTER_URL = "/signup"
    SECURITY_USERNAME_ENABLE = True
    SECURITY_MSG_USERNAME_DISALLOWED_CHARACTERS = (
        "Username can contain only letters, numbers and hyphen (-)",
        "error",
    )
    SECURITY_USERNAME_REQUIRED = True
    SECURITY_USE_REGISTER_V2 = True

    # ### Confirmable ###
    SECURITY_CONFIRMABLE = True
    SECURITY_CONFIRM_URL = "/verify-email"
    SECURITY_EMAIL_SUBJECT_CONFIRM = f"[{SERVICE}] Verify Email Address!"
    SECURITY_POST_CONFIRM_VIEW = "auth.email_verified"

    # ### Changeable
    SECURITY_CHANGEABLE = True
    SECURITY_CHANGE_URL = "/change-password"
    SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE = (
        f"[{SERVICE}] You password has been changed!"
    )

    # ### Recoverable ###
    SECURITY_RECOVERABLE = True
    SECURITY_RESET_URL = "/reset-password"

    # ### Change-Email ###
    SECURITY_CHANGE_EMAIL = True
    SECURITY_CHANGE_EMAIL_SUBJECT = f"[{SERVICE}] Confirm your new email address!"
    SECURITY_POST_CHANGE_EMAIL_VIEW = "user.email_changed"
    SECURITY_CHANGE_EMAIL_ERROR_VIEW = "user.email_changed"

    # ### Two-Factor ###
    SECURITY_TWO_FACTOR = True
    SECURITY_TWO_FACTOR_REQUIRED = False
    SECURITY_TWO_FACTOR_ENABLED_METHODS = ["authenticator"]
    # SECURITY_TWO_FACTOR_RESCUE_MAIL = ADMIN_EMAIL
    SECURITY_EMAIL_SUBJECT_TWO_FACTOR = f"[{SERVICE}] Your Code for Two-Factor Login!"
    SECURITY_EMAIL_SUBJECT_TWO_FACTOR_RESCUE = (
        f"[{SERVICE}] Two-Factor Authentication Reset Request!"
    )
    SECURITY_TWO_FACTOR_RESCUE_URL = "/tf-recovery"
    SECURITY_TWO_FACTOR_IMPLEMENTATIONS = {
        "code": "flask_security.twofactor.CodeTfPlugin"
    }
    SECURITY_TWO_FACTOR_RESCUE_EMAIL = False

    # ### Username-Recovery ###
    SECURITY_USERNAME_RECOVERY = True
    SECURITY_EMAIL_SUBJECT_USERNAME_RECOVERY = f"[{SERVICE}] Username Recovery Request!"

    # ### Change Username ###
    SECURITY_CHANGE_USERNAME = True
    SECURITY_POST_CHANGE_USERNAME_VIEW = "user.username_changed"
    SECURITY_EMAIL_SUBJECT_USERNAME_CHANGE_NOTICE = (
        f"[{SERVICE}] Your username has been changed!"
    )

    # ### Recovery Codes ###
    SECURITY_MULTI_FACTOR_RECOVERY_CODES = True
    SECURITY_MULTI_FACTOR_RECOVERY_CODES_KEYS = [ENCRYPTION_KEY]
