import os
from dotenv import load_dotenv
from flask_security.utils import uia_username_mapper

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SERVICE = os.getenv("SERVICE", "yutify")
    SERVICE_EMAIL = os.getenv("SERVICE_EMAIL", "hi@example.com")
    HOST_URL = os.getenv("HOST_URL", "localhost")
    SERVER_NAME = HOST_URL
    PREFERRED_URL_SCHEME = "https" if "localhost" not in HOST_URL else "http"
    REDIS_URI = os.getenv("REDIS_URI")
    RATELIMIT = os.getenv("RATELIMIT")
    YUTIFY_MAIL_ERROR_LOGS = bool(int(os.getenv("YUTIFY_MAIL_ERROR_LOGS", False)))
    YUTIFY_ACCOUNT_DELETE_EMAIL = bool(
        int(os.getenv("YUTIFY_ACCOUNT_DELETE_EMAIL", True))
    )

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "lax"
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

    # Only set these config variables if custom captcha solution used
    # for example, hCaptcha, otherwise Flask-WTF's defualt config will be used,
    # which is default to reCaptcha (google, ig) ~
    ENABLE_CAPTCHA = bool(int(os.getenv("ENABLE_CAPTCHA", False)))
    if ENABLE_CAPTCHA and bool(int(os.getenv("CUSTOM_CAPTCHA", False))):
        # Flask-WTF Recaptcha configs
        RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY")
        RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY")
        RECAPTCHA_DATA_ATTRS = {"theme": "dark"}
        RECAPTCHA_SCRIPT = os.getenv("RECAPTCHA_SCRIPT")
        RECAPTCHA_DIV_CLASS = os.getenv("RECAPTCHA_DIV_CLASS")
        RECAPTCHA_VERIFY_SERVER = os.getenv("RECAPTCHA_VERIFY_SERVER")

    # Flask-Security specific (and not specific as well) configs ~
    # https://flask-security.readthedocs.io/en/stable/configuration.html
    # ### Core ###
    SECRET_KEY = os.getenv("SECRET_KEY")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
    SECURITY_EMAIL_VALIDATOR_ARGS = {
        "check_deliverability": bool(int(os.getenv("CHECK_EMAIL_DELIVERABILITY", True)))
    }
    SECURITY_EMAIL_SENDER = f"no-reply@{HOST_URL}"
    SECURITY_USER_IDENTITY_ATTRIBUTES = [
        {"username": {"mapper": uia_username_mapper, "case_insensitive": True}},
    ]
    SECURITY_RETURN_GENERIC_RESPONSES = bool(
        int(os.getenv("RETURN_GENERIC_RESPONSES", True))
    )

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
    SECURITY_EMAIL_SUBJECT_REGISTER = (
        f"[{SERVICE}] Verify Email Address!"
        if bool(int(os.getenv("SECURITY_CONFIRMABLE", True)))
        else f"[{SERVICE}] Welcome!"
    )
    SECURITY_POST_REGISTER_VIEW = "auth.login"
    SECURITY_REGISTER_URL = "/signup"
    SECURITY_USERNAME_ENABLE = True
    SECURITY_MSG_USERNAME_DISALLOWED_CHARACTERS = (
        "Username can contain only letters, numbers and hyphen (-)",
        "error",
    )
    SECURITY_USERNAME_REQUIRED = True
    SECURITY_USE_REGISTER_V2 = True
    SECURITY_MSG_CONFIRM_REGISTRATION = (
        "✨ Almost there! Please check your email to confirm your account! (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
        "info",
    )

    # ### Confirmable ###
    SECURITY_CONFIRMABLE = bool(int(os.getenv("SECURITY_CONFIRMABLE", True)))
    SECURITY_CONFIRM_URL = "/verify-email"
    SECURITY_EMAIL_SUBJECT_CONFIRM = f"[{SERVICE}] Verify Email Address!"
    SECURITY_POST_CONFIRM_VIEW = "security.login"
    SECURITY_MSG_EMAIL_CONFIRMED = (
        "Thank you for verifying your email! You're all set, now login with your credentials!",
        "success",
    )

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
    SECURITY_TWO_FACTOR_RESCUE_MAIL = ADMIN_EMAIL
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

    # ######################
    OAUTH2_TOKEN_EXPIRES_IN = {"authorization_code": 3600}
    OAUTH2_REFRESH_TOKEN_GENERATOR = True
