import os

from dotenv import load_dotenv
from flask_security import LoginForm, RegisterFormV2
from flask_wtf import RecaptchaField
from wtforms import BooleanField, StringField
from wtforms.validators import DataRequired

load_dotenv()
ENABLE_CAPTCHA = bool(int(os.getenv("ENABLE_CAPTCHA", False)))


class RegistrationForm(RegisterFormV2):
    name = StringField("Name", validators=[DataRequired()])
    agreement = BooleanField("Agreement", validators=[DataRequired()])
    if ENABLE_CAPTCHA:
        recaptcha = RecaptchaField()


class MyLoginForm(LoginForm):
    if ENABLE_CAPTCHA:
        recaptcha = RecaptchaField()
