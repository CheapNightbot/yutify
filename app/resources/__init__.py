from flask import Blueprint
from flask_restful import Api

from app.resources.search import YutifySearch
from app.resources.activity import UserActivityResource
from app.extensions import csrf

bp = Blueprint("api", __name__)
api = Api(bp)
csrf.exempt(bp)

api.add_resource(YutifySearch, "/search/<path:artist>:<path:song>")
api.add_resource(UserActivityResource, "/me", "/activity.svg")
