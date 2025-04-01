import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SearchField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from zxcvbn import zxcvbn

from app import db
from app.models import User


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        email_hash = User.hash_email(email.data)
        user = db.session.scalar(sa.select(User).where(User._email_hash == email_hash))
        if user is not None:
            raise ValidationError("Please use a different email address.")

    def validate_password(self, password):
        results = zxcvbn(
            password.data, user_inputs=[self.username.data, self.email.data]
        )
        score = results["score"]
        feedback = (
            results["feedback"]["suggestions"][0]
            or "" + " " + results["feedback"]["warning"]
        )

        if score < 3:
            raise ValidationError(feedback)


class SearchForm(FlaskForm):
    artist = SearchField("Artist Name", validators=[DataRequired()])
    song = SearchField("Song Name", validators=[DataRequired()])
    search = SubmitField("Search")


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


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")
