from flask_security import RegisterFormV2
from wtforms import StringField
from wtforms.validators import DataRequired


class RegistrationForm(RegisterFormV2):
    name = StringField("Name", validators=[DataRequired()])
