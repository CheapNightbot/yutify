from flask_security import RegisterFormV2
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class RegistrationForm(RegisterFormV2):
    name = StringField("Name", validators=[DataRequired()])
    agreement = BooleanField("Agreement", validators=[DataRequired()])
