from flask import Blueprint

bp = Blueprint("oauth", __name__)

from app.oauth import routes
