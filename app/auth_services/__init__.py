from flask import Blueprint

bp = Blueprint("auth_services", __name__)

from app.auth_services import routes
