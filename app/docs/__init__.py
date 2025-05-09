from flask import Blueprint

bp = Blueprint("docs", __name__)

from app.docs import routes
