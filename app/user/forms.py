from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
    HiddenField,
    BooleanField,
)
from wtforms.validators import DataRequired, Length


class DeleteAccountForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Delete Account")


class EmptyForm(FlaskForm):
    form_name = HiddenField()


class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=128)])
    submit = SubmitField("Save Profile")


class LastfmLinkForm(FlaskForm):
    lastfm_username = StringField("Last.fm Username", validators=[DataRequired()])
    submit = SubmitField("Link")


class ListenBrainzLinkForm(FlaskForm):
    listenbrainz_username = StringField("ListenBrainz Username", validators=[DataRequired()])
    submit = SubmitField("Link")


class RevokeAppForm(FlaskForm):
    submit = SubmitField("Revoke")


class ProfileVisibilityForm(FlaskForm):
    is_profile_public = BooleanField("Profile Public")
    submit = SubmitField("Save")
