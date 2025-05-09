import os

from dotenv import load_dotenv
from flask_security.utils import uia_username_mapper

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
APP = "yutify"


class Config:
    REDIS_URI = os.getenv("REDIS_URI")
    RATELIMIT = os.environ.get("RATELIMIT")

    # SESSION_COOKIE_SECURE = True
    # SESSION_COOKIE_HTTPONLY = True
    # REMEMBER_COOKIE_SAMESITE = "strict"
    # SESSION_COOKIE_SAMESITE = "strict"

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MAIL_SERVER = os.environ.get("MAIL_SERVER")
    # MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    # MAIL_USE_TLS = bool(os.environ.get("MAIL_USE_TLS", 0))
    # MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    # MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    PORT = os.environ.get("PORT", 5000)
    LOG_TO_STDOUT = bool(os.environ.get("LOG_TO_STDOUT", 0))

    # Flask-Security specific (and not specific as well) configs ~
    # https://flask-security.readthedocs.io/en/stable/configuration.html
    # ### Core ###
    SECRET_KEY = os.environ.get("SECRET_KEY", "senpai-likes-small-potatoes")
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "potatoes").encode()
    SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": False}
    # # SECURITY_CSRF_COOKIE_NAME = "XSRF-TOKEN"
    # SECURITY_EMAIL_SENDER = "no-reply@localhost"
    # SECURITY_RETURN_GENERIC_RESPONSES = True
    SECURITY_USER_IDENTITY_ATTRIBUTES = [
        {"username": {"mapper": uia_username_mapper, "case_insensitive": True}},
    ]

    # # ### Core - Passwords and Tokens ###
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", "6663629")
    SECURITY_PASSWORD_LENGTH_MIN = 8
    SECURITY_PASSWORD_COMPLEXITY_CHECKER = "zxcvbn"

    # # ### Core - Multi-factor ###
    SECURITY_TOTP_SECRETS = {1: os.environ.get("SECURITY_TOTP_SECRETS")}
    SECURITY_TOTP_ISSUER = APP

    # # ### Core - rarely need changing ###
    # SECURITY_CLI_USERS_NAME = False
    # SECURITY_CLI_ROLES_NAME = False

    # # ### Login/Logout ###
    # SECURITY_LOGOUT_METHODS = ["POST"]
    SECURITY_POST_LOGIN_VIEW = "auth.login"
    SECURITY_POST_LOGOUT_VIEW = "auth.logout"
    # # SECURITY_UNAUTHORIZED_VIEW = callable !!
    # SECURITY_LOGIN_USER_TEMPLATE = "auth/login.html"
    # # SECURITY_VERIFY_TEMPLATE = "verify.html" !

    # # ### Registerable ###
    SECURITY_REGISTERABLE = bool(os.environ.get("ALLOW_SIGNUP", 0))
    SECURITY_SEND_REGISTER_EMAIL = False
    # SECURITY_REGISTER_USER_TEMPLATE = "auth/signup.html"
    SECURITY_REGISTER_URL = "/signup"
    SECURITY_USERNAME_ENABLE = True
    # SECURITY_MSG_USERNAME_DISALLOWED_CHARACTERS = (
    #     "Username can contain only letters, numbers and hyphen (-)",
    #     "error",
    # )
    SECURITY_USERNAME_REQUIRED = True
    SECURITY_USE_REGISTER_V2 = True

    # # ### Changeable ###
    # #

    # # ### Recoverable ###
    SECURITY_RECOVERABLE = True
    SECURITY_RESET_URL = "/reset-password"
    # # SECURITY_RESET_PASSWORD_TEMPLATE = "reset_password.html"
    # # SECURITY_FORGOT_PASSWORD_TEMPLATE = "forgot_password.html"

    # # ### Two-Factor ###
    SECURITY_TWO_FACTOR = True
    SECURITY_TWO_FACTOR_REQUIRED = False
    SECURITY_TWO_FACTOR_ENABLED_METHODS = ["email", "authenticator"]
    # SECURITY_TWO_FACTOR_RESCUE_MAIL = ADMIN_EMAIL
    # # SECURITY_TWO_FACTOR_VERIFY_CODE_TEMPLATE = "two_factor_verify_code.html"
    # # SECURITY_TWO_FACTOR_SETUP_TEMPLATE = "two_factor_setup.html"
    SECURITY_TWO_FACTOR_IMPLEMENTATIONS = {
        "code": "flask_security.twofactor.CodeTfPlugin"
    }

    # # ### Change Username ###
    SECURITY_CHANGE_USERNAME = True
    # # SECURITY_POST_CHANGE_USERNAME_VIEW = "user_settings" or maybe "user_profile" ?
    # SECURITY_CHANGE_USERNAME_TEMPLATE = "chanage_username.html"

    # # ### Recovery Codes ###
    SECURITY_MULTI_FACTOR_RECOVERY_CODES = True
    # # SECURITY_MULTI_FACTOR_RECOVERY_CODES_TEMPLATE = "mf_recovery_codes.html"
    # # SECURITY_MULTI_FACTOR_RECOVERY_TEMPLATE = "mf_recovery.html"
    SECURITY_MULTI_FACTOR_RECOVERY_CODES_KEYS = [ENCRYPTION_KEY]
