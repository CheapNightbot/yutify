from flask import Blueprint
from flask_restful import Api

from app.resources.search import YutifySearch
from app.resources.user_activity import UserActivityResource

bp = Blueprint("api", __name__)
api = Api(bp)
api.catch_all_404s = True

api.add_resource(YutifySearch, "/search/<path:artist>:<path:song>")
api.add_resource(UserActivityResource, "/me")
