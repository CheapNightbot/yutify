from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length


class RedirectURIForm(FlaskForm):
    class Meta:
        csrf = False

    redirect_uri = URLField(
        "Redirect URI",
        validators=[DataRequired()],
        render_kw={"placeholder": "https://example.com/callback"},
    )


class CreateClientForm(FlaskForm):
    client_name = StringField(
        "App name",
        name="client_name",
        validators=[DataRequired(), Length(min=3, max=32)],
    )
    client_description = StringField(
        "App description", name="client_description", validators=[DataRequired()]
    )
    client_uri = URLField("Website", name="client_uri")
    redirect_uris = FieldList(
        FormField(RedirectURIForm),
        "Redirect URIs",
        min_entries=1,
        validators=[DataRequired()],
    )
    submit = SubmitField("Save")


class DeleteClientForm(FlaskForm):
    delete = SubmitField("Delete")


class EditClientForm(FlaskForm):
    edit = SubmitField("Edit")
