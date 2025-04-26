import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    artist = SearchField("Artist Name", validators=[DataRequired()])
    song = SearchField("Song Name", validators=[DataRequired()])
    search = SubmitField("Search")
