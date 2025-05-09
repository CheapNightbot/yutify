import unicodedata

from flask_security import UsernameUtil
from flask_security.utils import config_value as cv
from flask_security.utils import get_message


class MyUsernameUtil(UsernameUtil):
    def __init__(self, app):
        super().__init__(app)

    def check_username(self, username: str) -> str | None:
        """
        Given a username - check for allowable character categories.

        Allow letters, numbers, hyphens and underscores (using unicodedata.category).

        Returns None if allowed, error message if not allowed.
        """
        cats = [
            (
                unicodedata.category(c)
                if unicodedata.category(c).startswith("P")
                else unicodedata.category(c)[0]
            )
            for c in username
        ]
        if any([cat not in ["L", "N", "Pd", "Pc"] for cat in cats]):
            return get_message("USERNAME_DISALLOWED_CHARACTERS")[0]
        return None

    def normalize(self, username: str) -> str:
        """
        Given an input username - return a clean (using bleach) and normalized
        (using Python's unicodedata.normalize()) version.
        Must be called in app context and uses
        :py:data:`SECURITY_USERNAME_NORMALIZE_FORM` config variable.
        """
        import bleach

        if not username:
            return ""

        username = bleach.clean(username.strip(), strip=True)
        if not username:
            return ""
        cf = cv("USERNAME_NORMALIZE_FORM")
        if cf:
            return unicodedata.normalize(cf, username.lower())
        return username.lower()
