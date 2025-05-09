import sqlalchemy as sa
from flask_security import RegisterFormV2

from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app import db
from app.models import User



class RegistrationForm(RegisterFormV2):
    name = StringField("Name", validators=[DataRequired()])


# class ResetPasswordRequestForm(FlaskForm):
#     email = StringField("Email", validators=[DataRequired(), Email()])
#     submit = SubmitField("Request Password Reset")


# class ResetPasswordForm(FlaskForm):
#     password = PasswordField("New Password", validators=[DataRequired()])
#     password2 = PasswordField(
#         "Confirm Password", validators=[DataRequired(), EqualTo("password")]
#     )
#     submit = SubmitField("Reset Password")
