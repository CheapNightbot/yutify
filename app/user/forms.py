import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from app import db
from app.models import User


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Save Profile")


class EditAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Save Account Details")

    def __init__(self, original_username, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(
                sa.select(User).where(User.username == username.data)
            )
            if user is not None:
                raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        if email.data != self.original_email:
            email_hash = User.hash_email(email.data)
            user = db.session.scalar(
                sa.select(User).where(User._email_hash == email_hash)
            )
            if user is not None:
                raise ValidationError("Please use a different email address.")

    def validate_password(self, password):
        user = db.session.scalar(
            sa.select(User).where(User.username == self.original_username)
        )

        if not user.check_password(password.data):
            raise ValidationError("Incorrect password.")
